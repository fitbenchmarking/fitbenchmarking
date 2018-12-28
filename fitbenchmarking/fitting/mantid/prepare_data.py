"""
Fitting and utility functions for the mantid fitting software.
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

import copy
import numpy as np
import mantid.simpleapi as msapi

from utils.logging_setup import logger


def wks_cost_function(problem, use_errors=True):
    """
    Helper function that prepares the data workspace used by mantid
    for fitting.

    @param problem :: object holding the problem information
    @param use_errors :: whether to use errors or not

    @returns :: the fitting data in workspace format and the
                cost function used in fitting
    """
    data_x = problem.data_x
    data_y = problem.data_y
    data_e = setup_errors(problem)

    if use_errors:
        wks_created = msapi.CreateWorkspace(DataX=data_x, DataY=data_y,
                                            DataE=data_e)
        convert_back(wks_created, problem, use_errors)
        cost_function = 'Least squares'
    else:
        wks_created = msapi.CreateWorkspace(DataX=data_x, DataY=data_y)
        convert_back(wks_created, problem, use_errors)
        cost_function = 'Unweighted least squares'

    return wks_created, cost_function

def setup_errors(problem):
    """
    Gets errors on the data points from the problem object if there are
    any. If not, the errors are approximated by taking the square root
    of the absolute y-value, since we cannot know how the data was
    obtained and this is a reasonable approximation.

    @param problem :: object holding the problem information

    @returns :: array of errors of particular problem
    """

    if problem.data_e is None:
        # Fake errors
        return np.sqrt(abs(problem.data_y))
    else:
        # True errors
        return problem.data_e

def convert_back(wks_used, problem, use_errors):
    """
    Convert back so data is of equal lengths.

    @param wks_used :: mantid workspace that hold the data
    @param problem :: problem object holding the problem data
    """
    tmp = msapi.ConvertToPointData(wks_used)
    problem.data_x = np.copy(tmp.readX(0))
    problem.data_y = np.copy(tmp.readY(0))
    if use_errors: problem.data_e = np.copy(tmp.readE(0))

def store_main_problem_data(fname, problem):
    """
    Stores the main problem data into the relevant attributes of the
    problem object.

    @param fname :: path to the neutron problem definition file
    @param problem :: object holding the problem information
    """

    wks_imported = msapi.Load(Filename=fname)
    problem.data_x = wks_imported.readX(0)
    problem.data_y = wks_imported.readY(0)
    problem.data_e = wks_imported.readE(0)
    problem.ref_residual_sum_sq = 0
