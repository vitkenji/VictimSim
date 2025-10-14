import sys
import os
import pygame
import random
import csv
import time
from .constants import VS

class PhysAgent:
    def __init__(self, mind, env, x_base, y_base, state=VS.ACTIVE):
        self.mind = mind              
        self.env = env              
        self.x_base = x_base         
        self.y_base = y_base        
        self.x = x_base             
        self.y = y_base              
        self._rtime = mind.TLIM       
        self._state = state
       
    def _end_of_time(self):
        if self._rtime < 0.0:
           return True
        return False

    def _at_base(self):   
        if self.x == self.env.dic["BASE"][0] and self.y == self.env.dic["BASE"][1]:
           return True
        return False

    def _walk(self, dx, dy):
        if dx != 0 and dy != 0:   
            base = self.mind.COST_DIAG 
        else:                  
            base = self.mind.COST_LINE
        
        new_x = self.x + dx
        new_y = self.y + dy

        if (new_x >= 0 and new_x < self.env.dic["GRID_WIDTH"]and
            new_y >= 0 and new_y < self.env.dic["GRID_HEIGHT"] and
            self.env.obst[new_x][new_y] != 100):
            self._rtime -= base * self.env.obst[new_x][new_y]
            
            if self._rtime < 0:
                return VS.TIME_EXCEEDED
            else:
                self.x = new_x
                self.y = new_y
                if self not in self.env.visited[new_x][new_y]:
                    self.env.visited[new_x][new_y].append(self)
                return VS.EXECUTED
        else:
            self._rtime -= base
            return VS.BUMPED

    def _check_walls_and_lim(self):
        delta = [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
        obstacles = [VS.CLEAR] * 8
        i = 0

        for d in delta:
            new_x = self.x + d[0]
            new_y = self.y + d[1]

            if new_x < 0 or new_x >= self.env.dic["GRID_WIDTH"] or new_y < 0 or new_y >= self.env.dic["GRID_HEIGHT"]:
                obstacles[i] = VS.END
            elif self.env.obst[new_x][new_y] == 100:
                obstacles[i] = VS.WALL
            i += 1

        return obstacles 

    def _check_for_victim(self):
        vic_id = VS.NO_VICTIM
        if (self.x, self.y) in self.env.victims:
            vic_id = self.env.victims.index((self.x, self.y))
        return vic_id

    def _read_vital_signals(self):
        self._rtime -= self.mind.COST_READ
    
        if self._rtime < 0:
           return VS.TIME_EXCEEDED

        vic_id = self._check_for_victim()
        if vic_id == VS.NO_VICTIM:
            return []
        
        self.env.found[vic_id].append(self)
        return self.env.signals[vic_id][:-2]

    def _first_aid(self):
        self._rtime -= self.mind.COST_FIRST_AID

        if self._rtime < 0:
           return VS.TIME_EXCEEDED

        vic_id = self._check_for_victim()
        if vic_id == VS.NO_VICTIM:
            return False
        
        self.env.saved[vic_id].append(self)
        return True

    def _get_found_victims(self):

        victims = []

        v = 0
        for finders in self.env.found:
            if self in finders:
                victims.append(v)
            v = v + 1
  
        return victims

    def _get_saved_victims(self):
        victims = []
        v = 0
        for rescuers in self.env.saved:
            if self in rescuers:
                victims.append(v)
            v = v + 1
  
        return victims 
                
            
