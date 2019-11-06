from __future__ import (absolute_import, division, print_function)

from collections import OrderedDict
import os
from sasmodels.data import load_data, empty_data1D
from sasmodels.core import load_model
from sasmodels.bumps_model import Experiment, Model

from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.logging_setup import logger


class SasViewParser(Parser):
    """
    Parser for the SasView problem definition file.
    """
    def parse(self):
        """
        Parse the SasView problem file into a Fitting Problem.

        :return: The fully parsed fitting problem
        :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
        """
        fitting_problem = FittingProblem()

        self._entries = self._get_data_problem_entries()
        self._parsed_func = self._parse_function()

        fitting_problem.name = self._entries['name']

        data_file_path = self._get_data_file()
        data_obj = load_data(data_file_path)

        fitting_problem.data_x = data_obj.x
        fitting_problem.data_y = data_obj.y

        fitting_problem.equation = self._parsed_func['name']

        fitting_problem.starting_values = self._get_starting_values()

        # start and end values in x range
        if 'fit_parameters' in self._entries:
            start_x, end_x = self._get_x_range()
            fitting_problem.start_x = start_x
            fitting_problem.end_x = end_x

        fitting_problem.starting_value_ranges = self._get_value_ranges()

        fitting_problem.functions = self._create_sasview_functions()

        return fitting_problem

    def _get_data_file(self):
        """
        Find/create the (full) path to a data_file specified in a SasView definition file, where
        the data_file is search for in the directory of the definition file and subfolders of this
        file

        @returns :: (full) path to a data file (str). Return None if not found
        """
        data_file = None
        data_file_name = self._entries['input_file']
        # find or search for path for data_file_name
        for root, _, files in os.walk(os.path.dirname(self._filename)):
            for name in files:
                if data_file_name == name:
                    data_file = os.path.join(root, data_file_name)

        if data_file is None:
            logger.error("Data file {} not found".format(data_file_name))

        return data_file

    def _get_data_problem_entries(self):
        """
        Get the problem self._entries from a sasview problem definition file.

        :returns: The entries from the file with string values
        :rtype: dict
        """

        entries = {}
        for line in self.file.readlines():
            # Discard comments
            line = line.split('#', 1)[0]
            line = line.rstrip()
            if not line:
                continue

            lhs, rhs = line.split("=", 1)
            entries[lhs.strip()] = rhs.strip().strip('"').strip("'")

        return entries

    def _parse_function(self):
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

    def _get_starting_values(self):
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

    def _get_x_range(self):
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

    def _get_value_ranges(self):
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

    def _create_sasview_functions(self):
        """
        Creates list of functions alongside the starting parameters.

        :returns: Function definition list containing the model and its
                  starting parameter values
        :rtype: List of list
        """
        functions = []
        equation = self._parsed_func['name']
        starting_values = self._get_starting_values()
        value_ranges = self._get_value_ranges()
        param_names = [params[0] for params in starting_values]

        def fitFunction(x, *tmp_params):

            model = load_model(equation)

            data = empty_data1D(x)
            param_dict = {name: value
                          for name, value
                          in zip(param_names, tmp_params)}

            model_wrapper = Model(model, **param_dict)
            for name, values in value_ranges.items():
                model_wrapper.__dict__[name].range(values[0], values[1])
            func_wrapper = Experiment(data=data, model=model_wrapper)

            return func_wrapper.theory()

        for i in range(len(starting_values[0][1])):

            param_values = [params[1][i] for params in starting_values]

            functions.append([fitFunction, param_values])

        return functions
