import sys
import os
import random
import math
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent, PriorityQueue, Stack
from vs.constants import VS
from map import Map
import heapq
import time
from collections import deque

class Explorer(AbstAgent):
    """ class attribute """
    MAX_DIFFICULTY = 1             # the maximum degree of difficulty to enter into a cell
    
    def __init__(self, env, config_file, resc, direction=0):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.map = Map()           # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals
        self.finish = False
        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())

        self.stack = Stack()
        self.direction = direction
        self.cells_known = {(0,0): {"visited": True, "difficulty" : 1, "cost_to_base": 0}}
    
    def __get_current_pos(self) -> tuple:
        return (self.x, self.y)
    

    def actions(self) -> tuple:
        obstacles = self.check_walls_and_lim()

        possible_actions = []
        
        for i, obstacle in enumerate(obstacles):
            if obstacle == VS.CLEAR:
                action = Explorer.AC_INCR[i]
                possible_actions.append(action)
            else:
                possible_actions.append(None)

        rotate = self.direction
        if rotate != 0:
            possible_actions = possible_actions[rotate:] + possible_actions[:rotate]

        print([i for i in possible_actions if i is not None])
        return [i for i in possible_actions if i is not None]


    def online_dfs(self):
        possible_actions = self.actions()

        current_pos = self.__get_current_pos()

        next_action = None

        for action in possible_actions:

            next_position = (current_pos[0] + action[0], current_pos[1] + action[1])
            
            if next_position not in self.cells_known.keys():
                self.cells_known[next_position] = {"visited": False, "difficulty" : None, "cost_to_base": None}

            if self.cells_known[next_position]["visited"] == False and not next_action:
                next_action = action

        if not next_action:
            return 0,0
        
        return next_action


    def backtracking(self):
        visited_locations = [key for key, value in self.cells_known.items() if value["visited"] == True]

        possible_goals = []
        for pos in visited_locations:
            if len(self.get_adjacents_unvisited(pos)) > 0:
                possible_goals.append(pos)

        min_cost = None
        best_path = None

        index = 0
        loc_range = 10 if len(possible_goals) > 10 else len(possible_goals)

        possible_goals = possible_goals[::-1]

        while not best_path and len(possible_goals) >= index + loc_range:

            for goal in possible_goals[index:index+loc_range]:
                path, cost = self.a_star_search(self.__get_current_pos(), goal)
                if path == [] or cost == -1:
                    pass
                elif min_cost is None or cost < min_cost:
                    min_cost = cost
                    best_path = path

            index += loc_range
            if loc_range + index > len(possible_goals):
                loc_range = len(possible_goals) - index 

        if not best_path:
            return
        
        last_step = best_path[-1]
        for step in reversed(best_path[:-1]):
            delta_step = (step[0]-last_step[0], step[1]-last_step[1])
            self.stack.push(delta_step)
            last_step = step
        self.stack.items.reverse()

    def heuristics(self, x, y):
        return math.sqrt(x**2 + y**2)

    def explore(self):  
        if not self.stack.is_empty():
            dx, dy = self.stack.pop()
        else:
            dx, dy = self.online_dfs()
        
        if dx == dy == 0:
            self.backtracking()
            if not self.stack.is_empty():
                dx, dy = self.stack.pop()
            else:
                dx, dy = 0, 0

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

            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy

            self.cells_known[self.__get_current_pos()]["visited"] = True

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

            self.cells_known[self.__get_current_pos()]["difficulty"] = difficulty

            # Update the map with the new cell
            self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
            #print(f"{self.NAME}:at ({self.x}, {self.y}), diffic: {difficulty:.2f} vict: {seq} rtime: {self.get_rtime()}")

        return

    def come_back(self):
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

        return
            
    def deliberate(self) -> bool:

        return_time = (abs(self.x) + abs(self.y))*6.5
        
        # keeps exploring while there is enough time
        if self.get_rtime() > return_time and not self.finish:
            self.explore()
            return True

        # no more come back walk actions to execute or already at base
        if (self.x == 0 and self.y == 0):
            # time to pass the map and found victims to the master rescuer
            self.resc.sync_explorers(self.map, self.victims)
            # finishes the execution of this agent
            return False

        # print('come back')
        self.come_back()
            
        return True
    
    def cost_plan(self):
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
        cost = 0
        if plan:
            for next_pos in plan:
                cost += 2
            return cost, plan
        else:
            return (abs(self.x) + abs(self.y))*7, None
    
    

