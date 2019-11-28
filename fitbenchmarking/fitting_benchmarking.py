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


def fitbenchmark_group(group_name, options, data_dir):
    """
    Gather the user input and list of paths. Call benchmarking on these.

    :param group_name: is the name (label) for a group. E.g. the name for
                       the group of problems in "NIST/low_difficulty" may be
                       picked to be NIST_low_difficulty
    :type group_name: str
    :param options: dictionary containing software used in fitting
                    the problem, list of minimizers and location of
                    json file contain minimizers
    :type options: fitbenchmarking.utils.options.Options
    :param data_dir: full path of a directory that holds a group of problem
                     definition files
    :type date_dir: str

    :returns: tuple(prob_results, results_dir) array of fitting results for
              the problem group and the path to the results directory
    :rtype: (list of FittingResult, str)
    """

    # Create results directory
    results_dir = create_dirs.results(options.results_dir)
    group_results_dir = create_dirs.group_results(results_dir, group_name)

    # Extract problem definitions
    problem_group = misc.get_problem_files(data_dir)

    results = []
    for p in problem_group:
        parsed_problem = parse_problem_file(p)
        problem_results = fitbm_one_prob(problem=parsed_problem,
                                         options=options,
                                         directory=group_results_dir)

        # Convert from list of dict to list of list and store
        for r in problem_results:
            tmp_result = []
            for s in options.software:
                tmp_result.extend(r[s])
            results.append(tmp_result)

    return results
