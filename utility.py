#!/usr/bin/env python
#
# BBSA Auto-benchmark

from math import sqrt


def statistics(s):
    '''min, max, mean, stddev'''
    result = {'min': 0, 'max': 0, 'mean': 0, 'stddev': 0}
    result['min'] = min(s)
    result['max'] = max(s)
    result['mean'] = sum(s) / float(len(s))
    result['stddev'] = \
        sqrt(sum((x - result['mean']) ** 2 for x in s) / float(len(s) - 1))
    return result


def population_analyzer(population, state):
    result = dict()
    fits = [x.fitness for x in population]
    for p in population:
        if not hasattr(p, '__age'):
            p.__age = -1
        p.age += 1
    ages = [x.__age for x in population]
    result['fitness'] = statistics(fits)
    result['ages'] = statistics(ages)
    result['best_fitness'] = max(result['best_fitness'],
                                 result['fitness']['max'])
    result['worst_fitness'] = min(result['worst_fitness'],
                                  result['fitness']['min'])
    result['size'] = len(population)
    return result


state = {
    'evals': 0,
    'max_evals': 10000,
    'best_fitness': 0,
    'worst_fitness': -1,
    'population_stats': {
        'fitness': {
            'max': 10,
            'min': -1,
            'mean': 6,
            'stddev': 3.4},
        'age': {
            'max': 10,
            'min': 0,
            'mean': 5,
            'stddev': 3},
    'size': 100,
    'diversity': 12
    }
}
