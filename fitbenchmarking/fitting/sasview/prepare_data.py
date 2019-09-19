"""
Functions that prepare the data to be in the right format.
"""

from __future__ import (absolute_import, division, print_function)

import numpy as np
from sasmodels.data import empty_data1D, Data1D

def prepare_data(problem, use_errors):
    """
    Prepares the data to be used in the fitting process.
    The acceptable data type is sasmodels.data.Data1D
    """

    problem = misc_preparations(problem)

    if use_errors:
        data_obj = Data1D(x=problem.data_x, y=problem.data_y, dy=problem.data_e)
        cost_function = 'least squares'
    else:
        data_obj = Data1D(x=problem.data_x, y=problem.data_y)
        cost_function = 'unweighted least squares'

    return data_obj, cost_function

def misc_preparations(problem):
    """
    Helper function that does some miscellaneous preparation of the data.
    It calculates the errors if they are not presented in problem file
    itself by assuming a Poisson distribution. Additionally, it applies
    constraints to the data if such constraints are provided.

    @return :: returns problem object with updated data
    """

    if problem.data_e is None:
        problem.data_e = np.sqrt(abs(problem.data_y))

    if problem.start_x is None and problem.end_x is None:
        pass
    elif problem.start_x is -np.inf and problem.end_x is np.inf:
        pass
    else:
        problem = apply_x_data_range(problem)

    return problem


def apply_x_data_range(problem):
    """
    Crop the data to fit within specified start_x and end_x values if these are provided otherwise
    return unalternated problem object.
    Scipy don't take start_x and end_x, meaning Scipy can on fit over the entire data array.

    @return :: Modified problem object where data have been cropped
    """

    if problem.start_x is None or problem.end_x is None:
        return problem

    start_x_diff = problem.data_x - problem.start_x
    end_x_diff = problem.data_x - problem.end_x
    start_idx = np.where(start_x_diff >= 0, start_x_diff, np.inf).argmin()
    end_idx = np.where(end_x_diff <= 0, end_x_diff, -np.inf).argmax()

    problem.data_x = np.array(problem.data_x)[start_idx:end_idx + 1]
    problem.data_y = np.array(problem.data_y)[start_idx:end_idx + 1]
    problem.data_e = np.array(problem.data_e)[start_idx:end_idx + 1]
    problem.data_e[problem.data_e == 0] = 0.00000001
    return problem
