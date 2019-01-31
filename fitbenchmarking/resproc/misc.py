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
import os

from resproc import visual_pages


def display_name_for_minimizers(names):
    """
    Converts minimizer names into their "display names". For example
    to rename DTRS to "Trust region" or similar.

    @param names :: array of minimizer names

    @returns :: the converted minimizer name array
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

    @param use_errors :: boolean showing if the user wants to consider
                         errors on the data points or not

    @returns :: 'weighted' or 'unweighted' string
    """
    values = {True: 'weighted', False: 'unweighted'}
    return values[use_errors]


def build_items_links(comparison_type, comp_dim, using_errors):
    """
    Figure out the links from rst table cells to other pages/sections
    of pages.

    @param comparison_type :: whether this is a 'summary', or a full
                              'accuracy', or 'runtime' table.
    @param comp_dim :: dimension (accuracy / runtime)
    @param using_errors :: whether using observational errors
                           in cost functions

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
