"""
Methods that prepare the data to be used by the mantid fitting software.
"""

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
