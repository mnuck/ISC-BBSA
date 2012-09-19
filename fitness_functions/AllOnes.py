#!/usr/bin/env python
#
# BBSA Auto-Benchmark

# data must implement .count(), which returns the number of ones
def fitness_AllOnes(individual, config ={'data': lambda x: x.data}):
    data = config['data'](individual)
    return data.count()
