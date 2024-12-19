from enum import Enum

class Movement(Enum):
    U = (0, -1)
    UR = (1, -1)
    R = (1, 0)
    DR = (1, 1)
    D = (0, 1)
    DL = (-1, 1)
    L = (-1, 0)
    UL = (-1, -1)
    STOP = (0, 0)