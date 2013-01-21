#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random

from representation import bit_string


def mu_lambda_ea(random_individual=default_individual_maker,
                 terminate=default_terminator,
                 survival_selector=default_survival_selector,
                 parent_selector=default_reproduction_selector,
                 mu=10, lam=5):
    state = dict()
    population = [random_individual() for x in xrange(mu)]
    while not terminate(state):
        population = cycle(population)
    return population

mu = 10
lam = 5
mutation_rate = 0.1

crossover = make_crossover()
mutator = make_mutator(mutation_rate)
selector = k_tournament
child_maker = make_child_maker(crossover, mutator, selector, lam)
survivor_picker = make_survivor_picker(truncate, mu)

cycle = make_cycle(child_maker, survivor_picker)
terminate = make_terminator()



def make_terminator():
    def terminator(state):
        pass
    return terminator


def make_cycle(child_maker, survivor_picker):
    def cycle(population):
        population.extend(child_maker(population))
        population = survivor_picker(population)
        return population
    return cycle


def make_child_maker(crossover, mutator, selector, n):
    def child_maker(population):
        children = list()
        while len(children) < n:
            children.extend(crossover(selector(population, n=2)))
        return [mutator(child) for child in children]
    return child_maker


def make_mutator(mutation_rate, mutation=lambda x: x.one_point_mutate()):
    def mutator(individual):
        if random.random() < mutation_rate:
            return mutation(individual)
        else:
            return individual
    return mutator


def make_crossover(crosser=lambda x, y: x.one_point_crossover(y)):
    def crossover(p1, p2):
        return crosser(p1, p2)
    return crossover


def make_survivor_picker(selector, n):
    def survivor_picker(population):
        return selector(population, n)
    return survivor_picker


def default_individual_maker():
    starter = bit_string()
    return starter.get_random(5)
