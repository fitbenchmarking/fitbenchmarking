
"""
Main module of the tool, this holds the master function that calls
a bunch of lower level functions to fit and benchmark a set of problems
and for a certain fitting algorithm.
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

from utils.logging_setup import logger
from parsing import parse
from utils import create_dirs, setup_problem_groups
from fitbenchmark_one_problem import fitbm_one_problem


def do_fitting_benchmark(algorithm, data_dir, minimizers=None, use_errors=True,
                         results_dir=None):
    """
    High level function that does the fitting benchmarking for a
    specified group of problems.

    @param data_dir :: directory that holds the problem group data
    @param minimizers :: array of minimizers used in fitting
    @param use_errors :: whether to use errors on the data or not
    @param results_dir :: directory in which to put the results

    @returns :: array of fitting results for the problem group and
                the path to the results directory
    """

    results_dir = create_dirs.results(results_dir)
    problem_groups = setup_problem_groups.setup(algorithm, data_dir)

    prob_results = None
    for group_name in problem_groups:
        group_results_dir = create_dirs.group_results(results_dir, group_name)
        prob_results = \
        [do_fitting_benchmark_group(algorithm, minimizers, group_name, block,
                                    use_errors, group_results_dir)
         for block in problem_groups[group_name]]

    return prob_results, results_dir


def do_fitting_benchmark_group(algorithm, minimizers, group_name, problem_block,
                               use_errors, results_dir):
    """
    Fit benchmark a specific group of problems.

    @param group_name :: name of the group of problems
    @param results_dir :: result directory for the problem group
    @param problem_block :: array of paths to problem files in the group
    @param minimizers :: array of minimizers used in fitting
    @param use_errors :: whether to use errors or not

    @returns :: array of result objects, per problem
    """

    results_per_problem = []
    for prob_file in problem_block:
        prob = parse.parse_problem_file(group_name, prob_file)
        results_prob = \
        fitbm_one_problem(algorithm, prob, minimizers, use_errors, results_dir)
        results_per_problem.extend(results_prob)

    return results_per_problem
