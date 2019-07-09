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
from parsing import base_fitting_problem
import mantid.simpleapi as msapi

from utils.logging_setup import logger


class FittingProblem(base_fitting_problem.BaseFittingProblem):
    """
    Definition of the native FitBenchmarking problem class, which
    provides the methods for parsing a native FitBenchmarking
    problem definition (FitBenchmark) file

    Types of data:
        - strings: name, type, equation
        - floats: start_x, end_x, ref_residual_sum_sq
        - numpy arrays: data_x, data_y, data_e
        - arrays: starting_values
    """

    def __init__(self, fname):

        super(FittingProblem, self).__init__(fname)
        super(FittingProblem, self).read_file()

        entries = self.get_fitbenchmark_data_problem_entries(self.contents)
        data_file = self.get_data_file(self.fname, entries['input_file'])

        wks_imported = msapi.Load(Filename=data_file)

        self._data_x = wks_imported.readX(0)
        self._data_y = wks_imported.readY(0)
        self._data_e = wks_imported.readE(0)

        self._ref_residual_sum_sq = 0

        self._name = entries['name']
        self._equation = entries['function']
        self._type = "FitBenchmark"

        self._starting_values = None
        if 'fit_parameters' in entries:
            self._start_x = entries['fit_parameters']['StartX']
            self._end_x = entries['fit_parameters']['EndX']

        super(FittingProblem, self).close_file()

    def get_data_file(self, fname, input_file):
        """
        Gets the path to the fitbenchmark problem data_file used in the problem.

        @param fname :: path to the problem definition file
        @param input_file :: file name of the data file

        @returns :: path to the data files directory (str)
        """
        data_file = None
        #find path of the folder containing data files
        for root, dirs, files in os.walk(os.path.dirname(fname)):
            for name in files:
                if input_file == name:
                    data_file = os.path.join(root, input_file)

        if data_file == None:
            logger.error("Data file {0} not found".format(input_file))

        return data_file

    def get_fitbenchmark_data_problem_entries(self, fname):
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
