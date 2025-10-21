import sys
import os
import random
import math
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map
from a_star import a_star, a_star_plan_cost
import time

class Explorer(AbstAgent):
    MAX_DIFFICULTY = 1     
    
    def __init__(self, env, config_file, resc, direction):

        super().__init__(env, config_file)
        self.walk_time = 0         # time consumed to walk when exploring (to decide when to come back)
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.come_back_plan = []
        self.time_come_back = 0
        self.favorite_direction = direction
        self.backtrack_stack = []
        self.backtrack_path = []
        self.map = Map()
        self.known_cells = {(0,0) : {"visited": True}}
        self.map_keys = self.map.data.keys()  
        self.returning = 0         # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals

        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())

    def directions(self):
        obstacles = self.check_walls_and_lim()
        obstacles = obstacles[self.favorite_direction:] + obstacles[:self.favorite_direction]
        
        possible_directions = list(Explorer.AC_INCR.values())
        possible_directions = possible_directions[self.favorite_direction:] + possible_directions[:self.favorite_direction]
        
        for i, direction in enumerate(possible_directions[:]):
            neighbour = (self.x + direction[0], self.y + direction[1])
            if obstacles[i] != VS.CLEAR:
                possible_directions.remove(direction)
            else:
                if neighbour not in self.known_cells:
                    self.known_cells[neighbour] = {"visited": False}
                
                if self.known_cells[neighbour]["visited"]:
                    possible_directions.remove(direction)


        if len(possible_directions) <= 0:
            return (0,0)

        return possible_directions[0]
            
    def verify_adjacents(self, position):
        x, y = position
        possible_directions = list(Explorer.AC_INCR.values())
        possible_directions = possible_directions[self.favorite_direction:] + possible_directions[:self.favorite_direction]

        for c in range(0, 8):
            direction = Explorer.AC_INCR[c]
            neighbour = (x + direction[0], y + direction[1])  
            if neighbour not in self.known_cells:
                continue                
            if not self.known_cells[neighbour]["visited"]:
                return neighbour                
        return None

    def backtrack(self):
        visited_keys = [key for key in self.known_cells if self.known_cells[key].get("visited", True)]
        while len(self.backtrack_stack) > 0:
            goal = self.verify_adjacents(self.backtrack_stack.pop())
            if goal != None:
                visited_keys.append(goal)
                return a_star(visited_keys, (self.x, self.y), goal)[1:]
        return []

    def explore(self):   
        dx, dy = self.directions()
        
        if len(self.backtrack_path) > 0:
            x1, y1 = self.backtrack_path.pop(0)
            dx = x1 - self.x
            dy = y1 - self.y

        else:
            dx, dy = self.directions()
            if dx == 0 and dy == 0:
                self.backtrack_path = self.backtrack()
                x1, y1 = self.backtrack_path.pop(0)
                dx = x1 - self.x
                dy = y1 - self.y


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

            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy

            if (self.x, self.y) not in self.known_cells:
                self.known_cells[(self.x, self.y)] = {"visited": False}
            
            if not self.known_cells[(self.x, self.y)]["visited"]:
                self.known_cells[(self.x, self.y)] = {"visited": True}
                self.backtrack_stack.append((self.x, self.y))

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

            if self.get_rtime() <= self.walk_time/2:
                self.come_back_plan = a_star(self.map_keys,(self.x, self.y),(0,0)) 
                self.time_come_back = a_star_plan_cost(self.come_back_plan)

        return

    def come_back(self):
        x1,y1 = self.come_back_plan.pop(0) 
        dx = x1 - self.x
        dy = y1 - self.y

        result = self.walk(dx, dy)
        if result == VS.BUMPED:
            print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
            return
        
        if result == VS.EXECUTED:
            self.x += dx
            self.y += dy
            #print(f"{self.NAME}: coming back at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
        
    def deliberate(self) -> bool:
        # keeps exploring while there is enough time
        if self.get_rtime() >= self.time_come_back * 1.6:
            self.explore()
            return True

        # no more come back walk actions to execute or already at base
        if self.x == 0 and self.y == 0:
            # time to pass the map and found victims to the master rescuer
            self.resc.sync_explorers(self.map, self.victims)
            # finishes the execution of this agent
            return False

        if not self.returning:
            self.come_back_plan = self.come_back_plan[1:]
            self.returning = 1
        
        self.come_back()
        return True