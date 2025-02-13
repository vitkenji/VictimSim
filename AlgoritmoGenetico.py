import Dijkstra
import enum
import random

class EC (enum):
    VALIDO = 1
    REPETICAO = 2
    CUSTO_INVALIDO = 3


# Ajustar o fitness para o somatório de pontos de acordo com os critérios.
def calcular_fitness(cromossomo, custos_preprocessados, vítimas):
    pontos = 0
    for i in range(len(cromossomo) - 1):
        if mapa[cromossomo[i]][1] != VS.NO_VICTIM:  # Verifica se há uma vítima
            pontos += 1
    return pontos

#Testa Cromossomo
def cromossomo_valido(cromossomo, custos_preprocessados, bateria_maxima):
    # Verifica repetição de vértices
    if len(cromossomo) != len(set(cromossomo)):
        return EC.REPETICAO
    # Verifica bateria
    custo_total = 0
    for i in range(len(cromossomo) - 1):
        custo_total += custos_preprocessados[(cromossomo[i], cromossomo[i+1])][1]
    if custo_total <= bateria_maxima :
        return EC.VALIDO
    else:
        return EC.CUSTO_INVALIDO

#Recuperacao do Indivíduo
def recuperacao(cromossomo, motivo, vitimas){

}
    
# Função de mutação Ajustar
def mutacao(cromossomo, custos_preprocessados):
    while not cromossomo_valido(cromossomo, custos_preprocessados):
        # Remove vértices aleatoriamente
        if len(cromossomo) > 2:
            cromossomo.pop(random.randint(1, len(cromossomo) - 2))
        else:
            break
    return cromossomo

#Função de crossover
def crossover(pai1, pai2):
    interior1 = pai1[1:-1]
    interior2 = pai2[1:-1]

    filho1 = [pai1[0]]
    filho2 = [pai2[0]]

    min_len = min(len(interior1), len(interior2))

    ultima = 0
    for i in range(min_len):
        if random.random() < 0.5:
            # Troca os genes entre os filhos
            filho1.append(interior2[i])
            filho2.append(interior1[i])
        else:
            # Cada filho recebe o gene do próprio pai
            filho1.append(interior1[i])
            filho2.append(interior2[i])
        ultima = i
    ultima += 1
    # O crossover para quando um 0 é atingido (ou seja, quando o pai mais curto acaba)
    # Se o pai1 for o mais curto:

    if len(interior1) == min_len:
        for i in range(ultima, len(interior2)):
            if random.random() < 0.5:
                filho1.append(interior1[i])
            else:
                filho2.append(interior2[i])
    else:
        for i in range(ultima, len(interior1)):
            if random.random() < 0.5:
                filho1.append(interior1[i])
            else:
                filho2.append(interior2[i])

    filho1.append(0)
    filho2.append(0)

    return filho1, filho2

#algoritmo
def algoritmo_genetico(mapa, vítimas, custos_preprocessados, população_size, gerações):
    população = []
    for _ in range(população_size):
        cromossomo = [random.choice(list(mapa.keys())) for _ in range(random.randint(3, 6))]
        população.append(cromossomo)

    for geração in range(gerações):
        população = sorted(população, key=lambda x: calcular_fitness(x, custos_preprocessados, vítimas), reverse=True)
        nova_população = população[:2]  # Elitismo

        while len(nova_população) < população_size:
            pai1, pai2 = random.choices(população[:10], k=2)
            filho1, filho2 = crossover(pai1, pai2)
            nova_população.append(mutacao(filho1, custos_preprocessados))
            nova_população.append(mutacao(filho2, custos_preprocessados))

        população = nova_população

    return população[0], calcular_fitness(população[0], custos_preprocessados, vítimas)


