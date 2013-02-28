#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random
from copy import copy

from bitarray import bitarray


def groupn(l, n):
    return zip(*(iter(l),) * n)


class fitness_DTRAP(object):
    def __init__(self, n=8, k=4, random_trap=False):
        "constructor"
        self.n = n
        self.k = k
        if not random_trap:
            self.lookup = range(k - 1, -1, -1) + [k]
        else:
            self.lookup = range(k + 1)
            random.shuffle(self.lookup)

    def clone(self):
        "makes a new DTRAP from an existing one"
        child = fitness_DTRAP(self.n, self.k)
        child.lookup = copy(self.lookup)
        return child

    def __str__(self):
        "a human-readable representation of this DTRAP"
        return str(self.lookup)

    def __repr__(self):
        return self.__str__()

    def __call__(self, individual):
        "evaluate the fitness of individual in this DTRAP"
        result = 0
        for trap in [bitarray(x) for x in groupn(individual, self.k)]:
            result += self.lookup[trap.count()]
        return result

    def one_point_mutate(self):
        "mutates the lookup table at a single location"
        child = self.clone()
        i = random.randint(0, child.k)
        child.lookup[i] = random.randint(0, child.k)
        return child

    def one_point_crossover(self, other):
        "performs one point crossover on self and other, returns 2 children"
        child1 = self.clone()
        child2 = other.clone()
        i = random.randint(0, self.k)
        child1.lookup[:i] = other.lookup[:i]
        child2.lookup[i:] = self.lookup[i:]
        return child1, child2


# data must implement .count(), which returns the number of ones
def fitness_DTRAP_old(individual, traplength=4,
                      data=lambda x: x.data, **kwargs):
    data = data(individual)
    result = 0
    trapcount = len(data) / traplength
    for trap in [data[i * traplength:(i + 1) * traplength]
                 for i in xrange(trapcount)]:
        count = trap.count()
        if count == traplength:
            result += traplength
        else:
            result += (traplength - count - 1)
    return result
