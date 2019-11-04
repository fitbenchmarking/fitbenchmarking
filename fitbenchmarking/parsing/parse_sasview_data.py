from __future__ import (absolute_import, division, print_function)

from collections import OrderedDict
import os
from sasmodels.data import load_data, empty_data1D
from sasmodels.core import load_model
from sasmodels.bumps_model import Experiment, Model

from fitbenchmarking.parsing import base_fitting_problem
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

        self._entries = self.get_data_problem_entries()
        self._parsed_func = self.parse_function()

        self._name = self._entries['name']

        data_file_path = self.get_data_file()
        data_obj = load_data(data_file_path)

        self._data_x = data_obj.x
        self._data_y = data_obj.y

        self._equation = self._parsed_func['name']

        self._starting_values = self.get_starting_values()

        # start and end values in x range
        if 'fit_parameters' in self._entries:
            start_x, end_x = self.get_x_range()
            self._start_x = start_x
            self._end_x = end_x

        self._starting_value_ranges = self.get_value_ranges()

        self.function = self.create_sasview_functions()

        super(FittingProblem, self).close_file()

    def get_function(self):
        """
        Get the functions list

        :return: Functions list
        :rtype: list
        """
        return self.function

    def get_data_file(self):
        """
        Find/create the (full) path to a data_file specified in a SasView definition file, where
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

    def get_data_problem_entries(self):
        """
        Get the problem self._entries from a sasview problem definition file.

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

        :returns: Function definition in format:
                  {name: [value1, value2, ...], ...}
        :rtype: dict
        """

        f = self._entries['function']

        if ';' in f:
            raise ValueError('Could not parse function.'
                             + 'Please check file.')

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

        return params_dict

    def get_starting_values(self):
        """
        Get the starting values for the problem

        :returns: Starting values for the function
        :rtype: list
        """
        ignore = ['name']

        starting_values = [[name, [val]]
                           for name, val in self._parsed_func.items()
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

    def get_value_ranges(self):
        """
        Get the value ranges from the problem.

        :return: Value ranges
        :rtype: dict {name: [min, max]}
        """
        value_ranges = {}

        for param in self._entries['parameter_ranges'].split(';'):
            name, value_txt = param.split('.range', 1)
            value_txt = value_txt.strip('(').strip(')')
            value_range = [float(val) for val in value_txt.split(',')]
            value_ranges[name] = value_range

        return value_ranges

    def create_sasview_functions(self):
        """
        Creates list of functions alongside the starting parameters.

        :returns: Function definition list containing the model and its
                  starting parameter values
        :rtype: List of list
        """
        functions = []

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

        for i in range(len(self._starting_values[0][1])):

            param_values = [params[1][i] for params in self._starting_values]

            functions.append([fitFunction, param_values])

        return functions
