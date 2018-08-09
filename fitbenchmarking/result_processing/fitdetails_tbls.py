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
    Builds an rst table containing the functional form and the parameters
    given the function definition string of the problem.
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
    Helper function that parses the function definition of a nist problem
    and returns the function name and parameters.
    """
    first_comma = function.find(',')
    second_comma = function.find(',', first_comma + 1)
    function_name = function[first_comma+10:second_comma]
    function_parameters = function[second_comma+2:-1]
    function_parameters = function_parameters.replace(',', ', ')

    return [function_name], [function_parameters]


def parse_neutron_function_def(function, function_names, function_parameters):
    """
    Helper function that parses the function definition of a neutron problem
    and returns the function name and parameters.
    """
    first_comma = function.find(',')
    if first_comma != -1:
        function_names.append(function[5:first_comma])
        function_parameters.append(function[first_comma+1:])
    else:
        function_names.append(function[5:])
        function_parameters.append('None')

    for idx in range(0, len(function_parameters)):
        function_parameters[idx] = function_parameters[idx].replace(',', ', ')

    return function_names, function_parameters


def fit_details_table_hdims(function_names, function_parameters):
    """
    Helper function that resolves the header dimensions of the fit details
    table present in the rst visual display page.
    """

    name_header_dim = max(len(name) for name in function_names)
    params_header_dim = max(len(parameter) for parameter in function_parameters)

    if name_header_dim < 4:
        name_header_dim = 4
    if params_header_dim < 10:
        params_header_dim = 10

    return name_header_dim, params_header_dim


def generate_fit_det_header(name_dim, params_dim):
    """
    Generates header of table containing the fit details.
    """

    header = ''
    header += '+-' + '-'*name_dim + '-+-' + '-'*params_dim + '-+\n'
    header += ('| ' + 'Form' + ' '*(name_dim-4) + ' ' +
               '| ' + 'Parameters' + ' '*(params_dim-10) + ' |\n')
    header += '+=' + '='*name_dim + '=+=' + '='*params_dim + '=+\n'

    return header


def generate_fit_det_body(names, params, name_dim, params_dim):
    """
    Generates the body of table containing fit details.
    """

    body = ''
    for idx in range(0, len(names)):

        body += ('| ' + names[idx] +
                 ' '*(name_dim-len(names[idx])) + ' ' +
                 '| ' + params[idx] +
                 ' '*(params_dim-len(params[idx])) + ' |\n')
        body += '+-' + '-'*name_dim + '-+-' + '-'*params_dim + '-+\n'

    return body
