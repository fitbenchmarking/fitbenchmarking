from __future__ import (absolute_import, division, print_function)

import os
from fitbenchmarking.parsing import base_fitting_problem
import numpy as np

from fitbenchmarking.utils.logging_setup import logger
from fitbenchmarking.parsing.fitbenchmark_data_functions import (
    fitbenchmark_func_definitions, get_fit_function_without_kwargs
)


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

        self._data_x = data_points[:, 0]
        self._data_y = data_points[:, 1]
        self._data_e = data_points[:, 2]
        self._name = entries['name']

        # String containing the function name(s) and the starting parameter values for each function
        self._mantid_equation = entries['function']

        equation = entries['function'].split(';', 1)[-1]
        equation = equation.split(',', 1)[0]
        self._equation = equation.split('=', 1)[1].strip()

        tmp_starting_values = entries['function'].split(';')[-1]
        tmp_starting_values = tmp_starting_values.split(',')[1:]
        self._starting_values = [[f.split('=')[0].strip(),
                                  [float(f.split('=')[1].strip())]]
                                 for f in tmp_starting_values
                                 if f.split('=')[0] != 'BinWidth']

        if 'fit_parameters' in entries:
            self._start_x = entries['fit_parameters']['StartX']
            self._end_x = entries['fit_parameters']['EndX']

        super(FittingProblem, self).close_file()

    def get_function(self):
        """

        @returns :: function definition list containing the function and its starting parameter values
        """

        function = fitbenchmark_func_definitions(self._mantid_equation)

        return function

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
