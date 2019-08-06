"""
Functions that prepare the data to be in the right format.
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
from sasmodels.data import load_data, Data1D

from utils.logging_setup import logger

def prepare_data(problem, use_errors):

    problem = misc_preparations(problem)

    cost_function = 'Unweighted least squares'

    return problem.data_obj, cost_function

def misc_preparations(problem):
    """
    Helper function that does some miscellaneous preparation of the data.
    It calculates the errors if they are not presented in problem file
    itself by assuming a Poisson distribution. Additionally, it applies
    constraints to the data if such constraints are provided.

    @return :: returns problem object with updated data
    """

    if problem.data_e is None:
        # problem.data_obj.dy = 0.2 * problem.data_obj.y
        problem.data_obj.dy = np.sqrt(abs(problem.data_obj.y))
        problem.data_e = problem.data_obj.dy

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

    start_x_diff = problem.data_obj.x - problem.start_x
    end_x_diff = problem.data_obj.x - problem.end_x
    start_idx = np.where(start_x_diff >= 0, start_x_diff, np.inf).argmin()
    end_idx = np.where(end_x_diff <= 0, end_x_diff, -np.inf).argmax()

    problem.data_obj.x = np.array(problem.data_obj.x)[start_idx:end_idx + 1]
    problem.data_obj.y = np.array(problem.data_obj.y)[start_idx:end_idx + 1]
    problem.data_obj.dy = np.array(problem.data_obj.dy)[start_idx:end_idx + 1]
    problem.data_obj.dy[problem.data_obj.dy == 0] = 0.00000001
    return problem



