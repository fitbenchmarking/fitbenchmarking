"""
Parse the problem file depending on the type of problem.
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
import re
import numpy as np

from parsing import fitbm_problem
from fitting.mantid.externals import store_main_problem_data
from parsing import parse_nist_data, parse_fitbenchmark_data
from utils.logging_setup import logger


def parse_problem_file(prob_file):
    """
    Helper function that loads the problem file and populates the fitting
    problem.

    @param prob_file :: path to the problem file
    @returns :: problem object with fitting information
    """

    prob_type = determine_problem_type(prob_file)

    with open(prob_file) as probf:
        if prob_type == "NIST":
            logger.info("*** Loading NIST formatted problem definition "
                        "file {0} ***".format(os.path.basename(probf.name)))
            lines = probf.readlines()
            equation_text, data_pattern_text, starting_values, \
                residual_sum_sq = parse_nist_data.parse_line_by_line(lines)
            data_pattern = parse_nist_data.parse_data_pattern(data_pattern_text)
            parsed_eq = parse_nist_data.parse_equation(equation_text)
            problem = parse_nist_data.store_prob_details(probf, parsed_eq, starting_values, data_pattern, residual_sum_sq)
            problem.type = prob_type
        elif prob_type == "FitBenchmark":
            logger.info("*** Loading FitBenchmark formatted problem definition file {0} ***".
                        format(os.path.basename(probf.name)))
            entries = parse_fitbenchmark_data.get_fitbenchmark_data_problem_entries(probf)
            problem = fitbm_problem.FittingProblem()
            data_file = parse_fitbenchmark_data.get_data_file(
                prob_file, entries['input_file'])
            parse_fitbenchmark_data.store_main_problem_data(data_file, problem)
            parse_fitbenchmark_data.store_misc_problem_data(problem, entries)
            problem.type = prob_type

    logger.info("* Testing fitting of problem {0}".format(problem.name))

    return problem


def determine_problem_type(prob_file):
    """
    Helper function that determines the problem type from reading information
    from the problem file. Two problem type formats are supported:

      * "NIST": NIST Noninear Regression format:
        https://www.itl.nist.gov/div898/strd/nls/data/LINKS/DATA/Misra1a.dat

      * "FitBenchmark": Format native to FitBenchmarking

    @param prob_file :: path to the problem file
    @returns :: problem type: "NIST" or "FitBenchmark"
    """

    # In this first implementation determine the problem type by investigating
    # the first line of the problem file
    # Pulls out the first line of the problem file
    fline = open(prob_file).readline().rstrip()

    if "NIST" in fline:
        # Checking for NIST in first line and from that assume the format is:
        prob_type = "NIST"
    elif "#" in fline:
        # Checking for a comment in the first line and from assume the format is:
        prob_type = "FitBenchmark"
    else:
        raise RuntimeError("Data type supplied currently not supported")

    return prob_type
