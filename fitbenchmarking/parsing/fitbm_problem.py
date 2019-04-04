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

from abc import ABCMeta, abstractmethod


class FittingProblem(object):
    """
    Definition of a base class implementation of the fitting test problem,
    normally loaded from a problem definition file.

    Types of data:
        - strings: name, type, equation
        - floats: start_x, end_x, ref_residual_sum_sq
        - numpy arrays: data_x, data_y, data_e
        - arrays: starting_values
    """
    __metaclass__ = ABCMeta

    def __init__(self, file):

        # Initializes
        self.file = file

        self.name = None
        # The type of problem, i.e. either neutron or nist etc.
        self.type = None
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

    @abstractmethod
    def __call__(self):
        pass

    def read_file(self):
        self.contents = open(self.file, "r")

    def print_file(self):
        for lines in self.contents:
            print(lines)

    @abstractmethod
    def set_data(self):
        self.data_x, self.data_y, self.data_e

    def get_data(self):
        return self.data_x, self.data_y, self.data_e

    @abstractmethod
    def set_definitions(self):
        self.name, self.type, self.equation

    def get_definitions(self):
        return self.name, self.type, self.equation

    @abstractmethod
    def set_initial_values(self):
        self.start_x, self.end_x, self.starting_values

    def get_initial_values(self):
        return self.start_x, self.end_x, self.starting_values
