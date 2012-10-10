#!/usr/bin/env python
#
# BBSA Auto-Benchmark


###############################################
### truncate
###
### @description select n 'best' members of a population
###
### Precondition:  len(population) >= n
### Postcondition: None
###
### @param population: the population of eligibles
### @param n: the number of selectees required
### @param function: a function to be used by sorted()
###                  to select the best individuals
###
### @return a list of selectees of length n
###############################################
def truncate(population,
             fitness=lambda x: x.fitness,
             n=1):
    return sorted(population, key=fitness)[:n]
