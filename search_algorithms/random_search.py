#!/usr/bin/env python
#
# BBSA Auto-Benchmark


###############################################
### random_search
###
### Randomly picks a different point in the search space
###
### Precondition:  none
### Postcondition: none
###
### @param current: must implement .get_random(),
###                 which must return a valid randomly generated individual
###
### @return a valid randomly generated individual
###############################################
def random_search(current, **kwargs):
    return current.get_random()
