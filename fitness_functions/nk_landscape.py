#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random
from itertools import product, chain
from copy import deepcopy

cudaEnabled = False
try:
    import pycuda.autoinit
    import pycuda.driver as cuda
    import numpy
    from pycuda.compiler import SourceModule
    cudaEnabled = True
except:
    pass

# cudaEnabled = False   # to disable CUDA, uncomment this line


###############################################
### fitness_nk_landscape
###
### A fitness function that operates on bitstring individuals of length n
### Total fitness is the sum of n subfitnesses
### Each subfitness i depends on both the value of the bitstring at
### location i, as well as k other locations. Once created, can be called as
### a function, which will evaluate the given bitstring individual and return
### a non-negative fitness.
###
### Implemented as a functor
###
### Includes pyCUDA metaprogramming. If enabled, when a new
### fitness_nk_landscape is created, a new cubin (CUDA binary) will be
### be written and compiled. This takes a considerable amount of time, but
### results in a considerable speedup if you have a large number of
### individuals to evaluate. On the developer's machine, a cubin compile takes
### just under a second, after which the GPU can evaluate a million
### individuals per second.
###
###############################################
class fitness_nk_landscape(object):
    def __init__(self, n=8, k=1):
        "constructor"
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

        if cudaEnabled:
            self.cuda_fitness = generate_cuda_fitness(self.neighborses,
                                                      self.subfuncs)

    def clone(self, clone_cubin=False):
        "makes a new fitness_nk_landscape from an old one"
        child = fitness_nk_landscape(n=self.n, k=self.k)
        child.neighborses = deepcopy(self.neighborses)
        child.subfuncs = deepcopy(self.subfuncs)
        if clone_cubin:
            child.cuda_fitness = self.cuda_fitness
        return child

    def __str__(self):
        "a human-readable representation of this NK landscape"
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
        "evaluate the fitness of individual in this NK landscape"
        if individual in self.cache:
            return self.cache[individual]
        result = 0
        for neighbors, subfunc in zip(self.neighborses, self.subfuncs):
            key = tuple(individual[i] for i in neighbors)
            result += subfunc[key]
        self.cache[individual] = result
        return result

    def one_point_mutate_neighbors(self):
        "mutates just the identity of the k neighbors at a single location"
        child = self.clone()
        i = random.randint(0, child.n - 1)
        r = range(child.n)
        child.neighborses[i] = [i] + random.sample(r[:i] + r[i + 1:], child.k)
        if cudaEnabled:
            child.cuda_fitness = generate_cuda_fitness(child.neighborses,
                                                       child.subfuncs)
        return child

    def one_point_mutate_subfuncs(self):
        "mutates just the subfuncs at a single location"
        child = self.clone()
        i = random.randint(0, child.n - 1)
        for key in child.subfuncs[i]:
            child.subfuncs[i][key] += (random.random() - 0.5)
        if cudaEnabled:
            child.cuda_fitness = generate_cuda_fitness(child.neighborses,
                                                       child.subfuncs)
        return child

    def one_point_mutate(self):
        """mutates both the identity of the k neighbors as well as the
        subfuncs at a single index location"""
        child = self.clone()
        i = random.randint(0, child.n - 1)
        r = range(child.n)
        child.neighborses[i] = [i] + random.sample(r[:i] + r[i + 1:], child.k)
        for key in child.subfuncs[i]:
            child.subfuncs[i][key] += (random.random() - 0.5)
        if cudaEnabled:
            child.cuda_fitness = generate_cuda_fitness(child.neighborses,
                                                       child.subfuncs)
        return child

    def one_point_crossover(self, other):
        "performs one point crossover on self and other, returns 2 children"
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
        if cudaEnabled:
            child1.cuda_fitness = generate_cuda_fitness(child1.neighborses,
                                                        child1.subfuncs)
            child2.cuda_fitness = generate_cuda_fitness(child2.neighborses,
                                                        child2.subfuncs)
        return child1, child2

# --------------


def generate_source_code(neighborses, subfuncs):
    "writes CUDA C code that properly evaluates the NK landscape"
    header = """__global__ void f(char* X, float* fitnesses, int length) {
        int i = threadIdx.x + blockIdx.x * blockDim.x;
        if(i < length) {
            fitnesses[i] = 0.0;\n"""
    footer = "}}"
    inner_template = "X[i * %i + %i] == %%i"
    outer_template = "            if(%s) { fitnesses[i] += %%f; }\n"
    guts = ""
    size = len(neighborses)
    for neighbors, subfunc in zip(neighborses, subfuncs):
        step1 = " && ".join([inner_template % (size, n) for n in neighbors])
        for (key, value) in subfunc.items():
            step2 = outer_template % step1
            guts += step2 % (tuple(key) + (value,))
    return header + guts + footer


def generate_cuda_fitness(neighborses, subfuncs):
    "returns python function that wraps around the CUDA function"
    source_code = generate_source_code(neighborses, subfuncs)
    m = SourceModule(source_code)
    f = m.get_function('f')

    def cuda_fitness(individuals):
        "takes a list of individuals, returns a list of fitnesses"
        length = numpy.int32(len(individuals))
        dudes = numpy.array(list(chain(*individuals)), dtype=numpy.int8)
        fitnesses = numpy.zeros(length, dtype=numpy.float32)
        f(cuda.In(dudes), cuda.InOut(fitnesses), length,
          block=(256, 1, 1), grid=(1 + int(length / 256), 1))
        return fitnesses
    return cuda_fitness


__example_CUDA_source_code__ = """
__global__ void f(char* X, float* fitnesses, int length) {
        int i = threadIdx.x + blockIdx.x * blockDim.x;
        if(i < length) {
            fitnesses[i] = 0.0;
            if(X[i * 14 + 0] == 0 && X[i * 14 + 1] == 0) { fitnesses[i] += 0.3; }
            if(X[i * 14 + 0] == 0 && X[i * 14 + 1] == 1) { fitnesses[i] += 0.6; }
            if(X[i * 14 + 0] == 1 && X[i * 14 + 1] == 0) { fitnesses[i] += 4.1; }
            if(X[i * 14 + 0] == 1 && X[i * 14 + 1] == 1) { fitnesses[i] += 2.1; }
}}
"""
