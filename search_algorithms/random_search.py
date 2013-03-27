#!/usr/bin/env python
#
# BBSA Auto-Benchmark

worst_ever = None


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
        global worst_ever
        print "starting a random search"
        result = initial_solution_maker()
        worst_ever = fitness(result)
        for _ in xrange(evals):
            candidate = result.get_random()
            if fitness(candidate) > fitness(result):
                result = candidate
            if fitness(candidate) < worst_ever:
                worst_ever = fitness(candidate)
        return result
    return solver
