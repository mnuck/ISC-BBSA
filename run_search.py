#!/usr/bin/env python
#
# BBSA Auto-benchmark

max_evals = 20

from search_algorithms.climb_hill import climb_hill
from search_algorithms.random_search import random_search
from fitness_functions.DTRAP import fitness_DTRAP
from fitness_functions.AllOnes import fitness_AllOnes
from representations.bit_string import bit_string

search = climb_hill
fitness = fitness_AllOnes
individual = bit_string

import logging
logformat = '%(asctime)s:%(levelname)s:%(message)s'
loglevel = logging.INFO
logging.basicConfig(format=logformat, level=loglevel)

def run_search():
    current = individual().get_random(length=5)
    result = {'best'  : current,
              'evals' : [{'count':1,
                          'current_best':current}]}
    
    for evals in xrange(1,max_evals):
        current = search(current, fitness=fitness)
        if fitness(current) > fitness(result['best']):
            logging.info("%i %i %s" % (evals, fitness(current), current))
            result['best'] = current
            result['evals'].append({'count':evals,
                                    'current_best':result['best']})
    return result['best']

trapped = individual('00000')
result = list()
for i in xrange(3200):
    result.append(run_search() == trapped)
print len([x for x in result if not x])
