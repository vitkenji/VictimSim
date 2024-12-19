from vs.EnumMovimentacao import Movement

class Node:
    def __init__(self,  posicao=None, custoTerreno=0, custoMovimentacao=float(0), posicaoFinal=None):
        if posicao is None:  # Construtor que cria o nó sem informações completas (caso base)
            self.Heuristica = float('inf')
            self.CustoTerreno = float(0)
            self.CustoMovimentacao = float(0)
            self.Posicao = None
        else:
            self.Posicao = posicao
            self.Heuristica = funcaoHeuristica(posicao, posicaoFinal)
            self.CustoTerreno = custoTerreno
            self.CustoMovimentacao = custoMovimentacao

    def getTotal(self):
        return self.Heuristica + self.CustoTerreno + self.CustoMovimentacao
    def getHeuristicaTotal(self):
        return self.Heuristica + self.CustoTerreno
    def getTotalSemTerreno(self):
        return self.Heuristica + self.CustoMovimentacao
    def setHeuristica(self, novaHeuristica):
        self.Heuristica = novaHeuristica - self.CustoTerreno

def LRTAStar(map, posicaoInicial, posicaoFinal, custoLinha, custoDiagonal, max_iters=100):

    posicoesComNos = dict()
    valor = map.get(posicaoInicial)[0]
    custoTerreno = valor-1 if valor is not None else 0
    noInicio = Node(posicaoInicial, custoTerreno, 0, posicaoFinal)
    iter_count = 0
    noAtual = noInicio
    posicoesComNos[posicaoInicial] = noInicio
    listaCaminho = []
    listaCaminho.append((noAtual.Posicao, noAtual.CustoMovimentacao, noInicio.CustoTerreno,))

    for i in range(0, 3):
        noAtual = noInicio
        listaCaminho = ajustarCaminho(noAtual, listaCaminho)
        while noAtual.Posicao != posicaoFinal and iter_count < max_iters:
            nosVizinhos = posicoesVizinhas(noAtual, posicaoFinal, custoLinha, custoDiagonal, map, posicoesComNos)

            noMenorCusto = Node()
            for vizinho in nosVizinhos:
                if (vizinho.getTotal() < noMenorCusto.getTotal()):
                    noMenorCusto = vizinho

            noAtual.Heuristica = noMenorCusto.getTotalSemTerreno()
            noAtual = noMenorCusto

            ajustarCaminho(noAtual, listaCaminho)

    iter_count += 1
    caminho = calcularCaminho(listaCaminho)
    custo = calcularCustoCaminho(listaCaminho)

    if len(caminho) == 0:
        print("oq")

    if caminho[-1] == posicaoFinal:  # Se o destino foi encontrado
        return (caminho, custo)

    return None

def ajustarCaminho(novoNo, listaCaminho):
    indice = next((i for i, (coord, _, _) in enumerate(listaCaminho) if coord == novoNo.Posicao), None)
    if indice is None:
        listaCaminho.append((novoNo.Posicao, novoNo.CustoMovimentacao, novoNo.CustoTerreno))
    else:
        listaCaminho = listaCaminho[:indice+1].copy()
        bucetinha23 = None
    return listaCaminho

def calcularCaminho(listaCaminho):
    caminho = []
    for no in listaCaminho[1:]:
        caminho.append(no[0])
    return caminho

def calcularCustoCaminho(listaCaminho):
    listaIteracao = listaCaminho[1:]
    custo = 0
    for no in listaIteracao:
        custo += no[1] + no[2]
    return custo

def funcaoHeuristica(posicao, posicaoFinal):
    return ((posicaoFinal[0] - posicao[0]) ** 2 + (posicaoFinal[1] - posicao[1]) ** 2) ** (1 / 2)

def posicoesVizinhas(posicaoVisitada, posicaoFinal, custoLinha, custoDiagonal, map, posicoesComNos):
    vizinhos = set()

    for move in (Movement.U, Movement.D, Movement.R, Movement.L):
        novaPosicao = (posicaoVisitada.Posicao[0]+ move.value[0], posicaoVisitada.Posicao[1] + move.value[1])
        if map.in_map(novaPosicao):
            node = posicoesComNos.get(novaPosicao)
            if node is None:
                node = Node(novaPosicao, map.get(novaPosicao)[0], custoLinha, posicaoFinal)
                posicoesComNos[novaPosicao] = node
            vizinhos.add(node)
            node.custoMovimentacao = custoLinha

    for move in (Movement.UL, Movement.UR, Movement.DL, Movement.DR):
        novaPosicao = (posicaoVisitada.Posicao[0]+ move.value[0], posicaoVisitada.Posicao[1] + move.value[1])
        if map.in_map(novaPosicao):
            node = posicoesComNos.get(novaPosicao)
            if node is None:
                node = Node(novaPosicao, map.get(novaPosicao)[0], custoDiagonal, posicaoFinal)
                posicoesComNos[novaPosicao] = node
            vizinhos.add(node)
            node.custoMovimentacao = custoDiagonal
    return vizinhos

def convert_path_to_actions(caminho):
    actions = []
    for i in range(0, len(caminho)):
        dx =  caminho[i][0] - caminho[i-1][0]
        dy =  caminho[i][1] - caminho[i-1][1]
        actions.append((dx, dy))
    return actions