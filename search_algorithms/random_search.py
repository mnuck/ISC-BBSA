#!/usr/bin/env python
#
# BBSA Auto-Benchmark


# Randomly picks a different point in the search space
def random_search(current, **kwargs):
    return current.get_random()
