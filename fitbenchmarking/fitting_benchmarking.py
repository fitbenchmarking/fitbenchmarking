"""
Main module of the tool, this holds the master function that calls
lower level functions to fit and benchmark a set of problems
for a certain fitting software.
"""

from __future__ import (absolute_import, division, print_function)

import os
import json
from fitbenchmarking.utils.logging_setup import logger

from fitbenchmarking.parsing import parse
from fitbenchmarking.utils import create_dirs, misc
from fitbenchmarking.fitbenchmark_one_problem import fitbm_one_prob


def fitbenchmark_group(group_name, software_options, data_dir,
                       use_errors=True, results_dir=None):
    """
    Gather the user input and list of paths. Call benchmarking on these.

    @param group_name :: is the name (label) for a group. E.g. the name for the group of problems in
                         "NIST/low_difficulty" may be picked to be NIST_low_difficulty
    @param software_options :: dictionary containing software used in fitting the problem, list of minimizers and
                               location of json file contain minimizers
    @param data_dir :: full path of a directory that holds a group of problem definition files
    @param use_errors :: whether to use errors on the data or not
    @param results_dir :: directory in which to put the results. None
                          means results directory is created for you

    @returns :: array of fitting results for the problem group and
                the path to the results directory
    """

    logger.info("Loading minimizers from {0}".format(
        software_options['software']))
    minimizers, software = misc.get_minimizers(software_options)

    # create list of paths to all problem definitions in data_dir
    problem_group = misc.get_problem_files(data_dir)

    results_dir = create_dirs.results(results_dir)
    group_results_dir = create_dirs.group_results(results_dir, group_name)

    user_input = misc.save_user_input(software, minimizers, group_name,
                                      group_results_dir, use_errors)

    prob_results = _benchmark(user_input, problem_group)

    return prob_results, results_dir


def _benchmark(user_input, problem_group):
    """
    Loops through software and benchmarks each problem within the problem
    group.

    @param user_input :: all the information specified by the user
    @param problem_group :: list of paths to problem files in the group
                            e.g. ['NIST/low_difficulty/file1.dat',
                                  'NIST/low_difficulty/file2.dat',
                                  ...]

    @returns :: array of result objects, per problem per user_input
    """

    parsed_problems = [parse.parse_problem_file(p) for p in problem_group]

    if not isinstance(user_input, list):
        list_prob_results = [per_func
                             for p in parsed_problems
                             for per_func in fitbm_one_prob(user_input, p)]

    else:
        list_prob_results = [[fitbm_one_prob(u, p)
                              for u in user_input]
                             for p in parsed_problems]

        # reorganise loop structure from:
        # [[[val per minimizer] per function] per input] per problem]
        # to:
        # [[val per input per minimizer] per function per problem]
        list_prob_results = \
            [[list_prob_results[prob_idx][input_idx][func_idx][minim_idx]
              for input_idx in range(len(user_input))
              for minim_idx in range(len(list_prob_results[prob_idx][input_idx][func_idx]))]
             for prob_idx in range(len(parsed_problems))
             for func_idx in range(len(list_prob_results[prob_idx][0]))]

    return list_prob_results

