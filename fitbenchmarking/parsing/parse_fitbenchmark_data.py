from __future__ import (absolute_import, division, print_function)

from collections import OrderedDict
import os
import mantid.simpleapi as msapi
import numpy as np

from fitbenchmarking.parsing import base_fitting_problem
from fitbenchmarking.utils.logging_setup import logger


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

        self._entries = self.get_fitbenchmark_data_problem_entries()
        self._parsed_func = self.parse_function()

        self._name = self._entries['name']

        data_points = self.get_data_points()

        self._data_x = data_points[:, 0]
        self._data_y = data_points[:, 1]
        self._data_e = data_points[:, 2]

        # String containing the function name(s) and the starting parameter values for each function
        self._mantid_equation = self._entries['function']

        self.function = self.fitbenchmark_func_definitions()

        # Print number of equations until better way of doing this is looked at.
        equation_count = len(self._parsed_func)
        self._equation = '{} Functions'.format(equation_count)

        self.starting_values = self.get_starting_values()

        # start and end values in x range
        if 'fit_parameters' in self._entries:
            start_x, end_x = self.get_x_range()
            self._start_x = start_x
            self._end_x = end_x
        super(FittingProblem, self).close_file()

    def get_function(self):
        """

        @returns :: function definition list containing the function and its
                    starting parameter values
        """
        return self.function

    def get_data_file(self):
        """
        Find/create the (full) path to a data_file specified in a FitBenchmark definition file, where
        the data_file is search for in the directory of the definition file and subfolders of this
        file

        @returns :: (full) path to a data file (str). Return None if not found
        """
        data_file = None
        data_file_name = self._entries['input_file']
        # find or search for path for data_file_name
        for root, _, files in os.walk(os.path.dirname(self.fname)):
            for name in files:
                if data_file_name == name:
                    data_file = os.path.join(root, data_file_name)

        if data_file is None:
            logger.error("Data file {} not found".format(data_file_name))

        return data_file

    def get_fitbenchmark_data_problem_entries(self):
        """
        Get the problem self._entries from a fitbenchmark problem definition file.

        :returns: The entries from the file with string values
        :rtype: dict
        """

        entries = {}
        for line in self.contents:
            # Discard comments
            line = line.split('#', 1)[0]
            line = line.rstrip()
            if not line:
                continue

            lhs, rhs = line.split("=", 1)
            entries[lhs.strip()] = rhs.strip().strip('"').strip("'")

        return entries

    def parse_function(self):
        """
        Get the params from the function as a list of dicts from the data file

        :returns: Fucntion definition in format:
                  [{name: [value1, value2, ...], ...]
        :rtype: list of dict
        """
        function_def = []

        functions = self._entries['function'].split(';')

        for f in functions:
            params_dict = OrderedDict()
            params_list = f.split(',')
            pop_stack = False
            stack = [params_dict]
            for p in params_list:
                name, val = p.split('=', 1)
                name = name.strip()
                val = val.strip()

                if val[0] == '(':
                    stack += [OrderedDict()]
                    val = val[1:]
                if val[-1] == ')':
                    if len(stack) == 1:
                        raise ValueError('Could not parse.'
                                         + 'Check parentheses in input')
                    val = val[:-1]
                    pop_stack = True

                # Parse to an int/float if possible else assume string
                tmp_val = None
                for t in [int, float]:
                    if tmp_val is None:
                        try:
                            tmp_val = t(val)
                        except ValueError:
                            pass

                if tmp_val is not None:
                    val = tmp_val

                stack[-1][name] = val

                if pop_stack:
                    stack = stack[:-1]

            function_def.append(params_dict)

        return function_def

    def get_data_points(self):
        """
        Get the data points of the problem from the data file.

        @return :: array of data points
        """

        data_file_path = self.get_data_file()
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

    def get_starting_values(self):
        """
        Get the starting values for the problem

        :returns: Starting values for the function
        :rtype: list
        """
        ignore = ['name', 'BinWidth', 'ties']

        starting_values = [['f{}_{}'.format(i, name), f[name]]
                           for i, f in enumerate(self._parsed_func)
                           for name in f.keys()
                           if name not in ignore]

        return starting_values

    def get_x_range(self):
        """
        Get the x ranges for the problem

        :returns: start_x and end_x
        :rtype: float, float
        """
        fit_params_str = self._entries['fit_parameters'].strip('{').strip('}')
        fit_params = fit_params_str.split(',')
        for f in fit_params:
            name, val = f.split(':')
            name = name.strip().strip('"').strip("'")
            if name not in ['StartX', 'EndX']:
                continue

            try:
                val = float(val.strip())
            except ValueError:
                raise ValueError('Could not parse fit_parameter: {}'.format(f))

            if name == 'StartX':
                start_x = val
            else:
                end_x = val

        return start_x, end_x

    def fitbenchmark_func_definitions(self):
        """
        Processing the function in the FitBenchmark problem definition into a python
        callable.

        :returns: A function definition array of one element which contains a
                callable Mantid function and the function parameter values.
        :rtype: list
        """
        fit_function = None
        param_vals = []

        for f in self._parsed_func:
            name = f['name']
            params = {key: f[key]
                      for key in f
                      if key not in ['name', 'BinWidth', 'ties']}
            param_vals.extend(params.values())
            tmp_function = msapi.__dict__[name](**params)
            if fit_function is None:
                fit_function = tmp_function
            else:
                fit_function += tmp_function

        for i, f in enumerate(self._parsed_func):
            if 'ties' in f:
                for tie, val in f['ties']:
                    fit_function.tie(name='f{}.{}'.format(i, tie),
                                     expr=val)

        function_def = [[fit_function, param_vals]]

        return function_def
