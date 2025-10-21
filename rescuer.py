import os
import csv
import sys
import joblib
import numpy as np
from map import Map
from vs.abstract_agent import AbstAgent
from vs.physical_agent import PhysAgent
from vs.constants import VS
from bfs import BFS
from abc import ABC, abstractmethod
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from a_star import a_star, a_star_plan_cost
from genetic_algorithm import GeneticAlgorithm
import warnings

warnings.filterwarnings("ignore")

class Rescuer(AbstAgent):
    def __init__(self, env, config_file, nb_of_explorers=1,clusters=[]):
        super().__init__(env, config_file)
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
        
        self.set_state(VS.IDLE)

    def save_cluster_csv(self, cluster, cluster_id):
        filename = f"./clusters/cluster{cluster_id}.txt"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for vic_id, values in cluster.items():
                x, y = values[0]      # x,y coordinates
                vs = values[1]        # list of vital signals
                writer.writerow([vic_id, x, y, vs[6], vs[7]])

    def save_sequence_csv(self, sequence, sequence_id):
        filename = f"./clusters/seq{sequence_id}.txt"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for id, values in sequence.items():
                x, y = values[0]      # x,y coordinates
                vs = values[1]        # list of vital signals
                writer.writerow([id, x, y, vs[6], vs[7]])

    def cluster_victims(self):
        coordinates = np.array([self.victims[v_id][0] for v_id in list(self.victims.keys())])
        
        kmeans = KMeans(n_clusters=4, random_state=0)
        labels = kmeans.fit_predict(coordinates)
        
        #plt.scatter(coordinates[:, 0], coordinates[:, 1], c=labels, cmap='viridis', s=50)
        #plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], c='red', s=200, marker='X', label='Centros')
        #plt.grid(True)
        #plt.show()

        clusters = [{},{},{},{}]
        for v_id, label in zip(list(self.victims.keys()), labels):
            clusters[label][v_id] = self.victims[v_id]

        return clusters

    def predict_severity_and_class(self):
        classifier = joblib.load('./models/classifier.pkl')
        regressor = joblib.load('./models/regressor.pkl')
        for vic_id, values in self.victims.items():
            values[1].extend([regressor.predict([values[1][1:]])[0].item(), classifier.predict([values[1][1:]])[0].item()])

    def sequencing(self):
        """ Currently, this method sort the victims by the x coordinate followed by the y coordinate
            @TODO It must be replaced by a Genetic Algorithm that finds the possibly best visiting order """

        """ We consider an agent may have different sequences of rescue. The idea is the rescuer can execute
            sequence[0], sequence[1], ...
            A sequence is a dictionary with the following structure: [vic_id]: ((x,y), [<vs>]"""

        new_sequences = []

        #genetic_algorithm = GeneticAlgorithm(self.get_rtime(), self.victims)
        #genetic_algorithm.run()
        for seq in self.sequences:   # a list of sequences, being each sequence a dictionary
            seq = dict(sorted(seq.items(), key=lambda item: item[1]))
            new_sequences.append(seq)       
            #print(f"{self.NAME} sequence of visit:\n{seq}\n")

        self.sequences = new_sequences

    def planner(self):
        """ A method that calculates the path between victims: walk actions in a OFF-LINE MANNER (the agent plans, stores the plan, and
            after it executes. Eeach element of the plan is a pair dx, dy that defines the increments for the the x-axis and  y-axis."""


        # let's instantiate the breadth-first search
        bfs = BFS(self.map, self.COST_LINE, self.COST_DIAG)

        # for each victim of the first sequence of rescue for this agent, we're going go calculate a path
        # starting at the base - always at (0,0) in relative coords
        
        if not self.sequences:   # no sequence assigned to the agent, nothing to do
            return

        # we consider only the first sequence (the simpler case)
        # The victims are sorted by x followed by y positions: [vic_id]: ((x,y), [<vs>]

        sequence = self.sequences[0]
        start = (0,0) # always from starting at the base
        for vic_id in sequence:
            goal = sequence[vic_id][0]
            plan, time = bfs.search(start, goal, self.plan_rtime)
            self.plan = self.plan + plan
            self.plan_rtime = self.plan_rtime - time
            start = goal

        # Plan to come back to the base
        goal = (0,0)
        plan, time = bfs.search(start, goal, self.plan_rtime)
        self.plan = self.plan + plan
        self.plan_rtime = self.plan_rtime - time
           

    def sync_explorers(self, explorer_map, victims):
        """ This method should be invoked only to the master agent

        Each explorer sends the map containing the obstacles and
        victims' location. The master rescuer updates its map with the
        received one. It does the same for the victims' vital signals.
        After, it should classify each severity of each victim (critical, ..., stable);
        Following, using some clustering method, it should group the victims and
        and pass one (or more)clusters to each rescuer """

        self.received_maps += 1

        # print(f"{self.NAME} Map received from the explorer")
        self.map.update(explorer_map)
        self.victims.update(victims)

        if self.received_maps == self.nb_of_explorers:
            print(f"{self.NAME} all maps received from the explorers")
            #print(f"{self.NAME} found victims by all explorers:\n{self.victims}")

            self.predict_severity_and_class()

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
                filename = f"rescuer_{i+1:1d}_config.txt"
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

