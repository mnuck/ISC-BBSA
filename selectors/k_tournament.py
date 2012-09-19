#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random

###############################################
### k_tournament
###
### @description generate a parent pool of size n via k_tournament
###
### Precondition:  len(population) >= n, k
###                k + 1 < len(population) - n
### Postcondition: None
###
### @param population: the population of eligibles
### @param n: the number of selectees required
### @param k: the size of each tournament
### @param function: a function to be used by max()
###                  to select the best contestant
### @param replacement: if replacement is True, then contestants
###                     are copied out of the population
###                     if false, then contestants are "physically"
###                     removed. Hence clones are not possible
###
### @return a list of selectees
###
### @limitations: None
###
###############################################
def k_tournament(population, config={'fitness': lambda x: x.fitness,
                                     'replacement': False,
                                     'k': 1, 'n': 1}):
    my_population = population[:]
    result = list()
    while len(result) < config['n']:
        winner = max(random.sample(my_population, config['k']), 
                     key=config['fitness'])
        result.append(winner)
        if not config['replacement']:
            my_population.remove(winner)
    return result
