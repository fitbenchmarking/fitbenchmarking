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
# File change history is stored at: <https://github.com/mantidproject/mantid>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>
from __future__ import (absolute_import, division, print_function)


class FittingTestProblem(object):
    """
    Definition of a fitting test problem, normally loaded from a problem
    definition file.
    """
    def __init__(self):
        self.name = None
        # If there is an online/documentation link describing this problem
        self.equation = None
        self.start_x = None
        self.end_x = None

        # can be for example the list of starting values from
        # NIST test problems
        self.starting_values = None
        # The data
        self.data_x = None
        self.data_y = None
        self.data_e = None

        # The 'certified' or reference sum of squares, if provided
        # (for example in NIST tests).
        self.ref_residual_sum_sq = None
