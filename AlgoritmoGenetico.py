import math
import random

import Dijkstra

from vs.constants import VS
from ComplementoAlgoritmoGenetico import *

'''
 ->Gerar população
 ->Ajustar o algoritmo e as estruturas de dados
 ->Testar
 ->Ajustar
 ->Alegrilsson
'''
TAMANHO_POPULACAO = 100
NUM_GERACOES = 15000

#Implantar e realizar os testes

def algoritmo_genetico(mapa, vitimas, custo_lateral, custo_diagonal, bateria_maxima):
    if(len(vitimas) == 0):
        return []

    maior_pontuacao = 0.0
    custos_preprocessados = Dijkstra.calcular_caminhos_e_custos(mapa, vitimas, custo_lateral, custo_diagonal)
    populacao = gera_populacao(vitimas, TAMANHO_POPULACAO)
    for individuo in populacao: individuo[1] = calcular_custo(individuo[0], custos_preprocessados)
    torna_custo_valido_pop(populacao, custos_preprocessados, bateria_maxima)
    for individuo in populacao: individuo[2] = calcular_fitness(individuo[0])
    for geracao in range(NUM_GERACOES):
        print(geracao)
        filhos = reproducao(populacao, vitimas)
        mutacao_populacao(filhos, vitimas)
        for filho in filhos: filho[1] = calcular_custo(filho[0], custos_preprocessados)
        torna_custo_valido_pop(filhos, custos_preprocessados, bateria_maxima)
        for filho in filhos: filho[1] = calcular_custo(filho[0], custos_preprocessados)
        for filho in filhos: filho[2] = calcular_fitness(filho[0])
        populacao.extend(filhos)
        populacao = sorted(populacao, key=lambda x: x[2], reverse=True)[0:100]
        if (populacao[0][2] > maior_pontuacao):
            maior_pontuacao = populacao[0][2]
    etapas = populacao[0][0]
    caminho = []
    if(len(etapas) > 0):
        caminho.append((0, 0))
        for i in range(len(etapas)-1):
            start = (etapas[i][1], etapas[i][2])
            end = (etapas[i+1][1], etapas[i+1][2])
            caminho.extend(custos_preprocessados[start, end][0][1:])
    return etapas, caminho

# Gerar população
def gera_populacao(vitimas, tamanhoPopulacao):
    populacao = []
    for _ in range(tamanhoPopulacao):
        cromossomo = [(0, 0, 0, 0, -1)]
        tamanho_cromossomo = random.randint(1, len(vitimas))
        vitimas_geracao = set(vitimas)
        for _ in range(tamanho_cromossomo):
            gene = random.choice(list(vitimas_geracao))
            vitimas_geracao.remove(gene)
            cromossomo.append(gene)
        cromossomo.append((0, 0, 0, 0, -2))
        populacao.append([cromossomo, 0, 0])
    return populacao

# Ajustar o fitness para o somatório de pontos de acordo com os critérios.
def calcular_fitness(cromossomo):
    fitness = 0.0
    for gene in cromossomo:
        fitness += gene[3]
    return fitness

# Roleta
def selecao_por_roleta(populacao):
    if not populacao:
        return None
    total = sum(individuo[2] for individuo in populacao)
    resultado = random.uniform(0, total)
    somatorio = 0
    for individuo in populacao:
        somatorio += individuo[2]
        if somatorio >= resultado:
            return individuo
    return populacao[-1]

# Reprodução
def reproducao(populacao, vitimas):
    filhos = []
    for _ in range(math.ceil(len(populacao)/2)):
        pai1 = selecao_por_roleta(populacao)
        pai2 = selecao_por_roleta(populacao)
        filho1, filho2 = crossover(pai1, pai2, vitimas)
        filhos.append([filho1, 0, 0])
        filhos.append([filho2, 0, 0])
    return filhos

# Função de crossover
def crossover(pai1, pai2, vitimas):
    num_vitimas = len(vitimas)

    interior1 = pai1[0][1:-1]
    interior2 = pai2[0][1:-1]

    filho1 = [pai1[0][0]]
    filho2 = [pai2[0][0]]

    usado_filho1 = set(filho1)
    usado_filho2 = set(filho2)

    min_len = min(len(interior1), len(interior2))

    for i in range(min_len):
        if random.random() < 0.5:
            if interior2[i] not in usado_filho1:
                filho1.append(interior2[i])
                usado_filho1.add(interior2[i])
            if interior1[i] not in usado_filho2:
                filho2.append(interior1[i])
                usado_filho2.add(interior1[i])
        else:
            if interior1[i] not in usado_filho1:
                filho1.append(interior1[i])
                usado_filho1.add(interior1[i])
            if interior2[i] not in usado_filho2:
                filho2.append(interior2[i])
                usado_filho2.add(interior2[i])

    for i in range(min_len, len(interior2)):
        if len(filho1) < num_vitimas + 1 and interior2[i] not in usado_filho1:
            filho1.append(interior2[i])
            usado_filho1.add(interior2[i])

    for i in range(min_len, len(interior1)):
        if len(filho2) < num_vitimas + 1 and interior1[i] not in usado_filho2:
            filho2.append(interior1[i])
            usado_filho2.add(interior1[i])

    filho1.append((0, 0, 0, 0, -2))
    filho2.append((0, 0, 0, 0, -2))

    return filho1, filho2

# Mutacao populacao
def mutacao_populacao(populacao, vitimas):
    for individuo in populacao:
        mutacao(individuo[0], vitimas)

# Função de mutação
def mutacao(cromossomo, vitimas):
    sorteio = random.random()
    if(sorteio > 0.95): #0.95
        adiciona_gene(cromossomo, vitimas)
    if(sorteio > 0.8): #0.8
        troca_posicoes(cromossomo)

def torna_custo_valido_pop(populacao, custos_preprocessados, bateria_maxima):
    for individuo in populacao:
        torna_custo_valido(individuo, custos_preprocessados, bateria_maxima)

# Testa Cromossomo
def torna_custo_valido(cromossomo, custos_preprocessados, bateria_maxima):
    if cromossomo[1] > bateria_maxima: #Verificar depois da remocao repeticoes
        diminuir_custo(cromossomo[0], custos_preprocessados, bateria_maxima)







