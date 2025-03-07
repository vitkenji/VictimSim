import heapq

from map import Map
from vs.EnumMovimentacao import Movement
from vs.constants import VS

def dijkstra(map, start, custo_lateral, custo_diagonal):
    # Inicializa as distâncias com infinito
    custos = {node: float('inf') for node in map.data.keys()}
    previous_nodes = {node: None for node in map.data.keys()}  # Para reconstruir o caminho depois
    custos[start] = 0

    # Min-Heap (fila de prioridade)
    pq = [(0, start)]  # (custo, nó)

    while pq:
        custo_atual, current_node = heapq.heappop(pq)

        # Se já encontrou um caminho melhor antes, ignora
        if custo_atual > custos[current_node]:
            continue

        # Explora vizinhos
        vizinhos = posicoes_vizinhas(current_node, map, custo_lateral, custo_diagonal)
        for vizinho in vizinhos:
            custo = custo_atual + map.get_difficulty(vizinho[0]) + vizinho[1]

            # Se encontrou um caminho melhor, atualiza
            if custo < custos[vizinho[0]]:
                custos[vizinho[0]] = custo
                previous_nodes[vizinho[0]] = current_node
                heapq.heappush(pq, (custo, vizinho[0]))

    return custos, previous_nodes

def posicoes_vizinhas(posicaoVisitada, map, custo_lateral, custo_diagonal ):
    vizinhos = set()

    for move in (Movement.U, Movement.D, Movement.R, Movement.L):
        vizinho = (posicaoVisitada[0]+ move.value[0], posicaoVisitada[1] + move.value[1])
        if map.in_map(vizinho):
            vizinhos.add((vizinho, custo_lateral))

    for move in (Movement.UL, Movement.UR, Movement.DL, Movement.DR):
        vizinho = (posicaoVisitada[0]+ move.value[0], posicaoVisitada[1] + move.value[1])
        if map.in_map(vizinho):
            vizinhos.add((vizinho, custo_diagonal))
    return vizinhos

# Função para reconstruir o caminho
def reconstruir_caminho(previous_nodes, start, end):
    caminho = []
    current_node = end
    while current_node != start:
        caminho.append(current_node)
        current_node = previous_nodes[current_node]
    caminho.append(start)
    caminho.reverse()
    return caminho

def calcular_caminhos_e_custos(map, victims, custo_lateral, custo_diagonal):
    caminhos = dict()
    start_coords = victims.copy()
    start_coords.insert(0, (0, 0, 0, 0.0, 1))
    for start in start_coords:
        start_coord = (start[1], start[2])
        custos, previous_nodes = dijkstra(map, start_coord, custo_lateral, custo_diagonal)
        end_coords = [v for v in start_coords if v != start]
        for end in end_coords:
            end_coord = (end[1], end[2])
            caminhos[(start_coord, end_coord)] = (reconstruir_caminho(previous_nodes, start_coord, end_coord), custos[end_coord])
        caminhos[(start_coord, start_coord)] = ((), 0)
    return caminhos