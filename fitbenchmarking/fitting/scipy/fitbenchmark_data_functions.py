"""
Methods that prepare the fitbenchmark problems function definitions to be
in the right format.
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

from fitting.mantid.externals import gen_func_obj, set_ties
from utils.logging_setup import logger


def fitbenchmark_func_definitions(functions_string):
    """
    Processing the fitbenchmark function definition into an appropriate format
    for the scipy software to use.

    @param function_string :: string defining the function in
                              mantid format

    @returns :: function definition array containing a mantid function
                callable and the function parameter values respectively
    """

    function_names = get_all_fitbenchmark_func_names(functions_string)
    function_params = get_all_fitbenchmark_func_params(functions_string)
    params, ties = get_fitbenchmark_initial_params_values(function_params)
    fit_function = None
    for name in function_names:
        fit_function = make_fitbenchmark_fit_function(name, fit_function)
    fit_function = set_ties(fit_function, ties)

    function_defs = [[fit_function, params]]

    return function_defs


def get_all_fitbenchmark_func_names(functions_string):
    """
    Helper function that parses the function_string and retrieves
    all the function names to be fitted.
    """

    functions = functions_string.split(';')
    function_names = []
    for function in functions:
        function_names = get_fitbenchmark_func_names(function, function_names)

    return function_names


def get_all_fitbenchmark_func_params(functions_string):
    """
    Helper function that parses the function_string and retrieves all
    the function parameters.
    """
    functions = functions_string.split(';')
    function_params = []
    for function in functions:
        function_params = get_fitbenchmark_func_params(function, function_params)

    return function_params


def get_fitbenchmark_func_names(function, function_names):
    """
    Helper function that retrieves the function name of only
    one function.
    """
    first_comma = function.find(',')
    if first_comma != -1:
        function_names.append(function[5:first_comma])
    else:
        function_names.append(function[5:])

    return function_names


def get_fitbenchmark_func_params(function, function_params):
    """
    Helper function that retrieves the function parameters of only
    one function.
    """
    first_comma = function.find(',')
    if first_comma != -1:
        function_params.append(function[first_comma + 1:])
    else:
        function_params.append('')

    function_params[-1] = function_params[-1].replace(',', ', ')

    return function_params


def get_fitbenchmark_initial_params_values(function_params):
    """
    Parses the function_params string and puts only the initial parameter
    values into a numpy array to be used by scipy.
    """
    params = []
    ties = []
    for param_set in function_params:
        get_fitbenchmark_params(param_set, params)
        get_fitbenchmark_ties(param_set, ties)

    params = np.array(params)
    return params, ties


def make_fitbenchmark_fit_function(func_name, fit_function):
    """
    Create the fitbenchmark fit function object that is used by scipy.
    """
    func_obj = gen_func_obj(func_name)
    if fit_function == None:
        fit_function = func_obj
    else:
        fit_function += func_obj

    return fit_function


def get_fitbenchmark_params(param_set, params):
    """
    Get the fitbenchmark param values from the param_set string array which
    may contain multiple parameter sets (for each function).
    """
    start = 0
    while True:
        comma = param_set.find(',', start)
        equal = param_set.find('=', start)
        if param_set[equal - 4:equal] == 'ties':
            break
        if comma == -1:
            parameter = float(param_set[equal + 1:])
        else:
            parameter = float(param_set[equal + 1:comma])
        params.append(parameter)
        if comma == -1:
            break
        start = comma + 1

    return params


def get_fitbenchmark_ties(param_set, ties):
    """
    Gets the fitbenchmark problem tie values.
    """
    start = param_set.find("ties=") + 5
    ties_per_function = []
    while True:
        if start == 4:
            break
        comma = param_set.find(',', start + 1)
        if comma != -1:
            tie = param_set[start + 1:comma]
        else:
            tie = param_set[start + 1:comma]
        ties_per_function.append(tie.replace("=", "': "))
        if comma == -1:
            break
        start = comma + 1

    ties.append(ties_per_function)

    return ties
