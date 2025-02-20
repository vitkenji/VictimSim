import random
from logging import exception


class EC :
    VALIDO = 0
    REPETICAO = 1
    CUSTO_INVALIDO = 2

#Calcular Custo
def calcular_custo(caminho, custos_preprocessados):
    custo_total = 0
    for i in range(len(caminho) - 1):
        try:
            start = (caminho[i][1], caminho[i][2])
            end = (caminho[i+1][1], caminho[i+1][2])
        except TypeError:
            a = 10
        custo_total += custos_preprocessados[(start, end)][1]
    return custo_total

#Contar repeticoes
def dicionario_repeticoes(lista):
    dicionario = {}
    for item in lista:
        if(item in dicionario):
            dicionario[item] += 1
        else:
            dicionario[item] = 1
    return dicionario

def diminuir_custo(cromossomo, custos_preprocessados, custo_maximo):

    if(1 != len(cromossomo) - 1):
        index_aleatorio = random.randint(1, len(cromossomo) - 2)
        try:
            cromossomo.pop(index_aleatorio)
        except:
            vagina = 0
        while(calcular_custo(cromossomo, custos_preprocessados) > custo_maximo):
            try:
                index_aleatorio = random.randint(1, len(cromossomo) - 2)
                cromossomo.pop(index_aleatorio)
            except IndexError:
                cu=0
            except ValueError:
                buceta=0
    else:
        cromossomo.pop(1)

def adiciona_gene(cromossomo, vitimas):
    faltantes = set(vitimas) - set(cromossomo)
    if(len(faltantes) > 0):
        item = random.choice(list(faltantes))
        index = random.randint(1, len(cromossomo)-1)
        cromossomo.insert(index, item)

def troca_posicoes(cromossomo):
    if(len(cromossomo) > 3):
        p1 = random.randint(1, len(cromossomo)-2)
        p2 = random.randint(1, len(cromossomo)-2)
        while(p1 == p2):
            p2 = random.randint(1, len(cromossomo) - 2)
        cromossomo[p1], cromossomo[p2] = cromossomo[p2], cromossomo[p1]
