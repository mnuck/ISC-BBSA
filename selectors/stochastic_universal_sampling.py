#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random


###############################################
### stochastic_universal_sampling
###
### @description select n members of a population
###
### Precondition:  None
### Postcondition: None
###
### @param population: the population of eligibles
### @param n: the number of selectees required
### @param fitness: a function that quantifies
###                 the value of an individual
###
### @return a list of selectees of length n
###
### @limitations all fitnesses must be non-negative
###############################################
def stochastic_universal_sampling(population,
                                  fitness=lambda x: x.fitness,
                                  n=1):
    total_fitness = sum([fitness(x) for x in population])
    spacing = total_fitness / float(n)
    choice_point = random.random() * spacing
    accumulated_fitness = 0
    result = list()
    for individual in population:
        accumulated_fitness += fitness(individual)
        while choice_point < accumulated_fitness:
            result.append(individual)
            choice_point += spacing
    return result

SUS = stochastic_universal_sampling


def fitness_proportional(population, fitness=lambda x: x.fitness):
    return SUS(population, fitness, 1)[0]
