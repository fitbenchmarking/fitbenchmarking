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
from utils.logging_setup import logger

def function_definitions(problem):
    """
    Processing the function definitions into an appropriate format for
    the software to understand.
    """
    problem_type = extract_problem_type(problem)

    if problem_type == 'NIST':
        from fitting.scipy.nist_data_functions import nist_func_definitions
        return nist_func_definitions(problem.equation,
                                     problem.starting_values)
    elif problem_type == 'FitBenchmark'.upper():
        """
        The following import is inserted here to allow fitbenchmarking 
        to run independently of mantid when solving NIST problems.
        FitBenchmark problems require mantid to generate problem function objects.
        As mantid is imported in fitbenchmark_data_function, the script should be 
        imported only in the case of solving FitBenchmark problems 
        """
        from fitting.scipy.fitbenchmark_data_functions import fitbenchmark_func_definitions
        return fitbenchmark_func_definitions(problem.equation)
    else:
        RuntimeError("Your problem type is not supported yet!")


def get_fin_function_def(init_function_def, func_callable, popt):
    """
    Produces the final function definition.

    @param init_function_def :: the initial function definition string
    @param func_callable :: callable function object
    @param popt :: array containing the values of the function variables
                   after the fit was performed

    @returns :: the final function definition string
    """
    if not 'name=' in str(func_callable):
        popt = list(popt)
        params = init_function_def.split("|")[1]
        params = re.sub(r"[-+]?\d+\.\d+", lambda m, rep=iter(popt):
                        str(round(next(rep), 3)), params)
        fin_function_def = init_function_def.split("|")[0] + " | " + params
    else:
        fin_function_def = str(func_callable)

    return fin_function_def


def get_init_function_def(function, mantid_definition):
    """
    Get the initial function definition string.

    @param function :: array containing the function information
    @param mantid_definition :: the string containing the function
                                definition in mantid format

    @returns :: the initial function definition string
    """
    if not 'name=' in str(function[0]):
        params = function[0].__code__.co_varnames[1:]
        param_string = ''
        for idx in range(len(function[1])):
            param_string += params[idx] + "= " + str(function[1][idx]) + ", "
        param_string = param_string[:-2]
        init_function_def = function[2] + " | " + param_string
    else:
        init_function_def = mantid_definition

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
