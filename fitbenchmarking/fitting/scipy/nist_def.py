"""
Functions that prepare the nist problem function definitions to be in
the right format.
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

import numpy as np
from utils.logging_setup import logger


def nist_func_definitions(function, startvals):
    """
    Processing the nist function definitions into an appropriate format
    for the scipy softwareto use.

    @param function :: function string as defined in the problem file
    @param startvals :: starting values for the function variables
                        provided in the problem definition file

    @returns :: array containing the fitting_function callable by scipy,
                values of the parameters and the function string
    """
    param_names, all_values = get_nist_param_names_and_values(startvals)
    function = format_function_scipy(function)
    function_defs = []
    for values in all_values:
        exec "def fitting_function(x, " + param_names + "): return " + function
        function_defs.append([fitting_function, values, function])

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
    function = function.replace("pi", "np.pi")

    return function
