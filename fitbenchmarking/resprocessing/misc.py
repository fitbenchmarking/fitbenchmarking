"""
File contains miscellaneous functions used for post processing the
fitting results.
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


def display_name_for_minimizers(names):
    """
    Converts minimizer names into their "display names". For example
    to rename DTRS to "Trust region" or similar
    """

    display_names = names
    # Quick fix for DTRS name in version 3.8 - REMOVE
    for idx, minimizer in enumerate(names):
        if 'DTRS' == minimizer:
            display_names[idx] = 'Trust Region'

    return display_names


def weighted_suffix_string(use_errors):
    """
    Produces a suffix weighted/unweighted. Used to generate names of
    output files.
    """
    values = {True: 'weighted', False: 'unweighted'}
    return values[use_errors]


def build_items_links(comparison_type, comp_dim, using_errors):
    """
    Figure out the links from rst table cells to other pages/sections of pages.

    @param comparison_type :: whether this is a 'summary', or a full 'accuracy',
                              or 'runtime' table.
    @param comp_dim :: dimension (accuracy / runtime)
    @param using_errors :: whether using observational errors in cost functions

    @returns :: link or links to use from table cells.
    """
    if 'summary' == comparison_type:
        items_link = ['Minimizers_{0}_comparison_in_terms_of_{1}_nist_lower'.
                      format(weighted_suffix_string(using_errors), comp_dim),
                      'Minimizers_{0}_comparison_in_terms_of_{1}_nist_average'.
                      format(weighted_suffix_string(using_errors), comp_dim),
                      'Minimizers_{0}_comparison_in_terms_of_{1}_nist_higher'.
                      format(weighted_suffix_string(using_errors), comp_dim),
                      'Minimizers_{0}_comparison_in_terms_of_{1}_cutest'.
                      format(weighted_suffix_string(using_errors), comp_dim),
                      'Minimizers_{0}_comparison_in_terms_of_{1}_neutron_data'.
                      format(weighted_suffix_string(using_errors), comp_dim),
                      ]
    elif 'accuracy' == comparison_type or 'runtime' == comparison_type:
        if using_errors:
            items_link = 'FittingMinimizersComparisonDetailedWithWeights'
        else:
            items_link = 'FittingMinimizersComparisonDetailed'
    else:
        items_link = ''

    return items_link


def make_result_tables_directory(results_dir, group_name):
    """
    Creates the results directory where the tables are located.
    e.g. fitbenchmarking/results/neutron/Tables/
    """

    if 'nist' in group_name:
        group_results_dir = os.path.join(results_dir, 'nist')
        if not os.path.exists(group_results_dir):
            os.makedirs(group_results_dir)
        tables_dir = os.path.join(group_results_dir, "tables", group_name)

    elif 'neutron' in group_name:
        group_results_dir = os.path.join(results_dir, 'neutron')
        if not os.path.exists(group_results_dir):
            os.makedirs(group_results_dir)
        tables_dir = os.path.join(group_results_dir, "tables")

    if not os.path.exists(tables_dir):
        os.makedirs(tables_dir)

    return tables_dir
