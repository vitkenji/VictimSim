import threading
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
from AlgoritmoGenetico import algoritmo_genetico

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
        self.resultado = []

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
            for values in sequence:
                id = values[0]
                x, y = values[1], values[2]
                writer.writerow([id, x, y, values[3], values[4]])

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
        regressor_model = regressor.load('regressor_model.pkl')
        

        dataframe = pd.DataFrame([victim[1][-3:] for _, victim in self.victims.items()])
        dataframe.columns = [['qpa', 'pulse', 'freq']]

        regression = regressor.predict(regressor_model, dataframe)
        classification = classifier.predict(classifier_model, dataframe)
        
        index = 0
        for vic_id, values in self.victims.items():
            print(vic_id, classification[index], f"{regression[index]:.1f}")
            severity_value = regression[index]
            severity_class = classification[index]
            index += 1
            values[1].extend([severity_value, severity_class])
    
    def sequencing(self):
        vitimas = []
        new_sequency = []
        for keys, values in self.clusters[0].items():
            vitimas.append((keys, values[0][0], values[0][1], values[1][6], values[1][7]))
        new_sequency, self.resultado = algoritmo_genetico(self.map, vitimas, self.COST_LINE, self.COST_DIAG, self.TLIM)
        return new_sequency[1:-1]

    def planner(self):

        self.plan = convert_path_to_actions(self.resultado)

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
    
            self.predict_severity_and_class()

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

            threads = []
            for i, rescuer in enumerate(rescuers):
                thread = threading.Thread(target=self.process_rescuer, args=(rescuer, i))
                threads.append(thread)
                thread.start()

            # Aguarda todas as threads terminarem
            for thread in threads:
                thread.join()


    def process_rescuer(self, rescuer, i):
        sequence = rescuer.sequencing()  # the sequencing will reorder the cluster

        self.save_sequence_csv(sequence, i + 1)  # primeira sequencia do 1o. cluster 1: seq1

        rescuer.planner()  # make the plan for the trajectory
        rescuer.set_state(VS.ACTIVE)  # from
         
        
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
    
    def convert_path_to_actions(caminho):
        actions = []
        for i in range(1, len(caminho)):
            dx = caminho[i][0] - caminho[i - 1][0]
            dy = caminho[i][1] - caminho[i - 1][1]
            actions.append((dx, dy))
        return actions

