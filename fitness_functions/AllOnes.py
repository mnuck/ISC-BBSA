#!/usr/bin/env python
#
# BBSA Auto-Benchmark


# data must implement .count(), which returns the number of ones
def fitness_AllOnes(individual, data=lambda x: x.data, **kwargs):
    return data(individual).count()
