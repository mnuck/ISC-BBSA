#!/usr/bin/env python
#
# BBSA Auto-benchmark

import logging
logformat = '%(asctime)s:%(levelname)s:%(message)s'
loglevel = logging.WARNING
logging.basicConfig(format=logformat, level=loglevel)

from math import sqrt
from representations.bit_string import bit_string

# import fitness_functions.nk_landscape as nk
# nk_fitness = nk.fitness_nk_landscape
# nk.cudaEnabled = False
from fitness_functions.DTRAP import fitness_DTRAP as dtrap

from search_algorithms.mu_lambda_ea import make_solver
from search_algorithms.mu_lambda_ea import make_default_child_maker

from search_algorithms.simulated_annealing import make_SA_solver

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


genome_length = 100
mu = 100
lam = 10


def population_maker():
    starter = bit_string()
    return [starter.get_random(genome_length) for i in xrange(mu)]


def initial_solution_maker():
    starter = bit_string()
    return starter.get_random(genome_length)


def fit_one_fit(fit):
    ea1 = make_solver(make_initial_population=population_maker,
                      survival_selector=make_SUS(fitness=fit, n=mu),
                      parent_selector=make_SUS(fitness=fit, n=lam),
                      fitness=fit)
    # ea2 = make_solver(make_initial_population=population_maker,
    #                   survival_selector=make_k_tournament(fitness=fit,
    #                                                       replacement=True,
    #                                                       k=2, n=mu),
    #                   parent_selector=make_k_tournament(fitness=fit,
    #                                                     replacement=True,
    #                                                     k=2, n=lam),
    #                   fitness=fit)

    sa = make_SA_solver(evals=1000,
                        initial_solution_maker=initial_solution_maker,
                        fitness=fit)

    results = [sa() for i in xrange(10)]
    result_fits = [fit(x) for x in results]
    #print "SA", statistics(result_fits)
    b = statistics(result_fits)['mean']

    result_pops = [ea1() for i in xrange(10)]
    result_fits = [[fit(x) for x in y] for y in result_pops]
    result_stats = [statistics(x)['max'] for x in result_fits]
    #print "EA", statistics(result_stats)
    a = statistics(result_stats)['mean']

    # result_pops = [ea2() for i in xrange(10)]
    # result_fits = [[fit(x) for x in y] for y in result_pops]
    # result_stats = [statistics(x)['max'] for x in result_fits]
    # b = statistics(result_stats)['mean']

    return 50 + b - a


def fit_fits(fits):
    for fit in fits:
        # s = fit.dumps()
        # # dump s into a queue
        # x = nk_fitness()
        # x.loads(s)
        fit.fitness = fit_one_fit(fit)
        # fit.fitness = fit_one_fit(fit)


def initial_fits():
    return [dtrap(n=genome_length, k=4, random_trap=True)
            for i in xrange(20)]


def main():
    fits = initial_fits()
    fit_fits(fits)

    survival_selector = make_SUS(fitness=lambda x: x.fitness, n=20)
    parent_selector = make_SUS(fitness=lambda x: x.fitness, n=5)
    child_maker = make_default_child_maker(mutation_rate=0.2)

    while True:
        print statistics([x.fitness for x in fits])
        parents = parent_selector(fits)
        children = child_maker(parents)
        fit_fits(children)
        fits.extend(children)
        fits = survival_selector(fits)


# if __name__ == "__main__":
#     main()

import cProfile
cProfile.run('main()', 'profiling.prof')
