#!/usr/bin/env python
#
# BBSA Auto-benchmark

import logging
logformat = '%(asctime)s:%(levelname)s:%(message)s'
loglevel = logging.WARNING
logging.basicConfig(format=logformat, level=loglevel)


from search_algorithms import random_search, climb_hill
from fitness_functions import fitness_nk_landscape
from representations.bit_string import bit_string as individual


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

# generate 10 random NK landscapes
# run brute_force to ensure we know the actual optimal FIXME
# run random_search on each of them 10 times. count then number of times
#  random_search finds the global optima.
# run climb_hill on each of them 10 times, count the number of times
#  climb_hill finds the global optima.

# find the ratio for each NK landscape of
#  random_search solves / climb_hill solves + random_search_solves

length = 8
huge_number = 20000
max_evals = 1000
population = [fitness_nk_landscape(n=length) for i in xrange(10)]


def get_fitnesses():
    for landscape in population:
        if hasattr(landscape, 'fitness'):
            print landscape.best, landscape.fitness
        best = run_search(random_search, landscape, huge_number, length)
        # print best, 'is current best'

        result = list()
        for i in xrange(20):
            result.append(run_search(random_search, landscape, max_evals, length))
        random_search_solves = len([x for x in result if x == best])
        # print random_search_solves, 'solves by random_search'

        result = list()
        for i in xrange(20):
            result.append(run_search(climb_hill, landscape, max_evals, length))
        climb_hill_solves = len([x for x in result if x == best])
        # print climb_hill_solves, 'solves by climb_hill'

        landscape.fitness = 1 - (climb_hill_solves / float(random_search_solves))
        landscape.best = best
        print landscape.best, landscape.fitness
    ave = sum(x.fitness for x in population) / len(population)
    print "Average fitness:", ave


def mate_and_die():
    global population
    population.sort(key=lambda x: x.fitness, reverse=True)
    population = population[:5]
    kids = [x.one_point_mutate_neighbors() for x in population]
    population.extend(kids)


for i in xrange(10):
    get_fitnesses()
    mate_and_die()

ave = sum(x.fitness for x in population) / len(population)
print "Average fitness:", ave
