"""
General utility functions for calculating some attributes of the fit.
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
import mantid


def prepare_algorithm_prerequisites(algorithm, problem, use_errors):
    """
    Prepare the required data structures and function definitions for each
    algorithm.

    @param algorithm :: algorithm used in fitting the problem, can be
                        e.g. mantid, numpy etc.
    @param problem :: a problem object containing information used in fitting
    @param use_errors :: wether or not to use errors

    @returns :: prerequisites, depending on the algorithm.
    """

    if algorithm == 'mantid':
        from fitting import mantid
        wks_mtd, cost_function = mantid.wks_cost_function(problem, use_errors)
        function_definitions = mantid.function_definitions(problem)
        return wks_mtd, cost_function, function_definitions
    else:
        raise NameError("Sorry, the specified algorithm is not supported yet.")
