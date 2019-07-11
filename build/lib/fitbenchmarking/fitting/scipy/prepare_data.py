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

from utils.logging_setup import logger


def prepare_data(problem, use_errors):
    """
    Prepares the data to be used in the fitting process.
    """
    data_x = np.copy(problem.data_x)
    data_y = np.copy(problem.data_y)
    data_e = problem.data_e
    data_x, data_y, data_e = misc_preparations(problem, data_x, data_y, data_e)

    if use_errors:
        data = np.array([data_x, data_y, data_e])
        cost_function = 'least squares'
    else:
        data = np.array([data_x, data_y])
        cost_function = 'unweighted least squares'

    return data, cost_function

def misc_preparations(problem, data_x, data_y, data_e):
    """
    Helper function that does some miscellaneous preparation of the data.
    It calculates the errors if they are not presented in problem file
    itself by assuming a Poisson distribution. Additionally, it applies
    constraints to the data if such constraints are provided.
    """
    if len(data_x) != len(data_y):
        data_x = data_x[:-1]
        problem.data_x = np.copy(data_x)
    if data_e is None:
        data_e = np.sqrt(abs(data_y))
        problem.data_e = np.copy(data_e)

    if problem.start_x is None and problem.end_x is None: pass
    else:
        data_x, data_y, data_e = \
        apply_constraints(problem.start_x, problem.end_x,
                          data_x, data_y, data_e)

    return data_x, data_y, data_e

def apply_constraints(start_x, end_x, data_x, data_y, data_e):
    """
    Applied constraints to the data if they are provided. Useful when
    fitting only part of the available data.
    """
    start_idx = (np.abs(data_x - start_x)).argmin()
    end_idx = (np.abs(data_x - end_x)).argmin()
    data_x = np.copy(data_x[start_idx:end_idx])
    data_y = np.copy(data_y[start_idx:end_idx])
    data_e = np.copy(data_e[start_idx:end_idx])
    data_e[data_e == 0] = 0.00000001
    return data_x, data_y, data_e
