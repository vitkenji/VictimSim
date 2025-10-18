import heapq

def a_star(map, start, goal):
    open = []
    closed = []
    g = {}
    g[start] = 0
    f = {}
    f[start] = h(start, goal)
    
    heapq.heappush(open, (f[start], start))

    path = {}

    while len(open) > 0:
        f_current, current = heapq.heappop(open)
        
        if current == goal:
            return build_path(path, current)

        closed.append(current)
        
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

    return {}

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

