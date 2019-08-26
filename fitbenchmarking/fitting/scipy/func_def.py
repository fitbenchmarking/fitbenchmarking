"""
Methods that prepare the fitting function definitions to be in the
right format.
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

import numpy as np
import re

def function_definitions(problem):
    """
    Processing the function definitions into an appropriate format for
    the software to understand.
    """
    problem_type = extract_problem_type(problem)

    if problem_type == 'NIST' or problem_type == 'FitBenchmark'.upper() or problem_type == 'SasView'.upper():
        return problem.get_function()
    else:
        RuntimeError("Your problem type is not supported yet!")


def get_fin_function_def(init_function_def, func_callable, popt):
    """
    Get the final function definition string to be passed on when result pages are created.

    @param init_function_def :: the initial function definition string
    @param func_callable :: callable function object
    @param popt :: array containing the values of the function variables
                   after the fit was performed

    @returns :: the final function definition string
    """
    if not 'name=' in init_function_def:
        # Problem type is NIST
        popt = list(popt)
        params = init_function_def.split("|")[1]

        # Replace the initial paramter values with the final parameter values
        params = re.sub(r"[-+]?\d+[.]\d+", lambda m, rep=iter(popt):
                        str(round(next(rep), 3)), params)
        fin_function_def = init_function_def.split("|")[0] + " | " + params
    else:
        # Problem type is FitBenchmark or SasView
        # Remove ties from the function definiton string
        all_attributes = re.findall(r",[\s+]?ties=[(][A-Za-z0-9=.,\s+]+[)]", init_function_def)
        if len(all_attributes) != 0:
            init_function_def = [init_function_def.replace(attr, '+') for attr in all_attributes][0]

        # Replace the initial paramter values with the final parameter values
        fin_function_def = re.sub(r"[-+]?\d+[.]\d+", lambda m, rep=iter(popt):
                        str(round(next(rep), 3)), init_function_def)

        # Add any previously removed ties to the function definiton string
        if len(all_attributes) != 0:
            fin_function_def = [fin_function_def.replace('+', attr) for attr in all_attributes]

    return fin_function_def


def get_init_function_def(function, problem):
    """
    Get the initial function definition string to be passed on when result pages are created.

    @param function :: array containing the function information
    @param equation :: the string containing the function
                                definition in mantid/sasview format

    @returns :: the initial function definition string
    """

    problem_type = extract_problem_type(problem)

    if not 'name=' in str(problem.equation):
        # Problem type is NIST
        params = function[0].__code__.co_varnames[1:]
        param_string = ''
        for idx in range(len(function[1])):
            param_string += params[idx] + "= " + str(function[1][idx]) + ", "
        param_string = param_string[:-2]
        init_function_def = function[2] + " | " + param_string
    elif problem_type == 'SasView'.upper():
        # Problem type is SasView
        init_function_def = problem.equation + ',' + problem.starting_values

        # Add a decimal place for each parameter without it
        init_function_def = re.sub(r"(=)([-+]?\d+)([^.\d])", r"\g<1>\g<2>.0\g<3>", init_function_def)
    else:
        # Problem type is FitBenchmark
        init_function_def = problem.equation

        # Add a decimal place for each parameter without it
        init_function_def = re.sub(r"(=)([-+]?\d+)([^.\d])", r"\g<1>\g<2>.0\g<3>", init_function_def)

    return init_function_def

def extract_problem_type(problem):
    """
    This function gets the problem object and figure out the problem type
    from the file name that the class that it has been sent from

    @param problem :: object holding the problem information

    @returns :: the type of the problem (e.g. NIST)
    """
    problem_file_name = problem.__class__.__module__
    problem_type = (problem_file_name.split('_')[1]).upper()

    return problem_type
