#!/usr/bin/env python
#
# BBSA Auto-benchmark

import logging
logformat = '%(asctime)s:%(levelname)s:%(message)s'
loglevel = logging.WARNING
logging.basicConfig(format=logformat, level=loglevel)

import json
from math import sqrt
from representations.bit_string import bit_string

import fitness_functions.nk_landscape as nk
nk_fitness = nk.fitness_nk_landscape
nk.cudaEnabled = False

from search_algorithms.mu_lambda_ea import make_solver

from selectors import make_k_tournament, make_SUS

def statistics(s):
    '''min, max, mean, stddev'''
    result = {'min': 0, 'max': 0, 'mean': 0, 'stddev': 0}
    result['min'] = min(s)
    result['max'] = max(s)
    result['mean'] = sum(s) / float(len(s))
    result['stddev'] = \
        sqrt(sum((x - result['mean']) ** 2 for x in s) / float(len(s) - 1))
    return result



genome_length = 1000
mu = 10
lam = 5

def population_maker():
    starter = bit_string()
    return [starter.get_random(genome_length) for i in xrange(mu)]


def main():
    fits = [nk_fitness(n=genome_length) for i in xrange(12)]
    for fit in fits:
        ea1 = make_solver(make_initial_population=population_maker,
                          survival_selector=make_SUS(fitness=fit, n=mu),
                          parent_selector=make_SUS(fitness=fit, n=lam))
        result_pops = [ea1() for i in xrange(5)]
        result_fits = [[fit(x) for x in y] for y in result_pops]
        result_stats = [statistics(x) for x in result_fits]

        # ea2 = make_solver(random_individual=individual_maker,
        #                   survival_selector=make_k_tournament(fitness=fit, 
        #                                                       replacement=True,
        #                                                       k=10, n=mu),
        #                   parent_selector=make_k_tournament(fitness=fit,
        #                                                     replacement=True,
        #                                                     k=10, n=lam),
        #                   child_maker=make_babies)
        print result_stats

    # make an EA solver that uses SUS
    # make an EA solver that uses k-tournament
    # make a population of NK landscapes
    # evolve an NK landscape where K-T tends to beat SUS
    pass


# if __name__ == "__main__":
#     main()

import cProfile
cProfile.run('main()', 'profiling.prof')
