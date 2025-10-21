import heapq
from functools import lru_cache

def a_star(map, start, goal):
    open_heap = []
    open_set = {start}
    closed = set()
    g = {start: 0}
    f = {start: h(start, goal)}
    heapq.heappush(open_heap, (f[start], start))
    path = {}

    while open_heap:
        f_current, current = heapq.heappop(open_heap)
        
        if current in closed:
            continue

        if current == goal:
            return build_path(path, current)

        closed.add(current)
        open_set.discard(current)
        
        for neighbour in neighbours(current, map):
            if neighbour in closed:
                continue
            
            g_ = g[current] + distance(current, neighbour)

            if neighbour not in g or g_ < g[neighbour]:
                g[neighbour] = g_
                f[neighbour] = g[neighbour] + h(neighbour, goal)
                path[neighbour] = current

                if neighbour not in open_set:
                    heapq.heappush(open_heap, (f[neighbour], neighbour))
                    open_set.add(neighbour)    
    return ()

@lru_cache(maxsize=None)
def h(s1, s2):
    return abs(s1[0] - s2[0]) + abs(s1[1] - s2[1])

def neighbours(s, map):
    x, y = s
    adjacent = [(x-1, y-1), (x-1, y), (x-1, y+1), (x, y-1),(x, y+1),(x+1, y-1), (x+1, y), (x+1, y+1)]
    return [cell for cell in adjacent if cell in map]

@lru_cache(maxsize=8)
def distance(s1, s2):
    return 1 if (s1[0] == s2[0] or s1[1] == s2[1]) else 1.5

def build_path(path, current):
    path_ = [current]
    while current in path:
        current = path[current]
        path_.insert(0, current)
    return path_

def a_star_plan_cost(plan):
    cost = 0
    last_coord = plan[0]

    for coord in plan[1:]:
        x1,y1 = last_coord
        x2, y2 = coord
        if (x1 == x2) or (y1 == y2):
            cost += 1
        else:
            cost += 1.5
        last_coord = coord 
    return cost