from __future__ import (absolute_import, division, print_function)

import os
import numpy as np
import re
from parsing import base_fitting_problem
from sasmodels.data import load_data, empty_data1D
from sasmodels.core import load_model
from sasmodels.bumps_model import Experiment, Model

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

        data_obj = load_data(data_file_path)

        self._data_x = data_obj.x
        self._data_y = data_obj.y

        self._start_x, self._end_x = self.get_start_x_and_end_x(self._data_x)

        self._name = entries['name']
        self._equation = (entries['function'].split(',', 1))[0]

        self._starting_values = (entries['function'].split(',', 1))[1]
        self._starting_value_ranges = entries['parameter_ranges']

        super(FittingProblem, self).close_file()

    def eval_f(self, x, *param_list):
        """
        Function Evaluation Method

        @param x :: x data values
        @param *param_list :: parameter value(s)

        @ returns :: the y data values evaluated from the model
        """
        data = empty_data1D(x)
        model = load_model((self._equation.split('='))[1])

        param_names = [(param.split('='))[0] for param in self.starting_values.split(',')]
        if len(param_list) == 1:
            if isinstance(param_list[0],basestring):
                exec ("params = dict(" + param_list[0] + ")")
        else:
            param_string = ''
            for name, value in zip(param_names, param_list):
                param_string += name+'='+str(value)+','
            param_string = param_string[:-1]
            exec ("params = dict(" + param_string + ")")

        model_wrapper = Model(model, **params)
        for range in self.starting_value_ranges.split(';'):
            exec ('model_wrapper.' + range)
        func_wrapper = Experiment(data=data, model=model_wrapper)

        return func_wrapper.theory()

    def get_function(self):
        """

        @returns :: function definition list containing the model and its starting parameter values
        """

        param_values = [(param.split('='))[1] for param in self.starting_values.split(',')]
        param_values = np.array([param_values],dtype=np.float64)

        function_defs = []

        for param in param_values:

            function_defs.append([self.eval_f, param])

        return function_defs


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
