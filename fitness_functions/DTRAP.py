#!/usr/bin/env python
#
# BBSA Auto-Benchmark

def fitness_DTRAP(individual, traplength=4):
    result = 0
    data = individual.data
    trapcount = len(data) / traplength
    for trap in [data[i*traplength:(i+1)*traplength]
                 for i in xrange(trapcount)]:
        count = trap.count()
        if count == traplength:
            result += traplength
        else:
            result += (traplength - count - 1)
    return result
