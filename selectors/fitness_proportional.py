#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random

# all fitnesses must be non-negative
def fitness_proportional(population, config={'fitness': lambda x: x.fitness}):
    '''roulette wheel selection'''
    fitness = config['fitness']
    total_fitness = sum([fitness(x) for x in population])
    choice_point = random.random(total_fitness)
    accumulated_fitness = 0
    for individual in population:
        accumulated_fitness += fitness(individual)
        if accumulated_fitness >= choice_point:
            return individual
