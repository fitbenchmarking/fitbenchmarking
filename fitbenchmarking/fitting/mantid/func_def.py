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


def function_definitions(problem):
    """
    Transforms the prob.equation field into a function that can be
    understood by the mantid fitting software.

    @param prob :: object holding the problem infomation

    @returns :: a function definitions string with functions that
                mantid understands
    """
    if problem.type == 'nist':
        # NIST data requires prior formatting
        nb_start_vals = len(problem.starting_values[0][1])
        function_defs = parse_nist_function_definitions(problem, nb_start_vals)
    elif problem.type == 'neutron':
        # Neutron data does not require any
        function_defs = []
        function_defs.append(problem.equation)

    return function_defs

def parse_nist_function_definitions(problem, nb_start_vals):
    """
    Helper function that parses the NIST function definitions and
    transforms them into a mantid-redeable format.

    @param prob :: object holding the problem information
    @param nb_start_vals :: the number of starting points for a given
                            function definition

    @returns :: the formatted function definition (str)
    """

    function_defs = []
    for start_idx in range(0, nb_start_vals):
        start_val_str = ''
        for param in problem.starting_values:
            start_val_str += ('{0}={1},'.format(param[0], param[1][start_idx]))
        # Eliminate trailing comma
        start_val_str = start_val_str[:-1]
        function_defs.append("name=UserFunction,Formula={0},{1}".
                             format(problem.equation, start_val_str))

    return function_defs
