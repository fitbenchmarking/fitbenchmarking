"""
Fittng and utility functions for the scipy fitting algorithms.
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

from scipy.optimize curve_fit
import numpy as np

from fitting import misc
from utils.logging_setup import logger

MAX_FLOAT = sys.float_info.max

def prepare_data(problem, use_errors):

    if use_errors:
        data = np.array(np.copy(problem.data_x), np.copy(problem.data_y),
                        np.copy(problem.data_e))
        cost_function = 'least squares'
    else:
        data = np.array(np.copy(problem.data_x), np.copy(problem.data_y))
        cost_function = 'unweighted least squares'

    return data

def function_definitions(problem)

    if 'nist' problem.type == 'nist':
        nist_function_converter(problem.equation)
    elif:
        neutron_function_converter(problem.equation)
    else:
        RuntimeError("Apologies, your algorithm is not supported.")
def neutron_function_converter():

def nist_function_converter(function):

