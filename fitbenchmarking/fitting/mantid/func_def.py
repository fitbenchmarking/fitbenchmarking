"""
Methods that prepare the function definitions to be used by the mantid
fitting software.
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


def function_definitions(problem):
    """
    Transforms the prob.equation field into a function that can be
    understood by the mantid fitting software.

    @param problem :: object holding the problem information

    @returns :: a function definitions string with functions that
                mantid understands
    """

    problem_type = extract_problem_type(problem)

    if problem_type == 'NIST':
        # NIST data requires prior formatting
        nb_start_vals = len(problem.starting_values[0][1])
        function_defs = parse_nist_function_definitions(problem, nb_start_vals)
    elif problem_type == 'FitBenchmark'.upper():
        # Native FitBenchmark format does not require any processing
        function_defs = []
        function_defs.append(problem.equation)
    else:
        raise NameError('Currently data types supported are FitBenchmark'
                        ' and nist, data type supplied was {}'.format(problem_type))

    return function_defs


def parse_nist_function_definitions(problem, nb_start_vals):
    """
    Helper function that parses the NIST function definitions and
    transforms them into a mantid-readable format.

    @param prob :: object holding the problem information
    @param nb_start_vals :: the number of starting points for a given
                            function definition

    @returns :: the formatted function definition (str)
    """

    function_defs = []
    for start_idx in range(0, nb_start_vals):
        start_val_str = ''
        for param in problem.starting_values:
            start_val_str += ('{0}={1},'.format(param[0], param[1][start_idx]))
        # Eliminate trailing comma
        start_val_str = start_val_str[:-1]
        function_defs.append("name=UserFunction,Formula={0},{1}".
                             format(problem.equation, start_val_str))

    return function_defs

def extract_problem_type(problem):
    """
    This function gets the problem object and figures out the problem type
    from the file name that the class that it has been sent from

    @param problem :: object holding the problem information

    @returns :: the type of the problem in capital letters (e.g. NIST)
    """
    problem_file_name = problem.__class__.__module__
    problem_type = (problem_file_name.split('_')[1]).upper()

    return problem_type
