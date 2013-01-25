#!/usr/bin/env python
#
# BBSA Auto-benchmark

import logging
logformat = '%(asctime)s:%(levelname)s:%(message)s'
loglevel = logging.WARNING
logging.basicConfig(format=logformat, level=loglevel)

import json
from math import sqrt
from search_algorithms import random_search, climb_hill
from fitness_functions import fitness_nk_landscape
from representations.bit_string import bit_string as individual


def statistics(s):
    '''min, max, mean, stddev'''
    result = {'min': 0, 'max': 0, 'mean': 0, 'stddev': 0}
    result['min'] = min(s)
    result['max'] = max(s)
    result['mean'] = sum(s) / float(len(s))
    result['stddev'] = \
        sqrt(sum((x - result['mean']) ** 2 for x in s) / float(len(s) - 1))
    return result


def run_search(search, fitness, max_evals, length):
    current = individual().get_random(length=length)
    result = {'best': current,
              'evals': [{'count': 1,
                          'current_best': current}]}

    for evals in xrange(1, max_evals):
        current = search(current, fitness=fitness)
        if fitness(current) > fitness(result['best']):
            logging.info("%i %.2f %s" % (evals, fitness(current), current))
            result['best'] = current
            result['evals'].append({'count': evals,
                                    'current_best': result['best']})
    logging.info("----------------")
    return result['best']

length = 8
huge_number = 20000
max_evals = 1000
population = [fitness_nk_landscape(n=length) for i in xrange(12)]


def get_fitnesses():
    global population
    for landscape in population:
        if hasattr(landscape, 'fitness'):
            continue
        best = run_search(random_search, landscape, huge_number, length)

        result = list()
        for i in xrange(3):
            result.append(run_search(random_search, landscape, max_evals, length))
        random_search_solves = len([x for x in result if x == best])

        result = list()
        for i in xrange(3):
            result.append(run_search(climb_hill, landscape, max_evals, length))
        climb_hill_solves = len([x for x in result if x == best])

        landscape.fitness = random_search_solves - climb_hill_solves
        landscape.best = best
    stats = statistics([x.fitness for x in population])
    print json.dumps(stats)


def mate_and_die():
    global population
    population.sort(key=lambda x: x.fitness, reverse=True)
    population = population[:6]
    kids1 = population[0].one_point_crossover(population[1])
    kids2 = population[2].one_point_crossover(population[3])
    kids3 = population[5].one_point_crossover(population[5])
    kids = [x.one_point_mutate() for x in kids1 + kids2 + kids3]
    population.extend(kids)


def main():
    for i in xrange(20):
        get_fitnesses()
        mate_and_die()

    get_fitnesses()
    stats = statistics([x.fitness for x in population])
    print json.dumps(stats)


# if __name__ == "__main__":
#     main()

import cProfile
cProfile.run('main()', 'profiling.prof')
