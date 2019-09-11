"""
Functions that prepare the function specified in FitBenchmark problem definition file into
the right format for SciPy.
"""

from __future__ import (absolute_import, division, print_function)

import numpy as np
import re
from fitting.mantid.externals import gen_func_obj, set_ties
from utils.logging_setup import logger


def fitbenchmark_func_definitions(functions_string):
    """
    Processing the function in a FitBenchmark problem definition into an appropriate format
    for the SciPy software.

    @param function_string :: string defining the function in
                              Mantid format

    @returns :: function definition array of one element which contains a callable Mantid function
                and the function parameter values
    """

    function_names = get_all_fitbenchmark_func_names(functions_string)
    function_params = get_all_fitbenchmark_func_params(functions_string)
    params, ties = get_fitbenchmark_initial_params_values(function_params)
    fit_function = None
    for name, params_set in zip(function_names, function_params):
        fit_function = make_fitbenchmark_fit_function(name, fit_function, params_set)
    fit_function = set_ties(fit_function, ties)

    function_def = [[fit_function, params]]

    return function_def


def get_fit_function_without_kwargs(fit_function, functions_string):
    """
    Create a function evaluation method that does not take any Keyword Arguments.
    This function is created from a Mantid function.

    @param fit_function :: a Mantid function
    @param functions_string :: a function definition string in the Mantid format

    @return :: an array containing a function evaluation method without Keyword Arguments
               and a list of initial parameter values
    """

    functions_string = re.sub(r",(\s+)?ties=[(][A-Za-z0-9=.,\s+]+[)]", '', functions_string)
    function_list = (functions_string).split(';')
    func_params_list = [((func.split(','))[1:]) for func in function_list]
    formatted_param_list = ['f' + str(func_params_list.index(func_params)) + '.' + param.strip() for func_params in
                            func_params_list for param in func_params]
    param_names = [(param.split('='))[0] for param in formatted_param_list]
    param_values = [(param.split('='))[1] for param in formatted_param_list if
                    not (param.split('='))[0].endswith('BinWidth')]
    new_param_names = [param.replace('.', '_') for param in param_names]

    param_names_string = ''
    for param in new_param_names:
        if not param.endswith('BinWidth'):
            param_names_string += ',' + param

    exec ('def bumps_function(x' + param_names_string + '):\n    return fit_function.__call__(x' + param_names_string + ')') in locals()

    return [[bumps_function, param_values]]


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
    values into a numpy array to be used by SciPy.
    """
    params = []
    ties = []
    for param_set in function_params:
        get_fitbenchmark_params(param_set, params)
        get_fitbenchmark_ties(param_set, ties)

    params = np.array(params)
    return params, ties


def make_fitbenchmark_fit_function(func_name, fit_function, params_set):
    """
    Create the FitBenchmark fit function object that can be used by SciPy.
    """
    func_obj = gen_func_obj(func_name, params_set)
    if fit_function == None:
        fit_function = func_obj
    else:
        fit_function += func_obj

    return fit_function


def get_fitbenchmark_params(param_set, params):
    """
    Get the FitBenchmark param values from the param_set string array which
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
    Gets the FitBenchmark problem tie values.
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
