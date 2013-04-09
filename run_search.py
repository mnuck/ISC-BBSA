#!/usr/bin/env python
#
# BBSA Auto-benchmark

import logging
logformat = '%(asctime)s:%(levelname)s:%(message)s'
loglevel = logging.INFO
logging.basicConfig(filename='spewlog.log', format=logformat, level=loglevel)

import sys
import json
from urllib2 import urlopen
import beanstalkc

from utility import statistics

from representations.bit_string import bit_string

from fitness_functions import fitness_nk_landscape as nk

from search_algorithms.mu_lambda_ea import make_EA_solver as make_EA
from search_algorithms.simulated_annealing import make_SA_solver as make_SA
from search_algorithms.climb_hill import make_climb_hill_solver as make_CH
from search_algorithms.random_search import make_random_search_solver as make_RA

from selectors import make_LR_SUS

distributed = False
stalk = None

genome_length = 32
ea_mu = 100
ea_lam = 10

inner_runs = 5
inner_max_evals = 10000

fit_mu = 20
fit_lam = 5
outer_max_evals = 100

output_file = "ISC.txt"
if len(sys.argv) == 2:
    output_file = sys.argv[1]
print "using output file", output_file


def initial_fits():
    '''initial population of fitnesses'''
    return [nk(n=genome_length) for i in xrange(fit_mu)]


def random_solution_maker():
    '''for single-solution algorithms'''
    starter = bit_string()
    return starter.get_random(genome_length)


def population_maker():
    '''for population-based algorithms'''
    return [random_solution_maker() for i in xrange(ea_mu)]


def inner_wrapped_make_EA(evals, fitness):
    '''Adapter design pattern'''
    return make_EA(make_initial_population=population_maker,
                   survival_selector=make_LR_SUS(fitness=fitness, s=2.0, n=ea_mu),
                   parent_selector=make_LR_SUS(fitness=fitness, s=2.0, n=ea_lam),
                   fitness=fitness, return_best=True)
inner_wrapped_make_EA.name = 'EA'


def inner_wrapped_make_SA(evals, fitness):
    '''Adapter design pattern'''
    return make_SA(evals=evals,
                   initial_solution_maker=random_solution_maker,
                   fitness=fitness)
inner_wrapped_make_SA.name = 'SA'


def inner_wrapped_make_CH(evals, fitness):
    '''Adapter design pattern'''
    return make_CH(evals=evals,
                   initial_solution_maker=random_solution_maker,
                   fitness=fitness)
inner_wrapped_make_CH.name = 'CH'


def inner_wrapped_make_RA(evals, fitness):
    '''Adapter design pattern'''
    return make_RA(evals=evals,
                   initial_solution_maker=random_solution_maker,
                   fitness=fitness)
inner_wrapped_make_RA.name = 'RA'

maker_names = {'RA': inner_wrapped_make_RA,
               'CH': inner_wrapped_make_CH,
               'SA': inner_wrapped_make_SA,
               'EA': inner_wrapped_make_EA}


worst_ever = None


def normalize(s, key=lambda x: x):
    global worst_ever
    maxfit = max(s, key=key)
    # minfit = min(s, key=key)
    minfit = worst_ever
    scale = float(maxfit - minfit)
    result = [(x - minfit) / scale for x in s]
    return result


def normalize2(s, upper, lower):
    scale = float(upper - lower)
    return [(x - lower) / scale for x in s]


def get_performance(fitness_function, search_maker,
                    n=inner_runs, evals=inner_max_evals):
    '''run search against fitness_function n times, allowing evals
    fitness evaluations per run. return a list corresponding to the
    fitness value of the best solution found per run'''
    global worst_ever
    search = search_maker(evals=evals, fitness=fitness_function)
    # results = [search() for _ in xrange(n)]
    results = list()
    for _ in xrange(n):
        results.append(search())
        worst = search.func_globals['worst_ever']
        print "worst individual:", worst
        if worst_ever is None or worst < worst_ever:
            print "new worst ever!"
            worst_ever = worst

    result_fits = [fitness_function(x) for x in results]
    print "resulting fits:", result_fits
    return statistics(result_fits)


def fit_fit(fitness_function, makers, index):
    '''index is the index of the algorithm that is supposed to win'''
    global worst_ever
    if not hasattr(fitness_function, 'fitness'):
        worst_ever = None
        performs = [get_performance(fitness_function, sa)['mean']
                    for sa in makers]
        performs = normalize(performs)
        print "performs:", performs
        diffs = [performs[index] - x
                 for x in performs[:index] + performs[index + 1:]]
        print "diffs:", diffs
        fitness_function.fitness = min(diffs)
        print "fitness of this NK landscape:", fitness_function.fitness
    return fitness_function.fitness


def distributed_fit_fit(fitness_function, makers, index):
    global stalk
    global worst_ever
    if not hasattr(fitness_function, 'fitness'):
        worst_ever = None
        best_ever = None
        stow_nk_landscape(fitness_function)
        nkID = fitness_function.nkID
        jobID = 0
        # make a job request for each run that needs to happen
        for maker in makers:
            for _ in xrange(inner_runs):
                req = {'jobID': jobID,
                       'nkID':  nkID,
                       'bbsa':  maker.name}
                stalk.put(json.dumps(req))
                jobID += 1
        results = {name: list() for name in maker_names.keys()}
        for _ in makers:
            for _ in xrange(inner_runs):
                job = stalk.reserve()
                result = json.loads(job.body)
                job.delete()
                results[result['bbsa']].append(result['best'])
                if best_ever is None or result['best'] > best_ever:
                    best_ever = result['best']
                if worst_ever is None or result['worst'] < worst_ever:
                    worst_ever = result['worst']
        performs = list()
        for name in [x.name for x in makers]:
            performs.append(statistics(results[name])['mean'])

        kept = performs
        performs = normalize2(performs, best_ever, worst_ever)
        fitness_function.performs = performs
        print index, kept, performs
        diffs = [performs[index] - x
                 for x in performs[:index] + performs[index + 1:]]
        fitness_function.fitness = min(diffs)
        print "fitness of", fitness_function.nkID, fitness_function.fitness
    return fitness_function.fitness


def do_eet(index):
    global distributed
    makers = [inner_wrapped_make_EA,
              inner_wrapped_make_SA,
              inner_wrapped_make_CH,
              inner_wrapped_make_RA]
    if distributed:
        outer_fit = lambda x: distributed_fit_fit(x, makers, index)
    else:
        outer_fit = lambda x: fit_fit(x, makers, index)
    selector = lambda x: make_LR_SUS(fitness=outer_fit, s=2.0, n=x)
    outer_ea = make_EA(
        make_initial_population=initial_fits,
        survival_selector=selector(fit_mu),
        parent_selector=selector(fit_lam),
        make_initial_state=lambda: {'evals': 0,
                                    'max_evals': outer_max_evals,
                                    'solverID': makers[index].name},
        fitness=outer_fit,
        noise=True, return_best=True)
    return outer_ea()


def for_a_size(x):
    global genome_length
    genome_length = x
    EA_best = do_eet(0)
    SA_best = do_eet(1)
    CH_best = do_eet(2)
    RA_best = do_eet(3)

    f = open(output_file, 'a')
    f.write("-----------------------------------------\n")
    f.write("Best NK-Landscape for Simulated Annealing %i\n" % genome_length)
    f.write("Fitness: %f\n" % SA_best.fitness)
    f.write("%s\n" % SA_best)
    f.write("%s\n" % SA_best.neighborses)
    f.write("%s\n" % SA_best.subfuncs)

    f.write("-----------------------------------------\n")
    f.write("Best NK-Landscape for Mu Lambda EA %i\n" % genome_length)
    f.write("Fitness: %f\n" % EA_best.fitness)
    f.write("%s\n" % EA_best)
    f.write("%s\n" % EA_best.neighborses)
    f.write("%s\n" % EA_best.subfuncs)

    f.write("-----------------------------------------\n")
    f.write("Best NK-Landscape for Hill Climber %i\n" % genome_length)
    f.write("Fitness: %f\n" % CH_best.fitness)
    f.write("%s\n" % CH_best)
    f.write("%s\n" % CH_best.neighborses)
    f.write("%s\n" % CH_best.subfuncs)

    f.write("-----------------------------------------\n")
    f.write("Best NK-Landscape for Random Search %i\n" % genome_length)
    f.write("Fitness: %f\n" % RA_best.fitness)
    f.write("%s\n" % RA_best)
    f.write("%s\n" % RA_best.neighborses)
    f.write("%s\n" % RA_best.subfuncs)
    f.close()


def main():
    for_a_size(32)


def fetch_nk_landscape(nkID):
    template = 'http://r10mannr4.device.mst.edu:8080/bbsa/%i'
    f = urlopen(template % nkID)
    pickled = f.read()
    f.close()
    landscape = nk()
    landscape.loads(pickled)
    landscape.nkID = nkID
    return landscape


def stow_nk_landscape(landscape):
    template = "/usr/share/nginx/www/bbsa/%i"
    f = open(template % landscape.nkID, 'w')
    f.write(landscape.dumps())
    f.close()


def client():
    print "entering client mode!"
    stalk = beanstalkc.Connection(host="r10mannr4.device.mst.edu")
    stalk.watch('bbsa-job-requests')
    stalk.use('bbsa-job-results')
    landscapes = dict()
    while True:
        job = stalk.reserve()
        data = json.loads(job.body)
        print "processing job", data['jobID']
        if data['nkID'] not in landscapes:
            landscapes[data['nkID']] = fetch_nk_landscape(data['nkID'])
        fitness = landscapes[data['nkID']]
        search = maker_names[data['bbsa']](evals=inner_max_evals,
                                           fitness=fitness)
        data['best'] = fitness(search())
        data['worst'] = search.func_globals['worst_ever']
        print data
        stalk.put(json.dumps(data))
        job.delete()


if len(sys.argv) == 5:  # all cows eat grass
    client()

if len(sys.argv) == 6:  # good boys do fine always
    distributed = True
    stalk = beanstalkc.Connection(host="r10mannr4.device.mst.edu")
    stalk.watch('bbsa-job-requests')
    while stalk.stats_tube('bbsa-job-requests')['current-jobs-ready'] > 0:
        job = stalk.reserve()
        job.delete()
    stalk.ignore('bbsa-job-requests')
    stalk.watch('bbsa-job-results')
    while stalk.stats_tube('bbsa-job-results')['current-jobs-ready'] > 0:
        job = stalk.reserve()
        job.delete()
    stalk.use('bbsa-job-requests')
    main()


if __name__ == "__main__":
    main()


# import cProfile
# cProfile.run('main()', 'profiling.prof')
