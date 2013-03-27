#!/usr/bin/env python
#
# BBSA Auto-benchmark

import logging
logformat = '%(asctime)s:%(levelname)s:%(message)s'
loglevel = logging.WARNING
logging.basicConfig(format=logformat, level=loglevel)

import sys

from utility import statistics

from representations.bit_string import bit_string

from fitness_functions import fitness_nk_landscape as nk

from search_algorithms.mu_lambda_ea import make_EA_solver as make_EA
from search_algorithms.simulated_annealing import make_SA_solver as make_SA
from search_algorithms.climb_hill import make_climb_hill_solver as make_CH
from search_algorithms.random_search import make_random_search_solver as make_RA

from selectors import make_LR_SUS


genome_length = 16
ea_mu = 100
ea_lam = 10

inner_runs = 2
inner_max_evals = 10000

fit_mu = 10
fit_lam = 3
outer_max_evals = 100

output_file = "the_winners.txt"
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


def inner_wrapped_make_SA(evals, fitness):
    '''Adapter design pattern'''
    return make_SA(evals=evals,
                   initial_solution_maker=random_solution_maker,
                   fitness=fitness)


def inner_wrapped_make_CH(evals, fitness):
    '''Adapter design pattern'''
    return make_CH(evals=evals,
                   initial_solution_maker=random_solution_maker,
                   fitness=fitness)


def inner_wrapped_make_RA(evals, fitness):
    '''Adapter design pattern'''
    return make_RA(evals=evals,
                   initial_solution_maker=random_solution_maker,
                   fitness=fitness)


worst_ever = None


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


def normalize(s, key=lambda x: x):
    global worst_ever
    maxfit = max(s, key=key)
    # minfit = min(s, key=key)
    minfit = worst_ever
    scale = float(maxfit - minfit)
    result = [(x - minfit) / scale for x in s]
    print "normalized fits:", result
    return result


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


def do_eet(index):
    makers = [inner_wrapped_make_SA,
              inner_wrapped_make_EA,
              inner_wrapped_make_CH,
              inner_wrapped_make_RA]
    outer_fit = lambda x: fit_fit(x, makers, index)
    selector = lambda x: make_LR_SUS(fitness=outer_fit, s=2.0, n=x)
    outer_ea = make_EA(
        make_initial_population=initial_fits,
        survival_selector=selector(fit_mu),
        parent_selector=selector(fit_lam),
        make_initial_state=lambda: {'evals': 0, 'max_evals': outer_max_evals},
        fitness=outer_fit,
        noise=True, return_best=True)
    return outer_ea()


def for_a_size(x):
    global genome_length
    genome_length = x
    SA_best = do_eet(0)
    EA_best = do_eet(1)
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
    for_a_size(16)
    for_a_size(32)
    for_a_size(128)


import cProfile
cProfile.run('main()', 'profiling.prof')


"""
position 0 with neighbors (0, 3)
  (0, 1) -> 0.841362295646
  (1, 0) -> 0.515198806587
  (0, 0) -> 0.761643960556
  (1, 1) -> 0.42002527554
position 1 with neighbors (1, 14)
  (0, 1) -> 0.34416592976
  (1, 0) -> 0.933224393317
  (0, 0) -> 0.972400162152
  (1, 1) -> 0.226885860476
position 2 with neighbors (2, 11)
  (0, 1) -> 0.745364975392
  (1, 0) -> 0.610119201016
  (0, 0) -> 0.923812584995
  (1, 1) -> 0.594434020168
position 3 with neighbors (3, 7)
  (0, 1) -> 0.146221412872
  (1, 0) -> 0.843026388217
  (0, 0) -> 0.161152741456
  (1, 1) -> 0.248779975202
position 4 with neighbors (4, 5)
  (0, 1) -> 0.874848697622
  (1, 0) -> 0.00891836140657
  (0, 0) -> 0.657516561739
  (1, 1) -> 0.740339846257
position 5 with neighbors (5, 10)
  (0, 1) -> 0.565686641301
  (1, 0) -> 0.713128950086
  (0, 0) -> 0.565450894066
  (1, 1) -> 0.555954475106
position 6 with neighbors (6, 9)
  (0, 1) -> 0.539579204795
  (1, 0) -> 0.70844571761
  (0, 0) -> 0.222616730008
  (1, 1) -> 0.8936565344
position 7 with neighbors (7, 10)
  (0, 1) -> 0.121703582511
  (1, 0) -> 0.851605335099
  (0, 0) -> 0.729312119452
  (1, 1) -> 0.750595603018
position 8 with neighbors [8, 7]
  (0, 1) -> 0.0267418130366
  (1, 0) -> -0.0501834546413
  (0, 0) -> 0.0529042232198
  (1, 1) -> -0.00160621685305
position 9 with neighbors (9, 5)
  (0, 1) -> 0.391169137986
  (1, 0) -> 0.0714662997908
  (0, 0) -> 0.991302260093
  (1, 1) -> 0.196349569996
position 10 with neighbors (10, 1)
  (0, 1) -> 0.252219082299
  (1, 0) -> 0.229735572638
  (0, 0) -> 0.633390410485
  (1, 1) -> 0.27696074748
position 11 with neighbors (11, 9)
  (0, 1) -> 0.0464375061593
  (1, 0) -> 0.741831385331
  (0, 0) -> 0.366605978358
  (1, 1) -> 0.0860632362641
position 12 with neighbors (12, 2)
  (0, 1) -> 0.608760085394
  (1, 0) -> 0.892430787778
  (0, 0) -> 0.767781511648
  (1, 1) -> 0.817651105943
position 13 with neighbors (13, 8)
  (0, 1) -> 0.473783822139
  (1, 0) -> 0.997926100582
  (0, 0) -> 0.340059810599
  (1, 1) -> 0.202261033783
position 14 with neighbors (14, 7)
  (0, 1) -> 0.109269579235
  (1, 0) -> 0.218809598835
  (0, 0) -> 0.162444686851
  (1, 1) -> 0.693682123042
position 15 with neighbors (15, 0)
  (0, 1) -> 0.104293557232
  (1, 0) -> 0.987311327552
  (0, 0) -> 0.672074466775
  (1, 1) -> 0.616573134163

[(0, 3), (1, 14), (2, 11), (3, 7), (4, 5), (5, 10), (6, 9), (7, 10), [8, 7], (9, 5), (10, 1), (11, 9), (12, 2), (13, 8), (14, 7), (15, 0)]
[{(0, 1): 0.8413622956459827, (1, 0): 0.5151988065869528, (0, 0): 0.7616439605555315, (1, 1): 0.42002527553973124}, {(0, 1): 0.3441659297601357, (1, 0): 0.9332243933169404, (0, 0): 0.9724001621515554, (1, 1): 0.2268858604763352}, {(0, 1): 0.745364975392401, (1, 0): 0.6101192010159588, (0, 0): 0.9238125849951159, (1, 1): 0.594434020167708}, {(0, 1): 0.14622141287219348, (1, 0): 0.8430263882170198, (0, 0): 0.16115274145580227, (1, 1): 0.2487799752021701}, {(0, 1): 0.8748486976224051, (1, 0): 0.008918361406568986, (0, 0): 0.6575165617390092, (1, 1): 0.7403398462571745}, {(0, 1): 0.5656866413014648, (1, 0): 0.7131289500859391, (0, 0): 0.5654508940655044, (1, 1): 0.555954475105702}, {(0, 1): 0.5395792047947418, (1, 0): 0.7084457176102903, (0, 0): 0.2226167300082218, (1, 1): 0.893656534400419}, {(0, 1): 0.12170358251104041, (1, 0): 0.851605335098976, (0, 0): 0.7293121194521089, (1, 1): 0.7505956030184414}, {(0, 1): 0.02674181303659262, (1, 0): -0.05018345464133611, (0, 0): 0.05290422321977217, (1, 1): -0.0016062168530506238}, {(0, 1): 0.3911691379863521, (1, 0): 0.0714662997907517, (0, 0): 0.9913022600928073, (1, 1): 0.19634956999601483}, {(0, 1): 0.25221908229919865, (1, 0): 0.22973557263801014, (0, 0): 0.6333904104847119, (1, 1): 0.2769607474804977}, {(0, 1): 0.04643750615932285, (1, 0): 0.7418313853313636, (0, 0): 0.36660597835790887, (1, 1): 0.08606323626407952}, {(0, 1): 0.6087600853939525, (1, 0): 0.8924307877779734, (0, 0): 0.7677815116482604, (1, 1): 0.8176511059427286}, {(0, 1): 0.47378382213942305, (1, 0): 0.9979261005824099, (0, 0): 0.3400598105986907, (1, 1): 0.20226103378320293}, {(0, 1): 0.10926957923463476, (1, 0): 0.2188095988345815, (0, 0): 0.16244468685050395, (1, 1): 0.6936821230417878}, {(0, 1): 0.10429355723186251, (1, 0): 0.9873113275524547, (0, 0): 0.6720744667753683, (1, 1): 0.6165731341632406}]
"""
