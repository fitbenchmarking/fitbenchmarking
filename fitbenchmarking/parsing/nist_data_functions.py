"""
Functions that prepare the function specified in NIST problem definition file into
the right format for SciPy.
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


def nist_func_definitions(function, startvals):
    """
    Processing a function plus different set of starting values as specified in the NIST problem definition file
    into function definitions appropriate for the SciPy software.

    @param function :: function string as defined in a NIST problem definition file
    @param startvals :: starting values for the function variables
                        provided in the definition file

    @returns :: array where each element contains function callable by SciPy,
                one set of starting parameter values and copy of the function string
    """
    param_names, all_values = get_nist_param_names_and_values(startvals)
    function_scipy_format = format_function_scipy(function)
    function_defs = []

    # Create a function def for each starting set in startvals
    for values in all_values:
        exec "def fitting_function(x, " + param_names + "): return " + function_scipy_format
        function_defs.append([fitting_function, values, function_scipy_format])

    return function_defs


def get_nist_param_names_and_values(startvals):
    """
    Parses startvals and retrieves the nist param names and values.
    """
    param_names = [row[0] for row in startvals]
    param_names = ", ".join(param for param in param_names)
    all_values = [row[1] for row in startvals]
    all_values = map(list, zip(*all_values))

    return param_names, all_values


def format_function_scipy(function):
    """
    Formats the function string such that it is scipy-ready.
    """

    function = function.replace("exp", "np.exp")
    function = function.replace("^", "**")
    function = function.replace("cos", "np.cos")
    function = function.replace("sin", "np.sin")
    function = function.replace("tan", "np.tan")
    function = function.replace("pi", "np.pi")

    return function
