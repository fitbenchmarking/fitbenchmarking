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
from sasmodels.core import load_model
import numpy as np
import re


def function_definitions(problem):
    """
    Transforms the prob.equation field into a function that can be
    understood by the mantid fitting software.

    @param problem :: object holding the problem information

    @returns :: a function definitions string with functions that
                mantid understands
    """

    problem_type = extract_problem_type(problem)

    if problem_type == 'SasView'.upper():
        model_name = (problem.equation.split('='))[1]
        kernel = load_model(model_name)
        function_defs = [[kernel, problem.starting_values, problem.equation]]
    elif problem_type == 'FitBenchmark'.upper():
        function_defs = problem.get_bumps_function()
    elif problem_type == 'NIST':
        function_defs = problem.get_function()
    else:
        raise NameError('Currently data types supported are FitBenchmark'
                        ' and nist, data type supplied was {}'.format(problem_type))

    return function_defs

def extract_problem_type(problem):
    """
    This function gets the problem object and figures out the problem type
    from the file name of the derived class

    @param problem :: object holding the problem information

    @returns :: the type of the problem in capital letters (e.g. NIST)
    """
    problem_file_name = problem.__class__.__module__
    problem_type = (problem_file_name.split('_')[1]).upper()

    return problem_type

def get_fin_function_def(final_param_values, problem, init_func_def):
    """

    @param result :: the result object created by Bumps fitting
    @param problem :: object holding the problem information
    @param init_func_def :: the initial function definition string

    @returns :: the final function definition string
    """

    problem_type = extract_problem_type(problem)

    if not 'name=' in init_func_def:
        final_param_values = list(final_param_values)
        params = init_func_def.split("|")[1]
        params = re.sub(r"[-+]?\d+.\d+", lambda m, rep=iter(final_param_values):
        str(round(next(rep), 3)), params)
        fin_function_def = init_func_def.split("|")[0] + " | " + params
    elif problem_type == 'SasView'.upper():
        param_names = [(param.split('='))[0] for param in problem.starting_values.split(',')]
        fin_function_def = problem.equation+','
        for name, value in zip(param_names, final_param_values):
            fin_function_def += name+ '=' + str(value) + ','
        fin_function_def = fin_function_def[:-1]
    else:
        final_param_values = list(final_param_values)
        all_attributes = re.findall(r"BinWidth=\d+[.]\d+", init_func_def)
        if len(all_attributes) != 0:
            init_func_def = [init_func_def.replace(attr, '+') for attr in all_attributes][0]
        fin_function_def = re.sub(r"[-+]?\d+[.]\d+", lambda m, rep=iter(final_param_values):
        str(round(next(rep), 3)), init_func_def)
        if len(all_attributes) != 0:
            fin_function_def = [fin_function_def.replace('+', attr) for attr in all_attributes]

    return fin_function_def


def get_init_function_def(function, problem):
    """
    Get the initial function definition string.

    @param function :: array containing the function information
    @param problem :: object holding the problem information

    @returns :: the initial function definition string
    """

    problem_type = extract_problem_type(problem)

    if not 'name=' in str(problem.equation):
        params = function[0].__code__.co_varnames[1:]
        param_string = ''
        for idx in range(len(function[1])):
            param_string += params[idx] + "= " + str(function[1][idx]) + ", "
        param_string = param_string[:-2]
        init_function_def = function[2] + " | " + param_string
    elif problem_type == 'SasView'.upper():
        init_function_def = problem.equation + ',' + problem.starting_values
        init_function_def = re.sub(r"(=)([-+]?\d+)([^.\d])", r"\g<1>\g<2>.0\g<3>", init_function_def)
    else:
        init_function_def = problem.equation
        init_function_def = re.sub(r",(\s+)?ties=[(][A-Za-z0-9=.,\s+]+[)]", '', init_function_def)
        init_function_def = re.sub(r"(=)([-+]?\d+)([^.\d])", r"\g<1>\g<2>.0\g<3>", init_function_def)

    return init_function_def

