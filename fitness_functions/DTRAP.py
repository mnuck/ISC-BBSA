#!/usr/bin/env python
#
# BBSA Auto-Benchmark

# data must implement .count(), which returns the number of ones
def fitness_DTRAP(individual, config ={'traplength' : 4, 
                                       'data'       : lambda x: x.data}):
    traplength = config['traplength']
    data = config['data'](individual)
    result = 0
    trapcount = len(data) / traplength
    for trap in [data[i*traplength:(i+1)*traplength]
                 for i in xrange(trapcount)]:
        count = trap.count()
        if count == traplength:
            result += traplength
        else:
            result += (traplength - count - 1)
    return result


