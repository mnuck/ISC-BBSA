#!/usr/bin/env python
#
# BBSA Auto-Benchmark

from math import sqrt
from random import choice
from time import time

from nk_landscape import fitness_nk_landscape


def statistics(s):
    '''min, max, mean, stddev'''
    result = {'min': min(s), 'max': max(s),
              'mean': sum(s) / float(len(s))}
    result.update({'stddev':
                        sqrt(sum((x - result['mean']) ** 2 for x in s) /
                             float(len(s) - 1))})
    return result


def gen_dude():
    return [choice([0, 1]) for i in xrange(20)]


def gen_dudes(x):
    return [gen_dude() for i in xrange(x)]


def time_it(dudes):
    f = fitness_nk_landscape()
    start = time()
    f.cuda_fitness(dudes)
    return time() - start


for exp in xrange(8):
    how_many = 10 ** exp
    dudes = gen_dudes(how_many)
    stats = statistics([time_it(dudes) for i in xrange(30)])
    print how_many, stats['mean'], stats['stddev']
