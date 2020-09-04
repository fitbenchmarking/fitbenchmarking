"""
This file implements a parser for the NIST style data format.
"""

from __future__ import (absolute_import, division, print_function)

from collections import OrderedDict
import re

import numpy as np

from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.parsing.nist_data_functions import nist_func_definition
from fitbenchmarking.utils.exceptions import ParsingError
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


# By design the parsers may have functions that do not necessarily use self
# within them
# pylint: no-self-use
class NISTParser(Parser):
    """
    Parser for the NIST problem definition file.
    """

    def parse(self):
        """
        Parse the NIST problem file into a Fitting Problem.

        :return: The fully parsed fitting problem
        :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
        """

        fitting_problem = FittingProblem(self.options)

        equation, data, starting_values, name = self._parse_line_by_line()
        data = self._parse_data(data)

        fitting_problem.data_x = data[:, 1]
        fitting_problem.data_y = data[:, 0]
        if len(data[0, :]) > 2:
            fitting_problem.data_e = data[:, 2]

        fitting_problem.name = name

        # String containing a mathematical expression
        fitting_problem.equation = self._parse_equation(equation)

        fitting_problem.starting_values = starting_values

        fitting_problem.function = \
            nist_func_definition(function=fitting_problem.equation,
                                 param_names=starting_values[0].keys())
        return fitting_problem

    def _parse_line_by_line(self):
        """
        Parses the NIST file one line at the time.

        :return: the equation, data pattern, and starting values
                 sections of the file
        :rtype: str, str, list of list of float
        """
        lines = self.file.readlines()
        idx, ignored_lines = 0, 0

        while idx < len(lines):
            line = lines[idx].strip()
            idx += 1
            if not line:
                continue

            if line.startswith('Model:'):
                equation_text, idx = self._get_nist_model(lines, idx)
            elif 'Starting values' in line or 'Starting Values' in line:
                starting_values, idx = self._get_nist_starting_values(lines,
                                                                      idx)
            elif line.startswith("Data:"):
                if " x" in line and " y " in line:
                    data_pattern_text, idx = self._get_data_txt(lines, idx)
            elif line.startswith("Dataset Name:"):
                name = line.split(':', 1)[1]
                name = name.split('(', 1)[0]
                name = name.strip()
            else:
                ignored_lines += 1

        LOGGER.debug("%s lines were ignored in this problem file",
                     ignored_lines)

        return equation_text, data_pattern_text, starting_values, name

    def _get_nist_model(self, lines, idx):
        """
        Gets the model equation used in the fitting process from the
        NIST file.

        :param lines: All lines in the imported nist file
        :type lines: list of str
        :param idx: the line at which the parser is at
        :type idx: int

        :return: The equation from the NIST file and the
                 new index
        :rtype: str and int
        """

        equation_text, idxerr = None, False
        try:
            while (not re.match(r'\s*y\s*=(.+)', lines[idx])
                   and not re.match(r'\s*log\[y\]\s*=(.+)', lines[idx]))\
                    and idx < len(lines):

                idx += 1
        except IndexError:
            LOGGER.error("Could not find equation, index went out of bounds!")
            idxerr = True

        equation_text, idx = self._get_equation_text(lines, idxerr, idx)

        return equation_text, idx

    def _get_equation_text(self, lines, idxerr, idx):
        """
        Gets the equation text from the NIST file.

        :param lines: All lines in the imported nist file
        :type lines: list of str
        :param idxerr: boolean that points out if there were any problems
                       in finding the equation in the file
        :type idxerr: bool
        :param idx: the line at which the parser is at
        :type idx: int

        :return: The equation from the NIST file and the
                 new index
        :rtype: str and int
        """

        # Next non-empty lines are assumed to continue the equation
        equation_text = ''
        if idxerr is False:
            while lines[idx].strip():
                equation_text += lines[idx].strip()
                idx += 1

        if not equation_text:
            raise ParsingError("Could not find the equation!")

        return equation_text, idx

    def _get_data_txt(self, lines, idx):
        """
        Gets the data pattern from the NIST problem file.

        :param lines: All lines in the imported nist file
        :type lines: list of str
        :param idx: the line at which the parser is at
        :type idx: int

        :return: The data pattern and the new index
        :rtype: (list of str) and int
        """

        data_text = None
        data_text = lines[idx:]
        idx = len(lines)

        if not data_text:
            raise ParsingError("Could not find the data!")

        return data_text, idx

    def _parse_data(self, data_text):
        """
        Parses the data string and returns a numpy array of the
        data points of the problem.

        :param data_text: The data from the NIST problem file
        :type data_text: list of str

        :return: The data points of the problem
        :rtype: np.ndarray
        """

        if not data_text:
            return None

        first = data_text[0].strip()
        dim = len(first.split())
        data_points = np.zeros((len(data_text), dim))

        for idx, line in enumerate(data_text):
            line = line.strip()
            point_text = line.split()
            point = [float(val) for val in point_text]
            data_points[idx, :] = point

        data_points = self._sort_data_from_x_data(data_points)

        return data_points

    def _sort_data_from_x_data(self, data_points):
        """
        Sort the numpy array of the data points of the problem
        using its x data.

        :param data_points: Unsorted data points of the problem
        :type data_points: np.ndarray

        :return: sorted data points of the problem
        :rtype: np.ndarray
        """

        sorted_data_points = sorted(data_points, key=lambda x: x[1])

        return np.asarray(sorted_data_points)

    def _parse_equation(self, eq_text):
        """
        Parses the equation and converts it to the right format.

        :param eq_text: The equation
        :type eq_text: str

        :return: formatted equation
        :rtype: str
        """

        start_normal = r'\s*y\s*=(.+)'
        if re.match(start_normal, eq_text):
            match = re.search(r'y\s*=(.+)\s*\+\s*e', eq_text)
            equation = match.group(1).strip()
        else:
            raise ParsingError("Unrecognized equation syntax when trying to "
                               "parse a NIST equation: " + eq_text)

        equation = self._convert_nist_to_muparser(equation)
        return equation

    def _convert_nist_to_muparser(self, equation):
        """
        Converts the raw equation from the NIST file into muparser format.

        :param equation: Raw equation
        :type equation: str

        :return: formatted muparser equation (mathematical notation)
        :rtype: str
        """

        # 'NIST equation syntax' => muparser syntax
        equation = equation.replace('[', '(')
        equation = equation.replace(']', ')')
        equation = equation.replace('arctan', 'atan')
        equation = equation.replace('**', '^')
        return equation

    def _get_nist_starting_values(self, lines, idx):
        """
        Gets the function starting values from the NIST problem file.

        :param lines: The lines in the imported nist file
        :type lines: list of str
        :param idx: the line at which the parser is at
        :type idx: int

        :return: The starting values and the new index
        :rtype: (list of OrderedDict) and int
        """

        starting_values = None
        idx += 2
        starting_values = self._parse_starting_values(lines[idx:])
        idx += len(starting_values)

        return starting_values, idx

    def _parse_starting_values(self, lines):
        """
        Parses the starting values of a NIST file and converts them into an
        array.

        :param lines: All lines in the imported nist file
        :type lines: list of str

        :return: The starting values used in NIST problem
        :rtype: list of list of float
        """
        starting_vals = []
        for line in lines:
            if not line.strip() or line.startswith('Residual'):
                break

            startval_str = line.split()
            if not startval_str[0].isalnum():
                raise ParsingError('Could not parse starting parameters.')

            alt_values = self._get_startvals_floats(startval_str)

            if not starting_vals:
                starting_vals = [OrderedDict() for _ in alt_values]
            for i, a in enumerate(alt_values):
                starting_vals[i][startval_str[0]] = a

        return starting_vals

    def _get_startvals_floats(self, startval_str):
        """
        Converts the starting values into floats.

        :param startval_str: Unparsed starting values
        :type startval_str: list of str

        :return: Starting values array of floats
        :rtype: list of float
        """

        # A bit weak/lax parsing, if there is one less column,
        # assume only one start point
        if len(startval_str) == 6:
            alt_values = [float(startval_str[2]), float(startval_str[3])]
        elif len(startval_str) == 5:
            alt_values = [float(startval_str[2])]
        # In the NIST format this can only contain 5 or 6 columns
        else:
            raise ParsingError("Failed to parse this line as starting "
                               "values information: {0}".format(startval_str))

        return alt_values
