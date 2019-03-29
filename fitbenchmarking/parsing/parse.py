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

from parsing import parse_nist_data, parse_fitbenchmark_data
from utils.logging_setup import logger


def parse_problem_file(prob_file):
    """
    Helper function that does the parsing of a specified problem file.
    This method needs group_name to inform how the prob_file should be
    passed.
    @param group_name :: name of the group of problems
    @param prob_file :: path to the problem file
    @returns :: problem object with fitting information
    """
    fline = open(prob_file).readline().rstrip()
    if "NIST" in fline:
        prob = parse_nist_data.load_file(prob_file)
        prob.type = 'NIST'
    elif "#" in fline:
        prob = parse_fitbenchmark_data.load_file(prob_file)
        prob.type = 'FitBenchmark'
    else:
        raise RuntimeError("Data type supplied currently not supported")

    logger.info("* Testing fitting of problem {0}".format(prob.name))

    return prob
