"""
This file implements a parser for the Fitbenchmark data format.
"""

from __future__ import (absolute_import, division, print_function)

from collections import OrderedDict
import mantid.simpleapi as msapi
import numpy as np
import os

from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.logging_setup import logger


class FitbenchmarkParser(Parser):
    """
    Parser for the native FitBenchmarking problem definition (FitBenchmark)
    file.
    """

    def parse(self):
        """
        Parse the Fitbenchmark problem file into a Fitting Problem.

        :return: The fully parsed fitting problem
        :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
        """
        fitting_problem = FittingProblem()

        self._entries = self._get_fitbenchmark_data_problem_entries()
        self._parsed_func = self._parse_function()

        fitting_problem.name = self._entries['name']

        data_points = self._get_data_points()

        fitting_problem.data_x = data_points[:, 0]
        fitting_problem.data_y = data_points[:, 1]
        if data_points.shape[1] > 2:
            fitting_problem.data_e = data_points[:, 2]

        # String containing the function name(s) and the starting parameter
        # values for each function
        self._mantid_equation = self._entries['function']

        fitting_problem.function = self._fitbenchmark_func_definition()

        # Print number of equations until better way of doing this is looked at
        equation_count = len(self._parsed_func)
        fitting_problem.equation = '{} Functions'.format(equation_count)

        fitting_problem.starting_values = self._get_starting_values()

        # start and end values in x range
        if 'fit_parameters' in self._entries:
            start_x, end_x = self._get_x_range()
            fitting_problem.start_x = start_x
            fitting_problem.end_x = end_x

        return fitting_problem

    def _get_data_file(self):
        """
        Find/create the (full) path to a data_file specified in a FitBenchmark
        definition file, where the data_file is searched for in the directory
        of the definition file and subfolders of this file

        :returns: (full) path to a data file. Return None if not found
        :rtype: str or None
        """
        data_file = None
        data_file_name = self._entries['input_file']
        # find or search for path for data_file_name
        for root, _, files in os.walk(os.path.dirname(self._filename)):
            for name in files:
                if data_file_name == name:
                    data_file = os.path.join(root, data_file_name)

        if data_file is None:
            logger.error("Data file %s not found", data_file_name)

        return data_file

    def _get_fitbenchmark_data_problem_entries(self):
        """
        Get the problem entries from a fitbenchmark problem definition
        file.

        :returns: The entries from the file with string values
        :rtype: dict
        """

        entries = {}
        for line in self.file.readlines():
            # Discard comments
            line = line.split('#', 1)[0]
            if line.strip() == '':
                continue

            lhs, rhs = line.split("=", 1)
            entries[lhs.strip()] = rhs.strip().strip('"').strip("'")

        return entries

    def _parse_function(self):
        """
        Get the params from the function as a list of dicts from the data
        file.

        :return: Function definition in format:
                 [{name1: value1, name2: value2, ...}, ...]
        :rtype: list of dict
        """
        function_def = []

        functions = self._entries['function'].split(';')

        for f in functions:
            params_dict = OrderedDict()
            # To handle brackets, must split on comma or split after an
            # opening backet
            tmp_params_list = f.split(',')
            if '(' in f:
                params_list = []
                for p in tmp_params_list:
                    if '(' in p:
                        vals = [v+'(' for v in p.split('(', 1)]
                        vals[-1] = vals[-1][:-1]
                        params_list.extend(vals)
                    else:
                        params_list.append(p)
            else:
                params_list = tmp_params_list

            pop_stack = False
            stack = [params_dict]
            for p in params_list:
                name, val = p.split('=', 1)
                name = name.strip()
                val = val.strip()

                if val == '(':
                    val = OrderedDict()
                    stack[-1][name] = val
                    stack += [val]
                    continue

                elif val[-1] == ')':
                    pop_stack = val.count(')')
                    if len(stack) <= pop_stack:
                        raise ValueError('Could not parse.'
                                         + 'Check parentheses in input')
                    val = val.strip(')')

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

                if pop_stack > 0:
                    stack = stack[:-pop_stack]
                    pop_stack = 0

            function_def.append(params_dict)

        return function_def

    def _get_data_points(self):
        """
        Get the data points of the problem from the data file.

        :return: data points
        :rtype: np.ndarray
        """

        data_file_path = self._get_data_file()

        with open(data_file_path, 'r') as f:
            data_text = f.readlines()

        first_row = data_text[2].strip()
        dim = len(first_row.split())
        data_points = np.zeros((len(data_text)-2, dim))

        for idx, line in enumerate(data_text[2:]):
            point_text = line.split()
            point = [float(val) for val in point_text]
            data_points[idx, :] = point

        return data_points

    def _get_starting_values(self):
        """
        Get the starting values for the problem

        :returns: Starting values for the function
        :rtype: list of OrderedDict
        """
        ignore = ['name', 'BinWidth', 'ties']

        starting_values = [
            OrderedDict([('f{}_{}'.format(i, name), f[name])
                         for i, f in enumerate(self._parsed_func)
                         for name in f.keys()
                         if name not in ignore])]

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

    def _fitbenchmark_func_definition(self):
        """
        Processing the function in the FitBenchmark problem definition into a
        python callable.

        :returns: A callable function
        :rtype: callable
        """
        fit_function = None

        for f in self._parsed_func:
            name = f['name']
            params = f.copy()
            for key in ['name', 'BinWidth', 'ties']:
                if key in params:
                    params.pop(key)
            tmp_function = msapi.__dict__[name](**params)
            if fit_function is None:
                fit_function = tmp_function
            else:
                fit_function += tmp_function

        for i, f in enumerate(self._parsed_func):
            if 'ties' in f:
                ties = {'f{}.{}'.format(i, tie): val
                        for tie, val in f['ties'].items()}
                fit_function.tie(ties)

        return fit_function
