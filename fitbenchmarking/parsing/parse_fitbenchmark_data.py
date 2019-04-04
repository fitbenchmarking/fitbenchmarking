"""
Parse input files describing fitting test examples and load the
information into problem objects

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
# File change history is stored at: <https://github.com/mantidproject/mantid>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>

from __future__ import (absolute_import, division, print_function)

import os
from parsing import fitbm_problem
import mantid.simpleapi as msapi

from utils.logging_setup import logger


class FitbenchmarkFittingProblem(fitbm_problem.FittingProblem):
    """
    Definition of the native fitbenchmarking problem class

    Types of data:
        - strings: name, type, equation
        - floats: start_x, end_x, ref_residual_sum_sq
        - numpy arrays: data_x, data_y, data_e
        - arrays: starting_values
    """

    def __init__(self, file, prob_type):

        super(FitbenchmarkFittingProblem, self).__init__(file, prob_type)
        self.entries = {}
        self.data_file = None

    def __call__(self):

        super(FitbenchmarkFittingProblem, self).read_file()
        self.entries = get_fitbenchmark_data_problem_entries(self.contents)
        self.data_file = get_data_file(self.file, self.entries['input_file'])

    def set_data(self):
        """
        Class function that sets the data (data_x, data_y and data_e)
        """

        wks_imported = msapi.Load(Filename=self.data_file)
        self.data_x = wks_imported.readX(0)
        self.data_y = wks_imported.readY(0)
        self.data_e = wks_imported.readE(0)
        self.ref_residual_sum_sq = 0

    def set_definitions(self):
        """
        Class function that sets the problem definitions (name and equation)
        """

        self.name = self.entries['name']
        self.equation = self.entries['function']

    def set_initial_values(self):
        """
        Class function that sets the problem initial values (starting value,
        start_x and end_x)
        """

        self.starting_values = None
        self.start_x = self.entries['fit_parameters']['StartX']
        self.end_x = self.entries['fit_parameters']['EndX']


def get_data_file(fname, input_file):
    """
    Gets the path to the fitbenchmark problem data_file used in the problem.
    sep_idx is used to find the last separator in the problem file path
    and set up the path for the data_files folder i.e truncates the path
    to ../Neutron_data and adds ../Neutron_data/data_files

    @param fname :: path to the problem definition file
    @param input_file :: file name of the data file

    @returns :: path to the data files directory (str)
    """

    prefix = ""
    if os.sep in fname:
        sep_idx = fname.rfind(os.sep)
        prefix = os.path.join(fname[:sep_idx], "data_files")

    data_file = os.path.join(prefix, input_file)

    return data_file


def get_fitbenchmark_data_problem_entries(fname):
    """
    Get the problem entries from a fitbenchmark problem definition file.

    @param fname :: path to the fitbenchmark problem definition file

    @returns :: a dictionary with all the entires of the problem file
    """

    entries = {}
    for line in fname:
        # Discard comments
        line = line.partition('#')[0]
        line = line.rstrip()
        if not line:
            continue

        lhs, rhs = line.split("=", 1)
        entries[lhs.strip()] = eval(rhs.strip())

    return entries
