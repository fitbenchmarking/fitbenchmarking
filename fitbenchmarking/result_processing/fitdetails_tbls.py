"""
Set up an rst table that contains the parameters and form of a given fit.
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


def create(functions_str):
    """
    Creates an rst table of the function definition string used
    to fit the problem data. The table can be seen in the support
    pages.

    @param function_str :: mantid-formatted function definition str

    @returns :: rst table of the function string
    """
    functions = functions_str.split(';')
    names, params = [], []

    for function in functions:
        # If string contains UserFunction then it means it is a nist problem
        # Otherwise it is a neutron problem
        if 'UserFunction' in function:
            names, params = parse_nist_function_def(function)
        else:
            names, params = parse_neutron_function_def(function, names, params)

    name_hdim, params_hdim = fit_details_table_hdims(names, params)
    header = generate_fit_det_header(name_hdim, params_hdim)
    body = generate_fit_det_body(names, params, name_hdim, params_hdim)
    tbl = header + body + '\n'

    return tbl


def parse_nist_function_def(function):
    """
    Helper function that parses the function definition of a NIST problem
    and returns the function name and parameters.

    @param function :: NIST function definition string

    @returns :: formatted function name and the final function
                parameters (after it has been fitted)
    """
    first_comma = function.find(',')
    second_comma = function.find(',', first_comma + 1)
    function_name = function[first_comma+9:second_comma]
    function_parameters = function[second_comma+1:]
    function_parameters = function_parameters.replace(',', ', ')

    return [function_name], [function_parameters]


def parse_neutron_function_def(function, function_names, function_parameters):
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
        function_parameters.append(function[first_comma+1:])
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
    header += '+-' + '-'*name_dim + '-+-' + '-'*params_dim + '-+\n'
    header += ('| ' + 'Form' + ' '*(name_dim-4) + ' ' +
               '| ' + 'Parameters' + ' '*(params_dim-10) + ' |\n')
    header += '+=' + '='*name_dim + '=+=' + '='*params_dim + '=+\n'

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
                 ' '*(name_dim-len(names[idx])) + ' ' +
                 '| ' + params[idx] +
                 ' '*(params_dim-len(params[idx])) + ' |\n')
        body += '+-' + '-'*name_dim + '-+-' + '-'*params_dim + '-+\n'

    return body
