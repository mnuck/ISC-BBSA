#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random
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


def make_cycle(child_maker, parent_selector, survivor_selector):
    def cycle(population, state):
        parents = parent_selector(population)
        children = child_maker(parents)
        population.extend(children)
        state['evals'] += len(children)
        population = survivor_selector(population)
        return population, state
    return cycle


def make_default_child_maker(mutation_rate=0.5):
    crossover = make_default_crossover()
    mutator = make_mutator(mutation_rate)

    def child_maker(parents):
        children = list()
        while len(children) < len(parents):
            children.extend(crossover(*random.sample(parents, 2)))
        return [mutator(child) for child in children]
    return child_maker


def make_mutator(mutation_rate, mutation=lambda x: x.one_point_mutate()):
    def mutator(individual):
        if random.random() < mutation_rate:
            return mutation(individual)
        else:
            return individual
    return mutator


def make_default_crossover(crosser=lambda x, y: x.one_point_crossover(y)):
    def crossover(p1, p2):
        return crosser(p1, p2)
    return crossover


def make_solver(make_initial_population,
                survival_selector,
                parent_selector,
                evals=None,
                child_maker=None,
                make_initial_state=None,
                terminate=None,
                fitness=lambda x: x,
                **kwargs):
    if evals is None:
        evals = 10000
    if child_maker is None:
        child_maker = make_default_child_maker()
    if make_initial_state is None:
        make_initial_state = lambda: {'evals': 0, 'max_evals': evals}
    if terminate is None:
        terminate = lambda x: x['evals'] > x['max_evals']

    cycle = make_cycle(child_maker, parent_selector, survival_selector)

    def solver():
        state = make_initial_state()
        population = make_initial_population()
        while not terminate(state):
            population, state = cycle(population, state)
        return population
    return solver
