"""
This file implements a parser for the Fitbenchmark data format.
"""

from __future__ import absolute_import, division, print_function

import os
from collections import OrderedDict

import numpy as np

from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.exceptions import MissingSoftwareError, ParsingError
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()

import_success = {}
try:
    import mantid.simpleapi as msapi
    import_success['mantid'] = (True, None)
except ImportError as ex:
    import_success['mantid'] = (False, ex)


try:
    from sasmodels.data import empty_data1D
    from sasmodels.core import load_model
    from sasmodels.bumps_model import Experiment, Model
    import_success['sasview'] = (True, None)
except ImportError as ex:
    import_success['sasview'] = (False, ex)


# By design the parsers may require many the private methods
# pylint: disable=too-many-branches
class FitbenchmarkParser(Parser):
    """
    Parser for the native FitBenchmarking problem definition (FitBenchmark)
    file.
    """

    def __init__(self, filename, options):
        super(FitbenchmarkParser, self).__init__(filename, options)

        self._entries = None
        self._parsed_func = None

    def parse(self):
        """
        Parse the Fitbenchmark problem file into a Fitting Problem.

        :return: The fully parsed fitting problem
        :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
        """
        # pylint: disable=attribute-defined-outside-init
        fitting_problem = FittingProblem(self.options)

        self._entries = self._get_data_problem_entries()
        software = self._entries['software'].lower()
        if not (software in import_success and import_success[software][0]):
            error = import_success[software][1]
            raise MissingSoftwareError('Requirements are missing for {} parser'
                                       ': {}'.format(software, error))

        self._parsed_func = self._parse_function()

        if software == 'mantid' and self._entries['input_file'][0] == '[':
            fitting_problem.multifit = True

        # NAME
        fitting_problem.name = self._entries['name']

        # DATA
        data_points = [_get_data_points(p) for p in self._get_data_file()]

        # FUNCTION
        if software == 'mantid':
            fitting_problem.function = self._create_mantid_function()
        elif software == 'sasview':
            fitting_problem.function = self._create_sasview_function()

        # EQUATION
        equation_count = len(self._parsed_func)
        if equation_count == 1:
            fitting_problem.equation = self._parsed_func[0]['name']
        else:
            fitting_problem.equation = '{} Functions'.format(equation_count)

        # STARTING VALUES
        fitting_problem.starting_values = self._get_starting_values()

        # PARAMETER RANGES
        vr = _parse_range(self._entries.get('parameter_ranges', ''))
        fitting_problem.value_ranges = vr if vr != {} else None

        # FIT RANGES
        fit_ranges_str = self._entries.get('fit_ranges', '')
        # this creates a list of strs like '{key: val, ...}' and parses each
        fit_ranges = [_parse_range('{' + r.split('}')[0] + '}')
                      for r in fit_ranges_str.split('{')[1:]]

        if fitting_problem.multifit:
            num_files = len(data_points)
            fitting_problem.data_x = [d[:, 0] for d in data_points]
            fitting_problem.data_y = [d[:, 1] for d in data_points]
            fitting_problem.data_e = [d[:, 2] if d.shape[1] > 2 else None
                                      for d in data_points]

            if not fit_ranges:
                fit_ranges = [{} for _ in range(num_files)]

            fitting_problem.start_x = [f['x'][0] if 'x' in f else None
                                       for f in fit_ranges]
            fitting_problem.end_x = [f['x'][1] if 'x' in f else None
                                     for f in fit_ranges]

        else:
            fitting_problem.data_x = data_points[0][:, 0]
            fitting_problem.data_y = data_points[0][:, 1]
            if data_points[0].shape[1] > 2:
                fitting_problem.data_e = data_points[0][:, 2]

            if fit_ranges and 'x' in fit_ranges[0]:
                fitting_problem.start_x = fit_ranges[0]['x'][0]
                fitting_problem.end_x = fit_ranges[0]['x'][1]

        if software == 'mantid':
            # String containing the function name(s) and the starting parameter
            # values for each function.
            fitting_problem.additional_info['mantid_equation'] \
                = self._entries['function']

            if fitting_problem.multifit:
                fitting_problem.additional_info['mantid_ties'] \
                    = self._parse_ties()

        return fitting_problem

    def _get_data_file(self):
        """
        Find/create the (full) path to a data_file specified in a FitBenchmark
        definition file, where the data_file is searched for in the directory
        of the definition file and subfolders of this file.

        :return: (full) path to a data file. Return None if not found
        :rtype: str or None
        """
        data_file_name = self._entries['input_file']
        if data_file_name.startswith('['):
            # Parse list assuming filenames do not have quote symbols or commas
            data_file_names = [
                d.replace('"', '').replace("'", '').strip('[').strip(']')
                for d in data_file_name.split(',')]
        else:
            data_file_names = [data_file_name]

        # find or search for path for data_file_name
        data_files = []
        for data_file_name in data_file_names:
            data_file = None
            for root, _, files in os.walk(os.path.dirname(self._filename)):
                for name in files:
                    if data_file_name == name:
                        data_file = os.path.join(root, data_file_name)

            if data_file is None:
                LOGGER.error("Data file %s not found", data_file_name)

            data_files.append(data_file)

        return data_files

    def _get_data_problem_entries(self):
        """
        Get the problem entries from a problem definition file.

        :return: The entries from the file with string values
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
        # pylint: disable=too-many-branches, too-many-statements
        function_def = []

        for f in self._entries['function'].split(';'):
            params_dict = OrderedDict()
            pop_stack = 0

            stack = [params_dict]
            for p in f.split(','):
                name, val = p.split('=', 1)
                name = name.strip()
                val = val.strip()

                l_count = val.count('(')
                r_count = val.count(')')
                if l_count > r_count:
                    # in brackets
                    # should be of the form 'varname=(othervar=3, ...)'

                    # Allow for nested brackets e.g. 'a=(b=(c=(d=1,e=2)))'
                    for _ in range(l_count - r_count):
                        # Cover case where formula mistyped
                        if '=' not in val:
                            raise ParsingError('Unbalanced brackets in '
                                               'function value: {}'.format(p))
                        # Must start with brackets
                        if val[0] != '(':
                            raise ParsingError('Bad placement of opening '
                                               'bracket in function: '
                                               '{}'.format(p))
                        # Create new dict for this entry and put at top of
                        # working stack
                        new_dict = OrderedDict()
                        stack[-1][name] = new_dict
                        stack.append(new_dict)
                        # Update name and val
                        name, val = val[1:].split('=', 1)
                elif l_count == r_count:
                    # Check if single item in brackets
                    while '=' in val:
                        if val[0] == '(' and val[-1] == ')':
                            val = val[1:-1]
                            new_dict = OrderedDict()
                            stack[-1][name] = new_dict
                            stack.append(new_dict)
                            name, val = val.split('=', 1)
                            pop_stack += 1
                        else:
                            raise ParsingError('Function value contains '
                                               'unexpected "=": {}'.format(p))
                elif l_count < r_count:
                    # exiting brackets
                    pop_stack = r_count - l_count
                    # must end with brackets
                    if val[-pop_stack:] != ')' * pop_stack:
                        raise ParsingError('Bad placement of closing bracket '
                                           'in function: {}'.format(p))
                    val = val[:-pop_stack]

                # Parse to an int/float if possible else assume string
                tmp_val = None
                for t in [int, float]:
                    if tmp_val is None:
                        try:
                            tmp_val = t(val)
                        except (ValueError, TypeError):
                            pass

                if tmp_val is not None:
                    val = tmp_val

                stack[-1][name] = val

                if pop_stack > 0:
                    if len(stack) <= pop_stack:
                        raise ParsingError('Too many closing brackets in '
                                           'function: {}'.format(p))
                    stack = stack[:-pop_stack]
                    pop_stack = 0

            if len(stack) != 1:
                raise ParsingError('Not all brackets are closed in function.')
            function_def.append(params_dict)

        return function_def

    def _get_starting_values(self):
        """
        Get the starting values for the problem

        :return: Starting values for the function
        :rtype: list of OrderedDict
        """
        # Mantid functions can have reserved keywords so ignore these as they
        # are not parameters.
        ignore = ['name', 'BinWidth', 'ties', 'Formula', 'constraints']

        name_template = '{1}' if len(self._parsed_func) == 1 else 'f{0}_{1}'
        starting_values = [
            OrderedDict([(name_template.format(i, name), val)
                         for i, f in enumerate(self._parsed_func)
                         for name, val in f.items()
                         if name not in ignore])]

        return starting_values

    def _create_mantid_function(self):
        """
        Processing the function in the FitBenchmark problem definition into a
        python callable.

        :return: A callable function
        :rtype: callable
        """
        fit_function = None

        for f in self._parsed_func:
            name = f['name']
            params = f.copy()
            for key in ['name', 'ties']:
                if key in params:
                    params.pop(key)
            tmp_function = msapi.__dict__[name](**params)
            if 'ties' in f:
                tmp_function.tie(f['ties'])
            if fit_function is None:
                fit_function = tmp_function
            else:
                fit_function += tmp_function

        return fit_function

    def _create_sasview_function(self):
        """
        Creates callable function

        :return: the model
        :rtype: callable
        """
        equation = self._parsed_func[0]['name']
        starting_values = self._get_starting_values()
        value_ranges = _parse_range(self._entries.get('parameter_ranges', ''))
        param_names = starting_values[0].keys()

        def fitFunction(x, *tmp_params):

            model = load_model(equation)

            data = empty_data1D(x)
            param_dict = dict(zip(param_names, tmp_params))

            model_wrapper = Model(model, **param_dict)
            if value_ranges is not None:
                for name, values in value_ranges.items():
                    model_wrapper.__dict__[name].range(values[0], values[1])
            func_wrapper = Experiment(data=data, model=model_wrapper)

            return func_wrapper.theory()

        return fitFunction

    def _parse_ties(self):
        try:
            ties = []
            for t in self._entries['ties'].split(','):
                # Strip out these chars
                for s in '[] "\'':
                    t = t.replace(s, '')
                ties.append(t)

        except KeyError:
            ties = []
        return ties


def _parse_range(range_str):
    """
    Parse a range string for the problem into a dict or list of dict if
    multi-fit.

    :param range_str: The a string to parse
    :type range_str: string

    :return: The ranges in a dictionary with key as the var and value as a
             list with min and max
             e.g. {'x': [0, 10]}
    :rtype: dict
    """
    if not range_str:
        return {}

    output_ranges = {}
    range_str = range_str.strip('{').strip('}')
    tmp_ranges = range_str.split(',')
    ranges = []
    cur_str = ''
    for r in tmp_ranges:
        cur_str += r
        balanced = True
        for lb, rb in ['[]', '{}', '()']:
            if cur_str.count(lb) > cur_str.count(rb):
                balanced = False
            elif cur_str.count(lb) < cur_str.count(rb):
                raise ParsingError(
                    'Unbalanced brackets in range: {}'.format(r))
        if balanced:
            ranges.append(cur_str)
            cur_str = ''
        else:
            cur_str += ','

    for r in ranges:
        name, val = r.split(':')
        name = name.strip().strip('"').strip("'").lower()

        # Strip off brackets and split on comma
        val = val.strip(' ')[1:-1].split(',')
        val = [v.strip() for v in val]
        try:
            pair = [float(val[0]), float(val[1])]
        except ValueError:
            raise ParsingError('Expected floats in range: {}'.format(r))

        if pair[0] >= pair[1]:
            raise ParsingError('Min value must be smaller than max value '
                               'in range: {}'.format(r))

        output_ranges[name] = pair

    return output_ranges


def _get_data_points(data_file_path):
    """
    Get the data points of the problem from the data file.

    :param data_file_path: The path to the file to load the points from
    :type data_file_path: str

    :return: data points
    :rtype: np.ndarray
    """

    with open(data_file_path, 'r') as f:
        data_text = f.readlines()

    # Find the line where data starts
    # i.e. the first line with a float on it
    first_row = 0

    # Loop until break statement
    while True:
        try:
            line = data_text[first_row].strip()
        except IndexError:
            raise ParsingError('Could not find data points')
        if line != '':
            x_val = line.split()[0]
            try:
                _ = float(x_val)
            except ValueError:
                pass
            else:
                break
        first_row += 1

    dim = len(data_text[first_row].split())
    data_points = np.zeros((len(data_text) - first_row, dim))

    for idx, line in enumerate(data_text[first_row:]):
        point_text = line.split()
        # Skip any values that can't be represented
        try:
            point = [float(val) for val in point_text]
        except ValueError:
            point = [np.nan for val in point_text]
        data_points[idx, :] = point

    # Strip all np.nan entries
    data_points = data_points[~np.isnan(data_points[:, 0]), :]

    return data_points
