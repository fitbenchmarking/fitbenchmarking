"""
Functions that prepare the data to be in the right format.
"""

from __future__ import (absolute_import, division, print_function)

import numpy as np

def prepare_data(problem, use_errors):
    """
    Prepares the data to be used in the fitting process.
    """

    data_x = np.copy(problem.data_x)
    data_y = np.copy(problem.data_y)
    data_e = problem.data_e
    problem = misc_preparations(problem, data_x, data_y, data_e)

    if use_errors:
        data = np.array([problem.data_x, problem.data_y, problem.data_e])
        cost_function = 'least squares'
    else:
        data = np.array([problem.data_x, problem.data_y])
        cost_function = 'unweighted least squares'

    return data, cost_function

def misc_preparations(problem, data_x, data_y, data_e):
    """
    Helper function that does some miscellaneous preparation of the data.
    It calculates the errors if they are not presented in problem file
    itself by assuming a Poisson distribution. Additionally, it applies
    constraints to the data if such constraints are provided.

    @return :: returns problem object with updated data
    """
    if len(data_x) != len(data_y):
        data_x = data_x[:-1]
        problem.data_x = np.copy(data_x)

    if data_e is None:
        data_e = np.sqrt(abs(data_y))
        problem.data_e = np.copy(data_e)

    if problem.start_x is None and problem.end_x is None: pass

    if problem.start_x is -np.inf and problem.end_x is np.inf: pass
    else:
        problem = \
        apply_x_data_range(problem)

    return problem

def apply_x_data_range(problem):
    """
    Crop the data to fit within specified start_x and end_x values if these are provided otherwise
    return unalternated problem object.
    Scipy don't take start_x and end_x, meaning SasView can on fit over the entire data array.

    @return :: Modified problem object where data have been cropped
    """

    if problem.start_x is None or problem.end_x is None:
        return problem

    start_x_diff = problem.data_x - problem.start_x
    end_x_diff = problem.data_x - problem.end_x
    start_idx = np.where(start_x_diff >= 0, start_x_diff, np.inf).argmin()
    end_idx = np.where(end_x_diff <= 0, end_x_diff, -np.inf).argmax()

    problem.data_x = np.array(problem.data_x)[start_idx:end_idx+1]
    problem.data_y = np.array(problem.data_y)[start_idx:end_idx+1]
    problem.data_e = np.array(problem.data_e)[start_idx:end_idx+1]
    problem.data_e[problem.data_e == 0] = 0.00000001
    return problem
