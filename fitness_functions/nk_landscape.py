#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random
from itertools import product
from copy import deepcopy


header = """def fit(self, X):
    if X in self.cache:
        return self.cache[X]
    result = 0
"""
footer = """    self.cache[X] = result
    return result
"""
inner_template = "X[%i] == %%i"
outer_template = "    if %s: result += %%f\n"
and_string = " and "


def unroll_doodad(neighborses, subfuncs):
    guts = ""
    for neighbors, subfunc in zip(neighborses, subfuncs):
        step1 = and_string.join([inner_template % n for n in neighbors])
        for (key, value) in subfunc.items():
            step2 = outer_template % step1
            guts += step2 % (tuple(key) + (value,))

    source_code = header + guts + footer
    exec(compile(source_code, '<string>', 'exec'))
    return fit


class fitness_nk_landscape(object):
    def __init__(self, n=8, k=1):
        self.n = n
        self.k = k
        self.neighborses = list()
        self.subfuncs = list()
        self.cache = dict()

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

        self._f = unroll_doodad(self.neighborses, self.subfuncs)

    def clone(self):
        child = fitness_nk_landscape(n=self.n, k=self.k)
        child.neighborses = deepcopy(self.neighborses)
        child.subfuncs = deepcopy(self.subfuncs)
        return child

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
        return self._f(self, individual)
    # def __call__(self, individual):
    #     if individual in self.cache:
    #         return self.cache[individual]
    #     result = 0
    #     for neighbors, subfunc in zip(self.neighborses, self.subfuncs):
    #         key = tuple(individual[i] for i in neighbors)
    #         result += subfunc[key]
    #     self.cache[individual] = result
    #     return result

    def one_point_mutate_neighbors(self):
        child = self.clone()
        i = random.randint(0, child.n - 1)
        r = range(child.n)
        child.neighborses[i] = [i] + random.sample(r[:i] + r[i + 1:], child.k)
        return child

    def one_point_mutate_subfuncs(self):
        child = self.clone()
        i = random.randint(0, child.n - 1)
        for key in child.subfuncs[i]:
            child.subfuncs[i][key] += (random.random() - 0.5)
        return child

    def one_point_mutate(self):
        child = self.clone()
        i = random.randint(0, child.n - 1)
        r = range(child.n)
        child.neighborses[i] = [i] + random.sample(r[:i] + r[i + 1:], child.k)
        for key in child.subfuncs[i]:
            child.subfuncs[i][key] += (random.random() - 0.5)
        return child

    def one_point_crossover(self, other):
        if self.n != other.n:
            raise Exception("nk_landscape self.n = %i but other.n = %i!" %
                            (self.n, other.n))
        if self.k != other.k:
            raise Exception("nk_landscape self.k = %i but other.k = %i!" %
                            (self.k, other.k))
        child1 = self.clone()
        child2 = other.clone()
        i = random.randint(0, self.n - 1)
        child1.neighborses[:i] = other.neighborses[:i]
        child2.neighborses[i:] = self.neighborses[i:]
        child1.subfuncs[:i] = other.subfuncs[:i]
        child2.subfuncs[i:] = self.subfuncs[i:]
        return child1, child2


# def __call__(self, individual):
#     result = 0
#     for neighbors, subfunc in zip(self.neighborses, self.subfuncs):
#         key = tuple(individual[i] for i in neighbors)
#         result += subfunc[key]
#     return result


# def fitness(self, X):
#     result = 0
#     if X[0] == 0 and X[3] == 0: result += 0.0
#     if X[0] == 0 and X[3] == 1: result += 0.0
#     ...
#     return result


# neighborses = [(0, 3), (1, 0), (2, 7), (3, 7), (4, 8), (5, 2), (6, 7), (7, 1)]
# subfuncs = [{(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.0},
#             {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.0},
#             {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.0},
#             {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.0},
#             {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.0},
#             {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.0},
#             {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.0},
#             {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.0}]


# header = """__global__ void f(individual* X, double* fitnesses, int length) {
#     int i = threadIdx.x + blockIdx.x * blockDim.x;
#     if(i < length) {
#         fitnesses[i] = 0;
# """
# footer = """    }
# }
# """
# inner_template = "X[i][%i] == %%i"
# outer_template = "        if(%s) { fitnesses[i] += %%f; }\n"
# and_string = " && "




# f = unroll_doodad(neighborses, subfuncs)
# print f

