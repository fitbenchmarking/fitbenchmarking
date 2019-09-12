"""
Main module of the tool, this holds the master function that calls
lower level functions to fit and benchmark a set of problems
for a certain fitting software.
"""

# Copyright &copy; 2016 ISIS Rutherford Appleton Laboratory, NScD
# Oak Ridge National Laboratory & European Spallation Source
#
# This file is part of Mantid.
# Mantid is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Mantid is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# File change history is stored at:
# <https://github.com/mantidproject/fitbenchmarking>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>

from __future__ import (absolute_import, division, print_function)

import os
import json
from utils.logging_setup import logger

from parsing import parse
from utils import create_dirs, misc
from fitbenchmark_one_problem import fitbm_one_prob


def do_fitting_benchmark(group_name, software_options, data_dir,
                         use_errors=True, results_dir=None):
    """
    This function does the fitting benchmarking for a
    specified group of problems.

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

    prob_results = do_benchmarking(user_input, problem_group)

    return prob_results, results_dir


def do_benchmarking(user_input, problem_group):
    """
    Loops through software and benchmarks each problem within the problem
    group.

    @param user_input :: all the information specified by the user
    @param problem_group :: list blocks of paths to problem files in the group
                            e.g. [['NIST/low_difficulty/file1.dat',
                                   'NIST/low_difficulty/file2.dat',
                                   ...],
                                  ['NIST/average_difficulty/file1.dat',
                                   'NIST/average_difficulty/file2.dat',
                                   ...],
                                  ...]

    @returns :: array of result objects, per problem per user_input
    """

    if not isinstance(user_input, list):
        list_block_results = [do_fitbm_block(user_input, p) for p in problem_group]

    else:
        list_block_results = [do_fitbm_block(u, p)
                              for u in user_input
                              for p in problem_group]

    # Flatten blocks into single list
    list_prob_results = [result for block in list_block_results for result in block]

    return list_prob_results


def do_fitbm_block(user_input, problem_block):
    """
    Fit benchmark a block of problems.

    @param user_input :: all the information specified by the user
    @param problem_block :: array of paths to problem files in the block

    @returns :: array of result objects
    """

    results_per_problem = []
    for prob_file in problem_block:
        problem = parse.parse_problem_file(prob_file)
        results_prob = fitbm_one_prob(user_input, problem)
        results_per_problem.extend(results_prob)

    return results_per_problem
