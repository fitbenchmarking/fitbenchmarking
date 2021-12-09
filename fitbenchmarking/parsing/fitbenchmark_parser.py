"""
This file implements a parser for the Fitbenchmark data format.
"""
from collections import OrderedDict

import os
import typing
import numpy as np

from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.exceptions import ParsingError
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


class FitbenchmarkParser(Parser):
    """
    Parser for the native FitBenchmarking problem definition (FitBenchmark)
    file.
    """

    def __init__(self, filename, options):
        super().__init__(filename, options)

        self._parsed_func: list = None
        self._entries: dict = None

    def parse(self) -> FittingProblem:
        """
        Parse the Fitbenchmark problem file into a Fitting Problem.

        :return: The fully parsed fitting problem
        :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
        """
        self._entries = self._get_data_problem_entries()

        # pylint: disable=attribute-defined-outside-init
        self.fitting_problem = FittingProblem(self.options)

        self._parsed_func = self._parse_function()

        self.fitting_problem.multifit = self._is_multifit()

        self.fitting_problem.name = self._entries['name']
        self.fitting_problem.description = self._entries['description']

        data_points = [_get_data_points(p) for p in self._get_data_file()]

        self.fitting_problem.function = self._create_function()
        self.fitting_problem.format = self._entries['software'].lower()

        # If using a multivariate function wrap the call to take a single
        # argument
        if len(data_points[0]['x'].shape) > 1:
            old_function = self.fitting_problem.function
            all_data = []
            count = 0
            for dp in data_points:
                all_data.append(dp['x'])
                dp['x'] = np.arange(count, count + dp['x'].shape[0])
                count = count + dp['x'].shape[0]
            all_data = np.concatenate(all_data)

            def new_function(x, *p):
                inp = all_data[x]
                return old_function(inp, *p)

            self.fitting_problem.function = new_function
            self.fitting_problem.multivariate = True

        # Set this flag if the output is non-scalar either
        if len(data_points[0]['y'].shape) > 2:
            self.fitting_problem.multivariate = True

        # EQUATION
        self.fitting_problem.equation = self._get_equation()

        # STARTING VALUES
        self.fitting_problem.starting_values = self._get_starting_values()

        # PARAMETER RANGES
        # Creates list containing tuples of lower and upper bounds
        # (lb,ub) for each parameter
        vr = _parse_range(self._entries.get('parameter_ranges', ''))
        if vr:
            self.fitting_problem.set_value_ranges(vr)

        # FIT RANGES
        fit_ranges_str = self._entries.get('fit_ranges', '')
        # this creates a list of strs like '{key: val, ...}' and parses each
        fit_ranges = [_parse_range('{' + r.split('}')[0] + '}')
                      for r in fit_ranges_str.split('{')[1:]]

        self._set_data_points(data_points, fit_ranges)

        self._set_additional_info()

        return self.fitting_problem

    @staticmethod
    def _is_multifit() -> bool:
        """
        Returns true if the problem is a multi fit problem.

        :return: True if the problem is a multi fit problem.
        :rtype: bool
        """
        return False

    def _create_function(self) -> typing.Callable:
        """
        Creates a python callable which is a wrapper around the fit function.
        """
        raise NotImplementedError

    def _get_equation(self) -> str:
        """
        Returns the equation in the problem definition file.

        :return: The equation in the problem definition file.
        :rtype: str
        """
        equation_count = len(self._parsed_func)
        if equation_count == 1:
            return self._parsed_func[0]['name']
        return f"{equation_count} Functions"

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        # SasView functions can have reserved keywords so ignore these
        ignore = ['name']

        starting_values = [
            OrderedDict([(name, val)
                         for name, val in self._parsed_func[0].items()
                         if name not in ignore])]

        return starting_values

    def _set_data_points(self, data_points: list, fit_ranges: list) -> None:
        """
        Sets the data points and fit range data in the fitting problem.

        :param data_points: A list of data points.
        :type data_points: list
        :param fit_ranges: A list of fit ranges.
        :type fit_ranges: list
        """
        self.fitting_problem.data_x = data_points[0]['x']
        self.fitting_problem.data_y = data_points[0]['y']
        if 'e' in data_points[0]:
            self.fitting_problem.data_e = data_points[0]['e']

        if fit_ranges and 'x' in fit_ranges[0]:
            self.fitting_problem.start_x = fit_ranges[0]['x'][0]
            self.fitting_problem.end_x = fit_ranges[0]['x'][1]

    def _set_additional_info(self) -> None:
        # pylint: disable=no-self-use
        """
        Sets any additional info for a fitting problem.
        """
        return

    def _get_data_file(self):
        """
        Find/create the (full) path to a data_file(s) specified in a
        FitBenchmark definition file, where the data_file is searched for in
        the directory of the definition file and subfolders of this file.

        :return: (full) path to a data file. Return None if not found
        :rtype: list<str>
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
        except ValueError as e:
            raise ParsingError('Expected floats in range: {}'.format(r)) from e

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

    :return: data
    :rtype: dict<str, np.ndarray>
    """

    with open(data_file_path, 'r') as f:
        data_text = f.readlines()

    first_row = _find_first_line(data_text)
    dim = len(data_text[first_row].split())
    cols = _get_column_data(data_text, first_row, dim)

    if not cols['x'] or not cols['y']:
        raise ParsingError('Input files need both X and Y values.')
    if cols['e'] and len(cols['y']) != len(cols['e']):
        raise ParsingError('Error must be of the same dimension as Y.')

    data_points = np.zeros((len(data_text) - first_row, dim))

    for idx, line in enumerate(data_text[first_row:]):
        point_text = line.split()
        # Skip any values that can't be represented
        try:
            point = [float(val) for val in point_text]
        except ValueError:
            point = [np.nan for _ in point_text]
        data_points[idx, :] = point

    # Strip all np.nan entries
    data_points = data_points[~np.isnan(data_points[:, 0]), :]

    # Split into x, y, and e
    data = {key: data_points[:, cols[key]]
            for key in ['x', 'y']}
    if cols['e']:
        data['e'] = data_points[:, cols['e']]

    # Flatten if the columns are 1D
    for key, col in cols.items():
        if len(col) == 1:
            data[key] = data[key].flatten()

    return data


def _find_first_line(file_lines: "list[str]") -> int:
    """
    Finds the first line where the data starts i.e. the
    first line with a float on it.

    :param file_lines: A list of lines from a file.
    :type file_lines: A list of strings.

    :return: index of the first file line with data.
    :rtype: int
    """
    for i, line in enumerate(file_lines):
        line = line.strip()
        if not line:
            continue
        try:
            float(line.split()[0])
        except ValueError:
            continue
        return i

    raise ParsingError('Could not find data points')


def _get_column_data(file_lines: "list[str]", first_row: int,
                     dim: int) -> list:
    """
    Gets the data in the file as a dictionary of x, y and e data.

    :param file_lines: A list of lines from a file.
    :type file_lines: A list of strings.
    :param first_row: Index of the first line in the file containing data.
    :type first_row: int
    :param dim: The number of columns in the file.
    :type dim: int

    :return: index of the first file line with data.
    :rtype: int
    """
    cols = {'x': [],
            'y': [],
            'e': []}
    num_cols = 0
    if first_row != 0:
        header = file_lines[0].split()
        for heading in header:
            if heading == '#':
                continue
            if heading[0] == '<' and heading[-1] == '>':
                heading = heading[1:-1]
            col_type = heading[0].lower()
            if col_type in ['x', 'y', 'e']:
                cols[col_type].append(num_cols)
                num_cols += 1
            else:
                raise ParsingError(
                    'Unrecognised header line, header names must start with '
                    '"x", "y", or "e".'
                    'Examples are: '
                    '"# X Y E", "#   x0 x1 y e", "# X0 X1 Y0 Y1 E0 E1", '
                    '"<X> <Y> <E>", "<X0> <X1> <Y> <E>"...')
        if dim != num_cols:
            raise ParsingError('Could not match header to columns.')
    else:
        cols['x'], cols['y'] = [0], [1]
        if dim == 3:
            cols['e'] = [2]
        elif dim != 2:
            raise ParsingError(
                'Cannot infer size of inputs and outputs in datafile. '
                'Headers are required when not using 1D inputs and outputs.')
    return cols
