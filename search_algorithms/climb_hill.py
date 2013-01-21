#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random


# Finds the neighbor[s] with highest fitness
# If there is more than one, picks randomly
# If we're at a local maxima, return current
# wander_plateau=True attempts to randomly wander across flat-fitness regions
# current must implement .get_neighbors(), which must return an iterable
#  of items that implement .fitness
# restart=True means if we are already at a local maxima, then we restart
def climb_hill(current, fitness=lambda x: x.fitness, **kwargs):
    '''Moves to the neighbor with highest fitness'''
    neighbors = current.get_neighbors()
    neighbors.append(current)
    best_fit = max([fitness(x) for x in neighbors])
    candidates = [n for n in neighbors if fitness(n) == best_fit]
    return random.choice(candidates)
