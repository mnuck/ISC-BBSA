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


def make_initial_state():
    return {'evals': 0, 'max_evals': 1000}


def default_terminator(state):
    return state['evals'] > state['max_evals']


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
                child_maker=None,
                terminate=default_terminator,
                fitness=lambda x: x):
    if child_maker is None:
        child_maker = make_default_child_maker()
    cycle = make_cycle(child_maker, parent_selector, survival_selector)

    def mu_lambda_ea():
        state = make_initial_state()
        population = make_initial_population()
        while not terminate(state):
            population, state = cycle(population, state)
        return population
    return mu_lambda_ea
