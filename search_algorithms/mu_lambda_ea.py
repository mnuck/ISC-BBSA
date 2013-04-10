#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import json
import random
import logging

worst_ever = None


def analyze_nk_population(population, state):
    for p in population:
        print p.nkID, p.fitness
    best = max(population, key=lambda x: x.fitness)
    payload = {'bbsa': state['solverID'],
               'id': best.nkID,
               'fitness': best.fitness,
               'k': best.k,
               'performs': best.performs,
               'evals': state['evals']}
    if 'loser' in state:
      payload.update({'loser': state['loser']})

    logging.info(json.dumps(payload))


def make_cycle(child_maker, parent_selector, survivor_selector, noise,
               state_updater=lambda a, b: {}):
    def cycle(population, state):
        parents = parent_selector(population)
        children = child_maker(parents)
        population.extend(children)
        state['evals'] += len(children)
        population = survivor_selector(population)
        if noise:
            analyze_nk_population(population, state)
        state.update(state_updater(population, state))
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


def make_EA_solver(make_initial_population,
                   survival_selector,
                   parent_selector,
                   evals=10000,
                   child_maker=None,
                   make_initial_state=None,
                   terminate=lambda x: x['evals'] > x['max_evals'],
                   fitness=lambda x: x,
                   noise=False,
                   return_best=False,
                   **kwargs):
    if child_maker is None:
        child_maker = make_default_child_maker()
    if make_initial_state is None:
        make_initial_state = lambda: {'evals': 0, 'max_evals': evals}

    cycle = make_cycle(child_maker, parent_selector, survival_selector, noise)

    def solver():
        global worst_ever
        state = make_initial_state()
        population = make_initial_population()
        state['evals'] += len(population)
        worst_ever = min([fitness(x) for x in population])
        while not terminate(state):
            population, state = cycle(population, state)
            worst_now = min([fitness(x) for x in population])
            if worst_now < worst_ever:
                worst_ever = worst_now
        return max(population, key=fitness) if return_best else population
    return solver
