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

import mantid.simpleapi as msapi
from utils.logging_setup import logger


def gen_func_obj(function_name):
    """
    Generates a mantid function object.

    @param function_name :: the name of the function to be generated

    @returns :: mantid function object that can be called in python
    """
    exec "function_object = msapi." + function_name + "()"
    return function_object


def set_ties(function_object, ties):
    """
    Sets the ties for a function/composite function object.

    @param function_object :: mantid function object
    @param ties :: array of strings containing the ties

    @returns :: mantid function object with ties
    """
    for idx, ties_per_func in enumerate(ties):
        for tie in ties_per_func:
            exec "function_object.tie({'f" + str(idx) + "." + tie + "})"

    return function_object

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
