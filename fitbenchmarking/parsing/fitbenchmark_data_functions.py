"""
Functions that prepare the function specified in FitBenchmark problem definition file into
the right format for SciPy.
"""


from __future__ import absolute_import, division, print_function

import re

import numpy as np

import mantid.simpleapi as msapi
from fitbenchmarking.utils.logging_setup import logger


def gen_func_obj(function_name, params_set):
    """
    Generates a mantid function object.

    @param function_name :: the name of the function to be generated
    @params_set :: set of parameters per function extracted from the
        problem definition file

    @returns :: mantid function object that can be called in python
    """
    params_set = (params_set.split(', ties'))[0]

    exec "function_object = msapi." + function_name + "(" + params_set + ")"

    return function_object


def set_ties(function_object, ties):
    """
    Sets the ties for a function/composite function object.

    @param function_object :: mantid function object
    @param ties :: array of strings containing the ties

    @returns :: mantid function object with ties
    """

    for idx, ties_per_func in enumerate(ties):
        for tie in ties_per_func:
            """
            param_str is a string of the parameter name in the mantid format
            For a Mantid Composite Function, a formatted parameter name would
            start with the function number and end with the parameter name.
            For instance, f0.A would refer to a parameter A of the first
            function is a Composite Function.
            """
            param_str = 'f' + str(idx) + '.' + (tie.split("'"))[0]
            function_object.fix(param_str)

    return function_object

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
        params += get_fitbenchmark_params(param_set)
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


def get_fitbenchmark_params(param_set):
    """
    Get the FitBenchmark param values from the param_set string array which
    may contain multiple parameter sets (for each function).
    """
    params_str = param_set.split('ties=', 1)[0]
    params_list = (ps
                   for ps in params_str.split(',')
                   if ps.strip() != '')

    param_strs = (p.split('=') for p in params_list)
    params = [float(p[1].strip())
              for p in param_strs
              if p[0].strip() != 'BinWidth']

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
