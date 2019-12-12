"""
Set up an rst table that contains the parameters and form of a given fit.
"""

from __future__ import (absolute_import, division, print_function)


def create(functions_str):
    """
    Creates an rst table of the function definition string used
    to fit the problem data. The table can be seen in the support
    pages.

    @param function_str :: mantid-formatted function definition str

    @returns :: rst table of the function string
    """

    functions = str(functions_str).split(';')

    for function in functions:
        names, params = generate_names_and_params(function)

    name_hdim, params_hdim = fit_details_table_hdims(names, params)
    header = generate_fit_det_header(name_hdim, params_hdim)
    body = generate_fit_det_body(names, params, name_hdim, params_hdim)
    tbl = header + body + '\n'

    return tbl


def generate_names_and_params(function):
    """
    Generates the function names and params.
    If string contains UserFunction then it means it is a nist problem.
    If it contains name it is a neutron problem.
    """
    names, params = [], []

    if 'UserFunction' in function:
        names, params = parse_dat_mantid_function_def(function)
    elif 'name=' in function:
        names, params = parse_txt_function_def(function, names, params)
    elif " | " in function:
        # Exception for nist scipy problems
        names, params = [function.split('|')[0]], [function.split('|')[1]]
    else:
        raise TypeError("Sorry, your type of function is not supported")

    return names, params


def parse_dat_mantid_function_def(function):
    """
    Helper function that parses the function definition of a NIST problem
    and returns the function name and parameters.

    @param function :: NIST function definition string

    @returns :: formatted function name and the final function
                parameters (after it has been fitted)
    """
    first_comma = function.find(',')
    second_comma = function.find(',', first_comma + 1)
    function_name = function[first_comma + 9:second_comma]
    function_parameters = function[second_comma + 1:]
    function_parameters = function_parameters.replace(',', ', ')

    return [function_name], [function_parameters]


def parse_txt_function_def(function, function_names, function_parameters):
    """
    Helper function that parses the function definition of a neutron problem
    and returns the function name and parameters.

    @param function :: neutron function definition string
    @param function_names :: array of names of the problem
    @param function_parameters :: array of the parameters of the problem

    @returns :: new array with appended function name and array
                with appended corresponding parameters
    """
    first_comma = function.find(',')
    if first_comma != -1:
        function_names.append(function[5:first_comma])
        function_parameters.append(function[first_comma + 1:])
    else:
        function_names.append(function[5:])
        function_parameters.append('None')

    function_parameters[-1] = function_parameters[-1].replace(',', ', ')

    return function_names, function_parameters


def fit_details_table_hdims(function_names, function_parameters):
    """
    Helper function that resolves the header dimensions of the fit details
    table present in the rst visual display page.

    @param function_names :: array of names of the problem
    @param function_parameters :: array of the parameters of the problem

    @returns :: dimensions of the name and params columns (int)
    """

    name_hdim = max(len(name) for name in function_names)
    params_hdim = max(len(parameter) for parameter in function_parameters)

    if name_hdim < 4:
        name_hdim = 4
    if params_hdim < 10:
        params_hdim = 10

    return name_hdim, params_hdim


def generate_fit_det_header(name_dim, params_dim):
    """
    Generates header of table containing the fit details in rst.

    @param name_dim :: the dimensions of the name column
    @param params_dim :: the dimensions of the parameters column

    @returns :: the header of the fit details table
    """

    header = ''
    header += '+-' + '-' * name_dim + '-+-' + '-' * params_dim + '-+\n'
    header += ('| ' + 'Form' + ' ' * (name_dim - 4) + ' ' +
               '| ' + 'Parameters' + ' ' * (params_dim - 10) + ' |\n')
    header += '+=' + '=' * name_dim + '=+=' + '=' * params_dim + '=+\n'

    return header


def generate_fit_det_body(names, params, name_dim, params_dim):
    """
    Generates the body of table containing fit details in rst.

    @param names :: array of strings containing the function names
    @param params :: array of strings that contain the parameters
                     of the functions used in fitting
    @param name_dim :: the dimensions of the name column
    @param params_dim :: the dimensions of the parameters column

    @returns :: body of the fit details table
    """

    body = ''
    for idx in range(0, len(names)):

        body += ('| ' + names[idx] +
                 ' ' * (name_dim - len(names[idx])) + ' ' +
                 '| ' + params[idx] +
                 ' ' * (params_dim - len(params[idx])) + ' |\n')
        body += '+-' + '-' * name_dim + '-+-' + '-' * params_dim + '-+\n'

    return body
