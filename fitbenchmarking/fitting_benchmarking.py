"""
Main module of the tool, this holds the master function that calls
lower level functions to fit and benchmark a set of problems
for a certain fitting software.
"""

from __future__ import (absolute_import, division, print_function)

from fitbenchmarking.utils.logging_setup import logger

from fitbenchmarking.parsing.parser_factory import parse_problem_file
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

    :param user_input: all the information specified by the user
    :type user_input: fitbenchmarking.utils.user_input.UserInput
    :param problem_group: Paths to problem files in the group
                          e.g. ['NIST/low_difficulty/file1.dat',
                                'NIST/low_difficulty/file2.dat',
                                ...]
    :type problem_group: list of string

    :returns: Result objects, per problem per user_input
    :rtype: list
    """
    if not isinstance(user_input, list):
        user_input = [user_input]

    results = []

    for p in problem_group:
        problem = parse_problem_file(p)

        problem_results = [fitbm_one_prob(u, problem)
                           for u in user_input]

        # reorganise loop structure from:
        # [[val per minimizer] per function] per input]
        # to:
        # [[val per input per minimizer] per function]
        reordered_results = [[problem_results[inp_idx][fun_idx][min_idx]
                              for inp_idx in range(len(user_input))
                              for min_idx in range(len(problem_results[inp_idx][fun_idx]))]
                             for fun_idx in range(len(problem_results[0]))]

        results.extend(reordered_results)

    return results
