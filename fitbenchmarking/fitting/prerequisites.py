"""
Functions which deals with the things that are software (Mantid, scipy etc)
specific.
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


def prepare_software_prerequisites(software, problem, use_errors):
    """
    Prepare the required data structures and function definitions for each
    software.

    @param software :: software used in fitting the problem, can be
                        e.g. mantid, numpy etc.
    @param problem :: a problem object containing information used in fitting
    @param use_errors :: wether or not to use errors

    @returns :: prerequisites, depending on the software.
    """

    if software == 'mantid':
        return prepare_mantid(problem, use_errors)
    elif software == 'scipy':
        return prepare_scipy(problem, use_errors)
    elif software == 'sasview':
        return prepare_sasview(problem, use_errors)
    # elif software == 'your_software':
        # return prepare_your_software(problem, use_errors)
    else:
        raise NameError("Sorry, the specified software is not supported yet.")


def prepare_mantid(problem, use_errors):
    """
    Does the things specified in the above description for benchmarking
    the mantid software.

    @returns :: mantid workspace data structure
                mantid cost funtion
                mantid function definitions
    """
    from fitting.mantid.prepare_data import wks_cost_function
    from fitting.mantid.func_def import function_definitions

    wks_mtd, cost_function = \
        wks_cost_function(problem, use_errors)

    # String containing the function name(s) and the starting parameter values for each function
    function_definitions = \
        function_definitions(problem)

    return wks_mtd, cost_function, function_definitions


def prepare_scipy(problem, use_errors):
    """
    Does the things specified in the above description for benchmarking
    the scipy software.

    @returns :: scipy workspace data structure
                scipy cost function
                scipy function definitions
    """
    from fitting.scipy.prepare_data import prepare_data
    from fitting.scipy.func_def import function_definitions

    data, cost_function = \
        prepare_data(problem, use_errors)

    # String containing function evaluation methods and the starting values for each method
    function_definitions = function_definitions(problem)
    # For problems that have no specified boundaries, set -inf and +inf
    if problem.start_x == None and problem.end_x == None:
        problem.start_x = - np.inf
        problem.end_x = np.inf
    return data, cost_function, function_definitions

def prepare_sasview(problem, use_errors):

    from fitting.sasview.prepare_data import prepare_data
    from fitting.sasview.func_def import function_definitions

    data_obj, cost_function = prepare_data(problem, use_errors)

    function_definitions = function_definitions(problem)

    return data_obj, cost_function, function_definitions