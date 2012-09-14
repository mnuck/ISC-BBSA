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

def climb_hill(current, fitness=None, wander_plateau=True, restart=False):
    '''Moves to the neighbor with highest fitness'''
    neighbors = current.get_neighbors()
    if not neighbors:
        return current
    best_fit = max([fitness(x) for x in neighbors])
    if fitness(current) > best_fit:
        if not restart:
            return current
        else:
            return climb_hill(current.get_random(), 
                              wander_plateau=wander_plateau,
                              restart=restart)        
    if fitness(current) == best_fit and not wander_plateau:
        return current
    candidates = [x for x in neighbors if fitness(x) == best_fit]
    return random.choice(candidates)
