#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random


###############################################
### simulated annealing
###
### Picks a neighbor and decides to move to it, or not, depending
### on randomness and a cooling schedule
###
### Precondition:  none
### Postcondition: none
###
### @param current: must implement .get_neighbors(),
###               which must return a list of items that implement .fitness
### @param fitness: a function that establishes the fitness of an individual
### @param temp: how 'willing' the algorithm is to go downhill
###
### @return the state picked by simulated annealing
###############################################
def simulated_annealing(current,
                        fitness=lambda x: x.fitness,
                        temp=lambda: 0):
    '''Climbs hills, but sometimes is willing to go downhill'''
    neighbor = random.choice(current.get_neighbors())
    if fitness(current) > fitness(neighbor):
        better, worse = current, neighbor
    else:
        better, worse = neighbor, current
    if random.random() > (1 + temp.next()) / 2:
        result = better
    else:
        result = worse
    return result

SA = simulated_annealing


def linear_decrease(starting_temp=1.0, max_time=10000):
    i = 0
    step = 1.0 / max_time
    result = starting_temp
    yield result
    for _ in xrange(max_time):
        i += 1
        result -= step
        yield result


def make_SA_solver(evals, initial_solution_maker,
                   temp_schedule=None, fitness=lambda x: x.fitness):
    def SA_solver():
        temp_schedule = linear_decrease(max_time=evals)

        result = initial_solution_maker()
        for i in xrange(evals):
            result = simulated_annealing(result, fitness, temp_schedule)
        return result

    return SA_solver

