import os
import random
import math
import csv
import sys
from map import Map
from vs.abstract_agent import AbstAgent
from vs.physical_agent import PhysAgent
from vs.constants import VS
from bfs import BFS
from abc import ABC, abstractmethod
from LRTAStar import *
from sklearn.cluster import KMeans
from concurrent.futures import ThreadPoolExecutor
import classifier
import regressor
import pandas as pd

class Rescuer(AbstAgent):
    def __init__(self, env, config_file, nb_of_explorers=1,clusters=[]):
        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.nb_of_explorers = nb_of_explorers
        self.received_maps = 0
        self.map = Map()
        self.victims = {}
        self.plan = []
        self.plan_x = 0
        self.plan_y = 0
        self.plan_visited = set()
        self.plan_rtime = self.TLIM
        self.plan_walk_time = 0.0
        self.x = 0
        self.y = 0
        self.clusters = clusters
        self.sequences = clusters

        #model = training(file='datasets/data_4000v/env_vital_signals.txt')
        #save(model, file='neural_network_model.pkl')
        #model = load('neural_network_model.pkl')
        #testing(model, 'datasets/data_800v/env_vital_signals.txt')
        
        self.set_state(VS.IDLE)

    def save_cluster_csv(self, cluster, cluster_id):
        filename = f"./clusters/cluster{cluster_id}.txt"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for vic_id, values in cluster.items():
                x, y = values[0]
                vs = values[1]
                writer.writerow([vic_id, x, y, vs[6], vs[7]])

    def save_sequence_csv(self, sequence, sequence_id):
        filename = f"./clusters/seq{sequence_id}.txt"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for id, values in sequence.items():
                x, y = values[0]
                vs = values[1]
                writer.writerow([id, x, y, vs[6], vs[7]])

    def cluster_victims(self):
        cluster0 = {}
        cluster1 = {}
        cluster2 = {}
        cluster3 = {}

        coordenadas = [(float(coord[0][0]), float(coord[0][1])) for vitima, coord in self.victims.items()]
        #modelo = KMeans(4, init="k-means++", max_iter=100)
        modelo = KMeans(4, init="k-means++")
        modelo.fit(coordenadas)
        etiquetas = modelo.labels_

        i = 0
        for key, values in self.victims.items():  # values are pairs: ((x,y), [<vital signals list>])
            if etiquetas[i] == 0:
                cluster0[key] = values
            elif etiquetas[i] == 1:
                cluster1[key] = values
            elif etiquetas[i] == 2:
                cluster2[key] = values
            elif etiquetas[i] == 3:
                cluster3[key] = values
            i+=1

        return [cluster0, cluster1, cluster2, cluster3]

    def predict_severity_and_class(self):

        classifier_model = classifier.training(file='datasets/data_4000v/env_vital_signals.txt')
        classifier.save(classifier_model, file='classifier_model.pkl')
        classifier_modell = classifier.load('classifier_model.pkl')
        classifier.testing(classifier_model, 'datasets/data_800v/env_vital_signals.txt')
        classifier_model = classifier.load('classifier_model.pkl')

        regressor_model = regressor.training(file='datasets/data_4000v/env_vital_signals.txt')
        regressor.save(regressor_model, file='regressor_model.pkl')
        regressor_model = regressor.load('regressor_model.pkl')
        regressor.testing(regressor_model, 'datasets/data_800v/env_vital_signals.txt')
        regressor_model = classifier.load('regressor_model.pkl')

        print(self.victims.items())
    
        dataframe = pd.DataFrame([victim[1][-3:] for _, victim in self.victims.items()])
        dataframe.columns = [['qPA', 'pulso', 'freqResp']]

        classification = classifier.predict(classifier_model, dataframe)
        regression = regressor.predict(regressor_model, dataframe)

        print(classification)
        print(regression)
        
        index = 0
        for vic_id, values in self.victims.items():
            print(vic_id, classification[index], regression[index])
            severity_value = regression[index]
            severity_class = classification[index]
            index += 1
            values[1].extend([severity_value, severity_class])
    
    def sequencing(self):
        new_sequences = []

        for seq in self.sequences:   # a list of sequences, being each sequence a dictionary
            seq = dict(sorted(seq.items(), key=lambda item: item[1]))
            new_sequences.append(seq)
            #print(f"{self.NAME} sequence of visit:\n{seq}\n")

        self.sequences = new_sequences

    def planner(self):

        posicaoAtual = (0, 0)
        trajetoria = []
        posicoesVitimas = dict(self.sequences[0])
        temEnergiaSuficiente = True
        tempoTotal = self.TLIM

        while len(posicoesVitimas) != 0 and temEnergiaSuficiente:
            vitimaSelecionada, caminhoVitimaSelecionada, menorCusto = self.calculaVitimaMenorEnergia(posicoesVitimas, posicaoAtual)
            caminhoVolta, custoVolta = LRTAStar(self.map, posicoesVitimas[vitimaSelecionada][0], (0, 0),
                                                self.COST_LINE, self.COST_DIAG)
            custoTotal = menorCusto + custoVolta + self.COST_FIRST_AID
            if (tempoTotal > custoTotal):
                    tempoTotal -= menorCusto + self.COST_FIRST_AID
                    trajetoria += caminhoVitimaSelecionada
                    posicaoAtual = posicoesVitimas[vitimaSelecionada][0]
                    del posicoesVitimas[vitimaSelecionada]
            else:
                if posicaoAtual != (0, 0,):
                    caminho, custo = LRTAStar(self.map, posicaoAtual, (0, 0), self.COST_LINE, self.COST_DIAG)
                    trajetoria += caminho
                temEnergiaSuficiente = False

        if (temEnergiaSuficiente and posicaoAtual != (0,0,)):
            caminho, custo = LRTAStar(self.map, posicaoAtual, (0, 0), self.COST_LINE, self.COST_DIAG)
            trajetoria += caminho
        self.plan = convert_path_to_actions(trajetoria)
        pass

    def calculaVitimaMenorEnergia(self, vitimas, posicaoAtual):
        vitimaSelecionada = None
        caminhoVitimaSelecionada = []
        menorCusto = float('inf')

        with ThreadPoolExecutor(max_workers=20) as executor:
            futuras = {executor.submit(self.calculaCustoEnegia, posicaoVitima, posicaoAtual): numVitima
                       for numVitima, posicaoVitima in vitimas.items()}

            for futura in futuras:
                resultado = futura.result()
                caminho, custo = resultado

                if custo < menorCusto:
                    vitimaSelecionada = futuras[futura]
                    caminhoVitimaSelecionada = caminho
                    menorCusto = custo

        return vitimaSelecionada, caminhoVitimaSelecionada, menorCusto

    def calculaCustoEnegia(self, posicaoVitima, posicaoAtual):
        return LRTAStar(self.map, posicaoAtual, posicaoVitima[0], self.COST_LINE, self.COST_DIAG)

    def sync_explorers(self, explorer_map, victims):
        """ This method should be invoked only to the master agent

        Each explorer sends the map containing the obstacles and
        victims' location. The master rescuer updates its map with the
        received one. It does the same for the victims' vital signals.
        After, it should classify each severity of each victim (critical, ..., stable);
        Following, using some clustering method, it should group the victims and
        and pass one (or more)clusters to each rescuer """

        self.received_maps += 1

        print(f"{self.NAME} Map received from the explorer")
        self.map.update(explorer_map)
        self.victims.update(victims)

        if self.received_maps == self.nb_of_explorers:
            print(f"{self.NAME} all maps received from the explorers")
            #self.map.draw()
            #print(f"{self.NAME} found victims by all explorers:\n{self.victims}")

            #@TODO predict the severity and the class of victims' using a classifier
            self.predict_severity_and_class()

            #@TODO cluster the victims possibly using the severity and other criteria
            # Here, there 4 clusters
            clusters_of_vic = self.cluster_victims()

            for i, cluster in enumerate(clusters_of_vic):
                self.save_cluster_csv(cluster, i+1)    # file names start at 1
  
            # Instantiate the other rescuers
            rescuers = [None] * 4
            rescuers[0] = self                    # the master rescuer is the index 0 agent

            # Assign the cluster the master agent is in charge of 
            self.clusters = [clusters_of_vic[0]]  # the first one

            # Instantiate the other rescuers and assign the clusters to them
            for i in range(1, 4):    
                #print(f"{self.NAME} instantianting rescuer {i+1}, {self.get_env()}")
                filename = f"rescuer_{1}_config.txt"
                config_file = os.path.join(self.config_folder, filename)
                # each rescuer receives one cluster of victims
                rescuers[i] = Rescuer(self.get_env(), config_file, 4, [clusters_of_vic[i]]) 
                rescuers[i].map = self.map     # each rescuer have the map

            
            # Calculate the sequence of rescue for each agent
            # In this case, each agent has just one cluster and one sequence
            self.sequences = self.clusters         

            # For each rescuer, we calculate the rescue sequence 
            for i, rescuer in enumerate(rescuers):
                rescuer.sequencing()         # the sequencing will reorder the cluster
                
                for j, sequence in enumerate(rescuer.sequences):
                    if j == 0:
                        self.save_sequence_csv(sequence, i+1)              # primeira sequencia do 1o. cluster 1: seq1 
                    else:
                        self.save_sequence_csv(sequence, (i+1)+ j*10)      # demais sequencias do 1o. cluster: seq11, seq12, seq13, ...

            
                rescuer.planner()            # make the plan for the trajectory
                rescuer.set_state(VS.ACTIVE) # from now, the simulator calls the deliberation method 
         
        
    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        # No more actions to do
        if self.plan == []:  # empty list, no more actions to do
           print(f"{self.NAME} has finished the plan [ENTER]")
           return False

        # Takes the first action of the plan (walk action) and removes it from the plan
        dx, dy = self.plan.pop(0)
        #print(f"{self.NAME} pop dx: {dx} dy: {dy} ")

        # Walk - just one step per deliberation
        walked = self.walk(dx, dy)

        # Rescue the victim at the current position
        if walked == VS.EXECUTED:
            self.x += dx
            self.y += dy
            #print(f"{self.NAME} Walk ok - Rescuer at position ({self.x}, {self.y})")

            # check if there is a victim at the current position
            if self.map.in_map((self.x, self.y)):
                vic_id = self.map.get_vic_id((self.x, self.y))
                if vic_id != VS.NO_VICTIM:
                    self.first_aid()
                    #if self.first_aid(): # True when rescued
                        #print(f"{self.NAME} Victim rescued at ({self.x}, {self.y})")                    
        else:
            print(f"{self.NAME} Plan fail - walk error - agent at ({self.x}, {self.x})")
            
        return True

