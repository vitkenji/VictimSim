from vs.constants import VS

class Map:
    def __init__(self):
        self.data = {}

    
    def in_map(self, coord):
        if coord in self.data:
            return True

        return False        
                
    def get(self, coord):
        return self.data.get(coord)

    def get_difficulty(self, coord):
        return self.data.get(coord)[0]

    def get_vic_id(self, coord):
        return self.data.get(coord)[1]

    def get_actions_results(self, coord):
        return self.data.get(coord)[2]

    def add(self, coord, difficulty, vic_id, actions_res):
        self.data[coord] = (difficulty, vic_id, actions_res)

    def update(self, another_map):
        self.data.update(another_map.data)

    def draw(self):
        if not self.data:
            print("Map is empty.")
            return

        min_x = min(key[0] for key in self.data.keys())
        max_x = max(key[0] for key in self.data.keys())
        min_y = min(key[1] for key in self.data.keys())
        max_y = max(key[1] for key in self.data.keys())

        for y in range(min_y, max_y + 1):
            row = ""
            for x in range(min_x, max_x + 1):
                item = self.get((x, y))
                if item:
                    if item[1] == VS.NO_VICTIM:
                        row += f"[{item[0]:7.2f}  no] "
                    else:
                        row += f"[{item[0]:7.2f} {item[1]:3d}] "
                else:
                    row += f"[     ?     ] "
            print(row)


    
