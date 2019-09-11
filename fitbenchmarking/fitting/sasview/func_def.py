"""
Methods that prepare the function definitions to be used by the mantid
fitting software.
"""

from __future__ import (absolute_import, division, print_function)

from sasmodels.core import load_model
import re


def function_definitions(problem):
    """
    Transforms the prob.equation field into a function that can be
    understood by the SasView fitting software.

    @param problem :: object holding the problem information

    @returns :: a function definitions string with functions that
                SasView understands
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
    Get the final function definition string to be passed on when result pages are created.

    @param final_param_values :: an array containing the final parameter values
    @param problem :: object holding the problem information
    @param init_func_def :: the initial function definition string

    @returns :: the final function definition string
    """

    problem_type = extract_problem_type(problem)

    if not 'name=' in init_func_def:
        # Problem type is NIST
        final_param_values = list(final_param_values)
        params = init_func_def.split("|")[1]

        # Replace the initial paramter values with the final parameter values
        params = re.sub(r"[-+]?\d+.\d+", lambda m, rep=iter(final_param_values):
        str(round(next(rep), 3)), params)
        fin_function_def = init_func_def.split("|")[0] + " | " + params
    elif problem_type == 'SasView'.upper():
        # Problem type is SasView
        param_names = [(param.split('='))[0] for param in problem.starting_values.split(',')]
        fin_function_def = problem.equation+','
        for name, value in zip(param_names, final_param_values):
            fin_function_def += name+ '=' + str(value) + ','
        fin_function_def = fin_function_def[:-1]
    else:
        # Problem type is FitBenchmark
        final_param_values = list(final_param_values)

        # Remove any function attribute. BinWidth is the only attribute in all FitBenchmark (Mantid) problems.
        all_attributes = re.findall(r"BinWidth=\d+[.]\d+", init_func_def)
        if len(all_attributes) != 0:
            init_func_def = [init_func_def.replace(attr, '+') for attr in all_attributes][0]

        # Replace the initial paramter values with the final parameter values
        fin_function_def = re.sub(r"[-+]?\d+[.]\d+", lambda m, rep=iter(final_param_values):
        str(round(next(rep), 3)), init_func_def)

        # Add any removed function attribute. BinWidth is the only attribute in all FitBenchmark (Mantid) problems.
        if len(all_attributes) != 0:
            fin_function_def = [fin_function_def.replace('+', attr) for attr in all_attributes]

    return fin_function_def


def get_init_function_def(function, problem):
    """
    Get the initial function definition string to be passed on when result pages are created.

    @param function :: array containing the function information
    @param problem :: object holding the problem information

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

        # Remove ties from the function definiton string
        init_function_def = re.sub(r",(\s+)?ties=[(][A-Za-z0-9=.,\s+]+[)]", '', init_function_def)

        # Add a decimal place for each parameter without it
        init_function_def = re.sub(r"(=)([-+]?\d+)([^.\d])", r"\g<1>\g<2>.0\g<3>", init_function_def)

    return init_function_def

