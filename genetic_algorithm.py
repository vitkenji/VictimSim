import random
import numpy as np
from copy import deepcopy

generations = 100
mutation_rate = 0.1
population_size = 50

class GeneticAlgorithm:
    def __init__(self, battery, victims):
        self.victims = victims
        self.battery = battery
    
    def fitness(self):
        print("")

    def crossover(self):
        print("")

    def mutate(self):
        print("")

    def distance(self, s1, s2):
        return abs(s1[0] - s2[0]) + abs(s1[1] - s2[1])

    def run(self):
        population = [random.sample(list(self.victims.keys())) for _ in range(population_size)]
        
        