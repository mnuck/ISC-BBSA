#!/usr/bin/env python
#
# BBSA Auto-benchmark

max_evals = 1000
length = 8

from search_algorithms import random_search

from fitness_functions import fitness_nk_landscape

from representations.bit_string import bit_string

search = random_search
fitness = fitness_nk_landscape(n=length)
individual = bit_string

import logging
logformat = '%(asctime)s:%(levelname)s:%(message)s'
loglevel = logging.INFO
logging.basicConfig(format=logformat, level=loglevel)


def run_search():
    current = individual().get_random(length=length)
    result = {'best': current,
              'evals': [{'count': 1,
                          'current_best': current}]}

    for evals in xrange(1, max_evals):
        current = search(current, fitness=fitness)
        if fitness(current) > fitness(result['best']):
            logging.info("%i %.2f %s" % (evals, fitness(current), current))
            result['best'] = current
            result['evals'].append({'count': evals,
                                    'current_best': result['best']})
    logging.info("----------------")
    return result['best']

result = list()
for i in xrange(10):
    result.append(run_search())
