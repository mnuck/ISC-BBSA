#!/usr/bin/env python
#
# BBSA Auto-benchmark

import logging
logformat = '%(asctime)s:%(levelname)s:%(message)s'
loglevel = logging.WARNING
logging.basicConfig(format=logformat, level=loglevel)

from utility import statistics

from representations.bit_string import bit_string

from fitness_functions.DTRAP import fitness_DTRAP_Reece as dtrap

from search_algorithms.mu_lambda_ea import make_solver as make_EA
from search_algorithms.mu_lambda_ea import make_default_child_maker
from search_algorithms.simulated_annealing import make_SA_solver as make_SA

from selectors import make_SUS


genome_length = 100
ea_mu = 100
ea_lam = 10

fit_mu = 20
fit_traplength = 4


def initial_fits():
    '''initial population of fitnesses'''
    return [dtrap(n=genome_length, k=fit_traplength, random_trap=True)
            for i in xrange(fit_mu)]


def random_solution_maker():
    '''for single-solution algorithms'''
    starter = bit_string()
    return starter.get_random(genome_length)


def population_maker():
    '''for population-based algorithms'''
    return [random_solution_maker() for i in xrange(ea_mu)]


def wrapped_make_EA(evals, fitness):
    '''Adapter design pattern'''
    return make_EA(make_initial_population=population_maker,
                   survival_selector=make_SUS(fitness=fitness, n=ea_mu),
                   parent_selector=make_SUS(fitness=fitness, n=ea_lam),
                   fitness=fitness)


def wrapped_make_SA(evals, fitness):
    '''Adapter design pattern'''
    return make_SA(evals=evals,
                   initial_solution_maker=random_solution_maker,
                   fitness=fitness)


def get_performance(fitness_function, search_maker, n=30, evals=10000):
    '''run search against fitness_function n times, allowing evals
    fitness evaluations per run. return a list corresponding to the
    fitness value of the best solution found per run'''
    search = search_maker(evals=evals, fitness=fitness_function)
    results = [search() for _ in xrange(n)]
    result_fits = [fitness_function(x) for x in results]
    return statistics(result_fits)


def fit_fit(fitness_function, makers, index):
    '''index is the index of the algorithm that is supposed to win'''
    performs = [get_performance(fitness_function, sa)
                for sa in makers]
    performs = [x['mean'] for x in performs]
    diffs = [x - performs[index]
             for x in performs[:index] + performs[index + 1:]]
    diffs = [x + 20 for x in diffs]
    return min(diffs)


def main():
    fits = initial_fits()
    makers = [wrapped_make_SA, wrapped_make_EA]
    for fit in fits:
        print "starting a fitness eval"
        fit.fitness = fit_fit(fit, makers, 0)
        print "ending a fitness eval"
    print fits


# if __name__ == "__main__":
#     main()

import cProfile
cProfile.run('main()', 'profiling.prof')
