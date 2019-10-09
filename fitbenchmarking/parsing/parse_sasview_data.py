from __future__ import (absolute_import, division, print_function)

import os
import numpy as np
import re
from fitbenchmarking.parsing import base_fitting_problem
from sasmodels.data import load_data, empty_data1D
from sasmodels.core import load_model
from sasmodels.bumps_model import Experiment, Model

from fitbenchmarking.utils.logging_setup import logger


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

        data_obj = load_data(data_file_path)

        self._data_x = data_obj.x
        self._data_y = data_obj.y

        self._start_x, self._end_x = self.get_start_x_and_end_x(self._data_x)

        self._name = entries['name']
        tmp_equation = entries['function'].split(',', 1)[0]
        self._equation = tmp_equation.split('=')[1]

        tmp_starting_values = entries['function'].split(',')[1:]
        self._starting_values = [[f.split('=')[0], [float(f.split('=')[1])]]
                                 for f in tmp_starting_values]

        tmp_starting_value_ranges = entries['parameter_ranges'].split(';')
        tmp_names = (val_range_txt.split('.', 1)[0]
                     for val_range_txt in tmp_starting_value_ranges)
        tmp_values = (tmp_range.split('(')[1]
                      for tmp_range in tmp_starting_value_ranges)
        tmp_values = (tmp_range.strip(')') for tmp_range in tmp_values)
        tmp_values = ([float(val) for val in tmp_range.split(',')]
                      for tmp_range in tmp_values)
        self._starting_value_ranges = {name: values
                                       for name, values
                                       in zip(tmp_names, tmp_values)}

        self.function = None

        super(FittingProblem, self).close_file()

    def get_function(self):
        """
        Creates list of functions alongside the starting parameters.
        Functions are saved to the instance so that this is only generated
        once.

        @returns :: function definition list containing the model and its
                    starting parameter values
        """
        if self.function is None:

            functions = []
            for i in range(len(self._starting_values[0][1])):

                param_names = [params[0] for params in self._starting_values]

                def fitFunction(x, *tmp_params):

                    model = load_model(self._equation)

                    data = empty_data1D(x)
                    param_dict = {name: value
                                  for name, value
                                  in zip(param_names, tmp_params)}

                    model_wrapper = Model(model, **param_dict)
                    for name, values in self.starting_value_ranges.items():
                        model_wrapper.__dict__[name].range(values[0], values[1])
                    func_wrapper = Experiment(data=data, model=model_wrapper)

                    return func_wrapper.theory()

                param_values = [params[1][i] for params in self._starting_values]

                functions.append([fitFunction, param_values, self._equation])

            self.function = functions

        return self.function

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

    def get_start_x_and_end_x(self, x_data):
        """

        Get the start and end value of x from the list of x values.

        @param x_data :: list containing x values
        @return :: the start and end values of the x data
        """

        sorted_x_data = sorted(x_data)

        start_x = sorted_x_data[0]
        end_x = sorted_x_data[-1]

        return start_x, end_x
