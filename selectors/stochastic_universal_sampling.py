#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random


###############################################
### stochastic_universal_sampling
###
### @description select n members of a population, with probability of
###              selection proportional to fitness
###
### Precondition:  None
### Postcondition: None
###
### @param population: the population of eligibles
### @param n: the number of selectees required
### @param fitness: a function that quantifies
###                 the value of an individual
###
### @return a list of selectees of length n
###
### @limitations all fitnesses must be non-negative
###############################################
def stochastic_universal_sampling(population,
                                  fitness=lambda x: x.fitness,
                                  n=1):
    '''Selects members of a population'''
    total_fitness = sum([fitness(x) for x in population])
    spacing = total_fitness / float(n)
    choice_point = random.random() * spacing
    accumulated_fitness = 0
    result = list()
    for individual in population:
        accumulated_fitness += fitness(individual)
        while choice_point < accumulated_fitness:
            result.append(individual)
            choice_point += spacing
    return result

SUS = stochastic_universal_sampling


def fitness_proportional(population, fitness=lambda x: x.fitness):
    '''Selects a single member of a population'''
    return SUS(population, fitness, 1)[0]


def make_SUS(fitness=lambda x: x.fitness, n=1):
    def f(population):
        total_fitness = sum([fitness(x) for x in population])
        spacing = total_fitness / float(n)
        choice_point = random.random() * spacing
        accumulated_fitness = 0
        result = list()
        for individual in population:
            accumulated_fitness += fitness(individual)
            while choice_point < accumulated_fitness:
                result.append(individual)
                choice_point += spacing
        return result
    return f


def make_LR_wrapper(algorithm_maker,
                    fitness=lambda x: x.fitness, s=2.0, **kwargs):
    def rank_fit(population):
        lookup = [[fitness(x), i] for i, x in enumerate(population)]
        lookup.sort(key=lambda (a, b): a)
        mu = len(population)
        for i in xrange(mu):
            lookup[i][0] = ((2 - s) / mu) + \
                           ((2 * i * (s - 1)) / (mu * (mu - 1)))
        lookup.sort(key=lambda (a, b): b)
        lookup = [a for (a, b) in lookup]
        for (fit, individual) in zip(lookup, population):
            individual.__fitrank = fit
        return lambda x: x.__fitrank

    def f(population):
        fit = rank_fit(population)
        selector = algorithm_maker(fitness=fit, **kwargs)
        return selector(population)
    return f


def make_LR_SUS(fitness=lambda x: x.fitness, s=2.0, n=1):
    return make_LR_wrapper(make_SUS, fitness, s, n=n)


# def make_LR_SUS(fitness=lambda x: x.fitness, s=2.0, n=1):
#     def f(population):
#         lookup = [[fitness(x), i] for i, x in enumerate(population)]
#         lookup.sort(key=lambda (a, b): a)
#         mu = len(population)
#         for i in xrange(mu):
#             lookup[i][0] = ((2 - s) / mu) + \
#                            ((2 * i * (s - 1)) / (mu * (mu - 1)))
#         lookup.sort(key=lambda (a, b): b)
#         lookup = [a for (a, b) in lookup]
#         for (fit, individual) in zip(lookup, population):
#             individual.__fitrank = fit
#         fit = lambda x: x.__fitrank

#         total_fitness = 1.0
#         spacing = total_fitness / float(n)
#         choice_point = random.random() * spacing
#         accumulated_fitness = 0
#         result = list()
#         for individual in population:
#             accumulated_fitness += fit(individual)
#             while choice_point < accumulated_fitness:
#                 result.append(individual)
#                 choice_point += spacing
#         return result
#     return f
