#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random


###############################################
### climb_hill
###
### Finds the neighbor[s] with highest fitness
### If there is more than one, picks randomly
### If we're at a local maxima, return current
###
### Precondition:  none
### Postcondition: none
###
### @param current: must implement .get_neighbors(),
###               which must return a list of items that implement .fitness
### @param fitness: a function that establishes the fitness of an individual
###
### @return the neighbor (or current) with highest fitness
###############################################
def climb_hill(current, fitness=lambda x: x.fitness, **kwargs):
    '''Moves to the neighbor with highest fitness'''
    neighbors = current.get_neighbors()
    neighbors.append(current)
    best_fit = max([fitness(x) for x in neighbors])
    candidates = [n for n in neighbors if fitness(n) == best_fit]
    return random.choice(candidates)


def make_climb_hill_solver(evals, initial_solution_maker,
                           fitness=lambda x: x.fitness, **kwargs):
    def solver():
        print "starting a hill climb"
        evals_left = evals
        current = initial_solution_maker()
        result = current
        while evals_left > 0:
            neighbors = current.get_neighbors()
            best_fit = max([fitness(x) for x in neighbors])
            evals_left -= len(neighbors)
            if best_fit <= fitness(current):  # local optima found.
                current = initial_solution_maker()
            else:
                candidates = [n for n in neighbors if fitness(n) == best_fit]
                current = random.choice(candidates)
            if fitness(current) > fitness(result):
                result = current
        return result
    return solver
