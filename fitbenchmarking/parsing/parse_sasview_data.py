from __future__ import (absolute_import, division, print_function)

import os
import numpy as np
import re
from parsing import base_fitting_problem
from sasmodels.data import load_data

from utils.logging_setup import logger

class FittingProblem(base_fitting_problem.BaseFittingProblem):
    """
    Definition of the SasView problem class, which provides the
    methods for parsing a SasView formatted FitBenchmarking
    problem definition file

    Types of data:
        - strings: name, type, equation
        - floats: start_x, end_x, ref_residual_sum_sq
        - numpy arrays: data_x, data_y, data_e
        - arrays: starting_values
    """
    def __init__(self, fname):

        super(FittingProblem, self).__init__(fname)
        super(FittingProblem, self).read_file()

        entries = self.get_data_problem_entries(self.contents)
        data_file_path = self.get_data_file(self.fname, entries['input_file'])

        # data_points = self.get_data_points(data_file_path)
        data = load_data(data_file_path)

        self._data_x = data.x
        self._data_y = data.y
        # self._data_e = data.e

        self._name = entries['name']
        self._equation = entries['function']

        self._starting_values = None
        # if 'fit_parameters' in entries:
        #     self._start_x = entries['fit_parameters']['StartX']
        #     self._end_x = entries['fit_parameters']['EndX']

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

    def get_data_problem_entries(self, fname):
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

