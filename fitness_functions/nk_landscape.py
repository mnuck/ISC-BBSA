#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random
from itertools import product
from copy import deepcopy


class fitness_nk_landscape(object):
    def __init__(self, n=8, k=1):
        self.n = n
        self.k = k
        self.neighborses = list()
        self.subfuncs = list()

        r = range(n)
        for i in xrange(n):
            # i, and k neighbors that are not i
            neighbors = [i] + random.sample(r[:i] + r[i + 1:], k)
            self.neighborses.append(tuple(neighbors))

        for neighbors in self.neighborses:
            subfunc = dict()
            for key in product(*([xrange(2)] * len(neighbors))):
                subfunc[key] = random.random()
            self.subfuncs.append(subfunc)

    def __str__(self):
        result = ""
        for (i, ns, fs) in zip(xrange(self.n),
                               self.neighborses,
                               self.subfuncs):
            result += "position %i with neighbors %s\n" % (i, ns)
            for (k, v) in fs.items():
                result += "  %s -> %s\n" % (k, v)
        return result

    def __repr__(self):
        return self.__str__()

    def __call__(self, individual):
        result = 0
        for neighbors, subfunc in zip(self.neighborses, self.subfuncs):
            key = tuple(individual[i] for i in neighbors)
            result += subfunc[key]
        return result

    def one_point_mutate_neighbors(self):
        child = fitness_nk_landscape(n=self.n, k=self.k)
        child.neighborses = deepcopy(self.neighborses)
        child.subfuncs = deepcopy(self.subfuncs)
        i = random.randint(0, child.n - 1)
        r = range(child.n)
        child.neighborses[i] = [i] + random.sample(r[:i] + r[i + 1:], child.k)
        return child

    def one_point_mutate_subfuncs(self):
        child = fitness_nk_landscape(n=self.n, k=self.k)
        child.neighborses = deepcopy(self.neighborses)
        child.subfuncs = deepcopy(self.subfuncs)
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
        child1 = fitness_nk_landscape(n=self.n, k=self.k)
        child1.neighborses = deepcopy(self.neighborses)
        child1.subfuncs = deepcopy(self.subfuncs)
        child2 = fitness_nk_landscape(n=other.n, k=other.k)
        child2.neighborses = deepcopy(other.neighborses)
        child2.subfuncs = deepcopy(other.subfuncs)
        index = random.randint(0, len(self.neighborses))
        child1.neighborses[:index] = other.neighborses[:index]
        child2.neighborses[index:] = self.neighborses[index:]
        child1.subfuncs[:index] = other.subfuncs[:index]
        child2.subfuncs[index:] = self.subfuncs[index:]
        return child1, child2
