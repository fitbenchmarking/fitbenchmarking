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

    # create list with blocks of paths to all problem definitions in data_dir
    problem_group = misc.setup_fitting_problems(data_dir)

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
        list_prob_results = [fitbm_one_prob(user_input, p) for p in parsed_problems]

    else:
        list_prob_results = [fitbm_one_prob(u, p)
                             for u in user_input
                             for p in parsed_problems]

    # Flatten
    list_prob_results = [res
                         for tmp_list in list_prob_results
                         for res in tmp_list]

    return list_prob_results

