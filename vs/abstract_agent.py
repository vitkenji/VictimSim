import os
import random
from abc import ABC, abstractmethod
from .constants import VS

class AbstAgent(ABC):
    AC_INCR = {
        0: (0, -1),  #  u: Up
        1: (1, -1),  # ur: Upper right diagonal
        2: (1, 0),   #  r: Right
        3: (1, 1),   # dr: Down right diagonal
        4: (0, 1),   #  d: Down
        5: (-1, 1),  # dl: Down left diagonal
        6: (-1, 0),  #  l: Left
        7: (-1, -1)  # ul: Up left diagonal
    }
    
    def __init__(self, env, config_file):
        self.NAME = ""             
        self.TLIM = 0.0             # public: time limit to execute (cannot be exceeded)
        self.COST_LINE = 0.0        
        self.COST_DIAG = 0.0        
        self.COST_READ = 0.0       
        self.COST_FIRST_AID = 0.0  
        self.COLOR = (100,100,100)  
        self.TRACE_COLOR = (140,140,140)
               
        self.__env = env           
        self.__body = None        
        self.config_folder = os.path.dirname(config_file) 

        with open(config_file, "r") as file:

            for line in file:
                
                words = line.split()

                keyword = words[0]
                if keyword=="NAME":
                    self.NAME = words[1]
                elif keyword=="COLOR":
                    r = int(words[1].strip('(), '))
                    g = int(words[2].strip('(), '))
                    b = int(words[3].strip('(), '))
                    self.COLOR=(r,g,b)
                elif keyword=="TRACE_COLOR":
                    r = int(words[1].strip('(), '))
                    g = int(words[2].strip('(), '))
                    b = int(words[3].strip('(), '))
                    self.TRACE_COLOR=(r,g,b)
                elif keyword=="TLIM":
                    self.TLIM = float(words[1])
                elif keyword=="COST_LINE":
                    self.COST_LINE = float(words[1])
                elif keyword=="COST_DIAG":
                    self.COST_DIAG = float(words[1])
                elif keyword=="COST_FIRST_AID":
                    self.COST_FIRST_AID = float(words[1])
                elif keyword=="COST_READ":    
                    self.COST_READ = float(words[1])
                    
        self.__body = env.add_agent(self)
        

    @abstractmethod
    def deliberate(self) -> bool:
        pass

    def get_rtime(self):
        return self.__body._rtime
   
    def get_state(self):
        return self.__body._state

    def set_state(self, value):
        self.__body._state  = value

    def get_env(self):
        return self.__env
        
    def walk(self, dx, dy):
        return self.__body._walk(dx, dy)

    def check_walls_and_lim(self):
        return self.__body._check_walls_and_lim()


    def check_for_victim(self):
        return self.__body._check_for_victim()

    def read_vital_signals(self):
        return self.__body._read_vital_signals()

    def first_aid(self):
        return self.__body._first_aid()


