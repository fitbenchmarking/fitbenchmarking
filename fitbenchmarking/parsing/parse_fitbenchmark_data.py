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
import numpy as np
# import mantid.simpleapi as msapi

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
        data_file_path = self.get_data_file(self.fname, entries['input_file'])

        data_points = self.get_data_points(data_file_path)

        self._data_x = data_points[:,0]
        self._data_y = data_points[:,1]
        self._data_e = data_points[:,2]

        # wks_imported = msapi.Load(Filename=data_file)
        #
        # self._data_x = wks_imported.readX(0)
        # self._data_y = wks_imported.readY(0)
        # self._data_e = wks_imported.readE(0)
        self._name = entries['name']
        self._equation = entries['function']

        self._starting_values = None
        if 'fit_parameters' in entries:
            self._start_x = entries['fit_parameters']['StartX']
            self._end_x = entries['fit_parameters']['EndX']

        super(FittingProblem, self).close_file()

    def get_data_file(self, full_path_of_fitting_def_file, data_file_name):
        """
        Find/create the (full) path to a data_file specified in a FitBenchmark definition file, where
        the data_file is search for in the directory of the definition file and subfolders of this 
        file

        @param full_path_of_fitting_def_file :: (full) path of a FitBenchmark definition file
        @param data_file_name :: the name of the data file as specified in the FitBenchmark definition file

        @returns :: (full) path to a data file (str). Return None if not found
        """
        data_file = None
        # find or search for path for data_file_name
        for root, dirs, files in os.walk(os.path.dirname(full_path_of_fitting_def_file)):
            for name in files:
                if data_file_name == name:
                    data_file = os.path.join(root, data_file_name)

        if data_file == None:
            logger.error("Data file {} not found".format(data_file_name))

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

    def get_data_points(self, data_file_path):
        """
        Get the data points of the problem from the data file.

        @param data_file :: full path of the data file
        @return :: array of data points
        """

        data_object = open(data_file_path, 'r')
        data_text = data_object.readlines()

        first_row = data_text[2].strip()
        dim = len(first_row.split())
        data_points = np.zeros((len(data_text)-2, dim))

        for idx, line in enumerate(data_text[2:]):
            line = line.strip()
            point_text = line.split()
            point = [float(val) for val in point_text]
            data_points[idx, :] = point

        return data_points





