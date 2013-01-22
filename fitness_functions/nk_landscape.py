#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random
from itertools import product
from copy import deepcopy


class fitness_nk_landscape(object):
    def __init__(self, n=8, k=1):
        k += 1  # because I'm my own neighbor
        self.n = n
        self.k = k
        self.neighborses = list()
        self.subfuncs = list()

        for i in xrange(n):
            # modify this to pick different neighbors
            neighbors = list()
            for j in xrange(i, min(n, i + k)):
                    neighbors.append(j)
            self.neighborses.append(tuple(neighbors))

        for neighbors in self.neighborses:
            subfunc = dict()
            for key in product(*([xrange(2)] * len(neighbors))):
                subfunc[key] = random.random()
            self.subfuncs.append(subfunc)

    def __call__(self, individual):
        result = 0
        for neighbors, subfunc in zip(self.neighborses, self.subfuncs):
            key = tuple(individual[i] for i in neighbors)
            result += subfunc[key]
        return result

    def one_point_mutate_neighbors(self):
        child = deepcopy(self)
        neighbors = random.choice(child.neighborses)
        index = random.randint(0, len(neighbors))
        neighbors[index] = random.randomint(0, self.n)
        return child

    def one_point_mutate_subfuncs(self):
        child = deepcopy(self)
        index = random.randint(0, len(child.subfuncs))
        key = random.choice(child.subfuncs[index].keys())
        child.subfuncs[index][key] += (random.random() - 0.5)
        return child

    def one_point_mutate(self):
        return self.one_point_mutate_subfuncs()

    def one_point_crossover(self, other):
        if self.n != other.n:
            raise Exception("nk_landscape self.n = %i but other.n = %i!" %
                            (self.n, other.n))
        if self.k != other.k:
            raise Exception("nk_landscape self.k = %i but other.k = %i!" %
                            (self.k, other.k))
        self._check_compatability(other)
        child1, child2 = deepcopy(self), deepcopy(other)
        index = random.randint(0, len(self.neighborses))
        child1.neighborses[:index] = other.neighborses[:index]
        child2.neighborses[index:] = self.neighborses[index:]
        child1.subfuncs[:index] = other.subfuncs[:index]
        child2.subfuncs[index:] = self.subfuncs[index:]
        return child1, child2
