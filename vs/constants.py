class VS:
    
    ENDED = 2   
    ACTIVE = 1  
    IDLE = 0    
    DEAD  = -1  

    BUMPED = -1 
    TIME_EXCEEDED = -2 
    EXECUTED = 1      

    NO_VICTIM = -1

    UNK = -1           
    CLEAR = 0
    WALL = 1
    END = 2

    OBST_WALL = 100 
    OBST_NONE = 1  
    
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    CYAN = (0, 255, 255)
    YELLOW = (255, 255, 0)
    VIC_COLOR_SEV1 = (255,51,51)
    VIC_COLOR_SEV2 = (255,128,0)
    VIC_COLOR_SEV3 = (255,255,51)
    VIC_COLOR_SEV4 = (128,255,0)
    VIC_COLOR_LIST = [VIC_COLOR_SEV1, VIC_COLOR_SEV2, VIC_COLOR_SEV3, VIC_COLOR_SEV4]
    
