#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random


###############################################
### k_tournament
###
### @description select n members of a population via k-tournment
###
### Precondition:  len(population) >= n, k
###                k + 1 < len(population) - n
### Postcondition: None
###
### @param population: the population of eligibles
### @param n: the number of selectees required
### @param k: the size of each tournament
### @param fitness: a function to be used by max()
###                  to select the best contestant
### @param replacement: if replacement is True, then individuals
###                     can be selected more than once
###
### @return a list of selectees of length n
###############################################
def k_tournament(population,
                 fitness=lambda x: x.fitness,
                 replacement=False,
                 k=1, n=1):
    my_population = population[:]
    result = list()
    while len(result) < n:
        winner = max(random.sample(my_population, k),
                     key=fitness)
        result.append(winner)
        if not replacement:
            my_population.remove(winner)
    return result
