# EXPLORER AGENT
# @Author: Tacla, UTFPR

import sys
import os
import random
import math
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map
import heapq
import time
from collections import deque

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

class Explorer(AbstAgent):
    """ class attribute """
    MAX_DIFFICULTY = 1             # the maximum degree of difficulty to enter into a cell
    
    def __init__(self, env, config_file, resc):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.walk_stack = Stack()  # a stack to store the movements
        self.walk_time = 0         # time consumed to walk when exploring (to decide when to come back)
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.map = Map()           # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals
        self.last_direction = 0
        self.finish = False
        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())

    
    def heuristics(self, x, y):
        return math.sqrt(x**2 + y**2)

    def get_next_position(self):
        
        obstacles = self.check_walls_and_lim()
        valid_directions = []

        for direction in range(8): 
            next_x = self.x + Explorer.AC_INCR[direction][0]
            next_y = self.y + Explorer.AC_INCR[direction][1]
            next_coord = (next_x, next_y)

            if obstacles[direction] == VS.CLEAR and not self.map.in_map(next_coord):
                valid_directions.append(direction)

        if valid_directions:
            self.last_direction = random.choice(valid_directions)
            return Explorer.AC_INCR[self.last_direction]
        
        while True:
            direction = random.randint(0, 7)
            if obstacles[direction] == VS.CLEAR:
                self.last_direction = direction
                return Explorer.AC_INCR[self.last_direction]


    def explore(self):
        # get an random increment for x and y       
        dx, dy = self.get_next_position()

        # Moves the body to another position  
        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()


        # Test the result of the walk action
        # Should never bump, but for safe functionning let's test
        if result == VS.BUMPED:
            # update the map with the wall
            self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())
            #print(f"{self.NAME}: Wall or grid limit reached at ({self.x + dx}, {self.y + dy})")

        if result == VS.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            self.walk_stack.push((dx, dy))

            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy

            # update the walk time
            self.walk_time = self.walk_time + (rtime_bef - rtime_aft)
            #print(f"{self.NAME} walk time: {self.walk_time}")

            # Check for victims
            seq = self.check_for_victim()
            if seq != VS.NO_VICTIM:
                vs = self.read_vital_signals()
                self.victims[vs[0]] = ((self.x, self.y), vs)
                #print(f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
                #print(f"{self.NAME} Seq: {seq} Vital signals: {vs}")
            
            # Calculates the difficulty of the visited cell
            difficulty = (rtime_bef - rtime_aft)
            if dx == 0 or dy == 0:
                difficulty = difficulty / self.COST_LINE
            else:
                difficulty = difficulty / self.COST_DIAG

            # Update the map with the new cell
            self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
            #print(f"{self.NAME}:at ({self.x}, {self.y}), diffic: {difficulty:.2f} vict: {seq} rtime: {self.get_rtime()}")

        return

    def come_back(self):
        print("coming back")
        obstacles = self.check_walls_and_lim()
        
        plan = deque()
        
        priority_queue = []
        heapq.heappush(priority_queue, (self.heuristics(self.x, self.y), 0, (self.x, self.y)))
        visited = set()
        parent_map = { (self.x, self.y): None }
        
        while priority_queue:
            f, g, node = heapq.heappop(priority_queue)
            
            if node == (0, 0):
                current = node
                while current != (self.x, self.y):
                    parent = parent_map[current]
                    plan.appendleft(current)
                    current = parent
                self.finish = True
                break
            
            if node in visited:
                continue
            
            visited.add(node)
            
            for neighbor in range(8):
                next_x = node[0] + Explorer.AC_INCR[neighbor][0]
                next_y = node[1] + Explorer.AC_INCR[neighbor][1]
                next_coord = (next_x, next_y)

                if next_coord not in visited and obstacles[neighbor] == VS.CLEAR:
                    g_node = 1 if neighbor % 2 == 0 else 1.5
                    new_g = g + g_node
                    f_node = new_g + self.heuristics(next_x, next_y)
                    
                    parent_map[next_coord] = node
                    
                    heapq.heappush(priority_queue, (f_node, new_g, next_coord))

        if plan:
            for next_pos in plan:
                dx, dy = next_pos[0] - self.x, next_pos[1] - self.y
                
                result = self.walk(dx, dy)
                
                if result == VS.EXECUTED:
                    self.x += dx
                    self.y += dy
                    print(f"Moving to {next_pos}, rtime: {self.get_rtime()}")
                else:
                    print(f"Failed to move to {next_pos}")
        
        return
            
    

    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        # forth and back: go, read the vital signals and come back to the position

        return_time = 200
        
        # keeps exploring while there is enough time
        if self.get_rtime() > return_time and not self.finish:
            self.explore()
            return True

        # no more come back walk actions to execute or already at base
        if self.walk_stack.is_empty() or (self.x == 0 and self.y == 0):
            # time to pass the map and found victims to the master rescuer
            self.resc.sync_explorers(self.map, self.victims)
            # finishes the execution of this agent
            return False
        
        self.come_back()
            
        return True

