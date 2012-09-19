#!/usr/bin/env python
#
# BBSA Auto-Benchmark

def truncate(population, config={'fitness': lambda x: x.fitness}):
    fitness = config['fitness']
    return min(population, key=fitness)
