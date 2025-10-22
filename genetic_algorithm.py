import random
import numpy as np
from copy import deepcopy
import time

GENERATIONS = 100
MUTATION_RATE = 0.1
POPULATION_SIZE = 50

class GeneticAlgorithm:
    def __init__(self, battery, victims):
        self.victims = victims
        self.battery = battery

    def fitness(self, sequence):
        #if sequence != []:
            #print(f"sequence: {len(sequence)}")

        total_cost = 0
        total_score = 0
        current = (0,0)


        for vid in sequence:
            vx, vy = self.victims[vid][0]
            gravity = self.victims[vid][1][6]
            classification = self.victims[vid][1][7]
            if vx != None and vy != None:
                print(f"{(vx, vy)} + {gravity} + {classification}")
            
            d = self.distance(current, (vx, vy))
            total_cost += d
            cost_return = total_cost + self.distance((vx, vy), (0,0))
            if cost_return > self.battery:
                break

            weight = 0.6*gravity + 10*classification
            total_score += weight
            current = (vx, vy)
        
        return total_score - 0.1 * total_cost
            
    def crossover(self, parent1, parent2):
        a, b = sorted(random.sample(range(len(parent1)), 2))
        child = [None]*len(parent1)
        child[a:b] = parent1[a:b]

        fill_positions = [x for x in parent2 if x not in child]
        j = 0
        for i in range(len(parent1)):
            if child[i] is None:
                child[i] = fill_positions[j]
                j += 1

        return child

    def mutate(self, individual):
        if random.random() < MUTATION_RATE:
            i, j = random.sample(range(len(individual)), 2)
            individual[i], individual[j] = individual[j], individual[i]

    def selection(self, population, fitness_values):
        selected = random.sample(list(zip(population, fitness_values)), 3)
        return max(selected, key=lambda x: x[1])[0]

    def distance(self, s1, s2):
        dx = abs(s1[0] - s2[0])
        dy = abs(s1[1] - s2[1])
        diag = min(dx,dy)
        straight = abs(dx - dy)
        return 1.5*diag + straight
    
    def compute_distances(self):
        keys = list(self.victims.keys())
        dist = {}
        for i in keys:
            for j in keys:
                if i != j:
                    dist[(i, j)] = self.distance(self.victims[i][0], self.victims[j][0])
        return dist

    def run(self):
        ids = list(self.victims.keys())
        population = [random.sample(ids, len(ids)) for _ in range(POPULATION_SIZE)]
        #print(f"population: {population}")
        best_solution = None
        best_fitness = -float('inf')

        for gen in range(GENERATIONS):
            fitness_values = [self.fitness(seq) for seq in population]
            new_population = []

            elite = np.argmax(fitness_values)
            new_population.append(deepcopy(population[elite]))

            while len(new_population) < POPULATION_SIZE:
                parent1 = self.selection(population, fitness_values)
                parent2 = self.selection(population, fitness_values)
                child = self.crossover(parent1, parent2)
                self.mutate(child)
                new_population.append(child)
            
            population = new_population

            if max(fitness_values) > best_fitness:
                best_fitness = max(fitness_values)
                best_solution = deepcopy(population[np.argmax(fitness_values)])
        
        return {vid : self.victims[vid] for vid in best_solution} 