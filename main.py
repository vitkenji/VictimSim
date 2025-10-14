import sys
import os
import time
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer

def main(data_folder_name, config_ag_folder_name):
   
    current_folder = os.path.abspath(os.getcwd())
    config_ag_folder = os.path.abspath(os.path.join(current_folder, config_ag_folder_name))
    data_folder = os.path.abspath(os.path.join(current_folder, data_folder_name))
    
    env = Env(data_folder)
    
    rescuer_file = os.path.join(config_ag_folder, "rescuer_1_config.txt")
    master_rescuer = Rescuer(env, rescuer_file, 4)
    
    for exp in range(1, 5):
        filename = f"explorer_{exp:1d}_config.txt"
        explorer_file = os.path.join(config_ag_folder, filename)
        Explorer(env, explorer_file, master_rescuer)

    env.run()
    
        
if __name__ == '__main__':    
    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        data_folder_name = os.path.join("datasets", "data_300v_90x90")
        config_ag_folder_name = os.path.join("agents_config","cfg_2")
        
    main(data_folder_name, config_ag_folder_name)
