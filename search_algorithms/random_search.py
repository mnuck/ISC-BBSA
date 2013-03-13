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


def make_random_search_solver(evals, initial_solution_maker,
                              fitness=lambda x: x.fitness,
                              **kwargs):
    def solver():
        result = initial_solution_maker()
        for _ in xrange(evals):
            candidate = result.get_random()
            if fitness(candidate) > fitness(result):
                result = candidate
        return result
    return solver
