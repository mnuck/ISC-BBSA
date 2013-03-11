#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random
from copy import copy

from bitarray import bitarray


def groupn(l, n):
    return zip(*(iter(l),) * n)


class fitness_DTRAP(object):
    def __init__(self, k=4, random_trap=False, **kwargs):
        "constructor"
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


class fitness_DTRAP_Reece(object):
    def __init__(self, a=1, b=4, k=4, random_trap=False, **kwargs):
        "constructor"
        self.a = a
        self.b = b
        self.k = k

    def clone(self):
        "makes a new DTRAP from an existing one"
        return fitness_DTRAP_Reece(self.a, self.b, self.k)

    def __str__(self):
        "a human-readable representation of this DTRAP"
        return "a=%i, b=%i, k=%i" % (self.a, self.b, self.k)

    def __repr__(self):
        return self.__str__()

    def __call__(self, individual):
        "evaluate the fitness of individual in this DTRAP"
        result = 0
        for trap in [bitarray(x) for x in groupn(individual, self.k)]:
            result += self.__process_fitness(trap.count())
        return result

    def __process_fitness(self, u):
        "determine the fitness of this input in the context of this DTRAP"
        z = float(self.k - 1)
        if u <= z:
            result = self.a / z * (z - u)
        else:
            result = self.b / (self.k - z) * (u - z)
        return result

    def one_point_mutate(self):
        "mutates one thing, random.choice([a, b, k])"
        child = self.clone()
        x = int(round(random.gauss(0, 1)))
        results = [(child.a, child.b, child.k + x),
                   (child.a, child.b + x, child.k),
                   (child.a + x, child.b, child.k)]
        child.a, child.b, child.c = random.choice(results)
        return child

    def one_point_crossover(self, other):
        "performs one point crossover on self and other, returns 2 children"
        child1 = self.clone()
        child2 = other.clone()
        for attribute in ['a', 'b', 'k']:
            if random.random() < 0.5:
                child1.__setattr__(attribute, other.__getattribute__(attribute))
                child2.__setattr__(attribute, self.__getattribute__(attribute))
        return child1, child2
