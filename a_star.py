import heapq
from functools import lru_cache

def a_star_2(map, start, goal):
    return list(a_star_cached(tuple(map), start, goal))

def a_star(map, start, goal):
    open = []
    closed = set()
    g = {start: 0}
    f = {start: h(start, goal)}
    
    heapq.heappush(open, (f[start], start))

    path = {}

    while len(open) > 0:
        f_current, current = heapq.heappop(open)
        
        if current == goal:
            return build_path(path, current)

        closed.add(current)
        
        neighbourhood = neighbours(current, map)
        for neighbour in neighbourhood:
            if neighbour in closed:
                continue
            
            g_ = g[current] + distance(current, neighbour)

            if neighbour not in g:
                g[neighbour] = g_
                f[neighbour] = g[neighbour] + h(neighbour, goal)
                path[neighbour] = current
                heapq.heappush(open, (f[neighbour], neighbour))

            elif g_ <= g[neighbour]:
                g[neighbour] = g_
                f[neighbour] = g[neighbour] + h(neighbour, goal)
                path[neighbour] = current
                heapq.heappush(open, (f[neighbour], neighbour))

    return ()

@lru_cache(maxsize=None)
def h(s1, s2):
    return abs(s1[0] - s2[0]) + abs(s1[1] - s2[1])

def neighbours(s, map):
    neighbourhood = []
    x1, y1 = s
    for cell in map:
        x2, y2 = cell
        if x2 >= x1 - 1 and x2 <= x1 + 1:
            if y2 >= y1 - 1 and y2 <= y1 + 1:
                if cell != s:
                    neighbourhood.append(cell)
    return neighbourhood

def distance(s1, s2):
    x1, y1 = s1
    x2, y2 = s2
    if x1 == x2 or y1 == y2:
        return 1
    return 1.5

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

if __name__ == "__main__":

    # Mapa 1: Grid 3x3 simples - todos os nós conectados
    map1 = [
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2),
        (2, 0), (2, 1), (2, 2)
    ]
    
    # Mapa 2: Grid 5x5 - teste maior
    map2 = [
        (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
        (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
        (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
        (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
        (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)
    ]
    
    # Mapa 3: Grid com "obstáculos" (células faltando)
    map3 = [
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0),         (1, 2), (1, 3),  # (1,1) é obstáculo
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1),         (3, 3)   # (3,2) é obstáculo
    ]
    
    print("=== Testando com Mapa 1 (3x3) ===")
    print("Start: (0,0), Goal: (2,2)")
    result = a_star(map1, (0, 0), (2, 2))
    print(f"Resultado: {result} com custo {a_star_plan_cost(result)}\n")
    
    print("=== Testando com Mapa 2 (5x5) ===")
    print("Start: (0,0), Goal: (4,4)")
    result2 = a_star(map2, (0, 0), (4, 4))
    print(f"Resultado: {result2} com custo {a_star_plan_cost(result2)}\n")

    print("=== Testando com Mapa 3 (com obstáculos) ===")
    print("Start: (0,0), Goal: (3,3)")
    result3 = a_star(map3, (0, 0), (3, 3))
    print(f"Resultado: {result3} com custo {a_star_plan_cost(result3)}\n")

