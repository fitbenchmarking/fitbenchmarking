"""
Parse input files describing fitting test examples and load the
information into problem objects

"""
# Copyright &copy; 2016 ISIS Rutherford Appleton Laboratory, NScD
# Oak Ridge National Laboratory & European Spallation Source
#
# This file is part of Mantid.
# Mantid is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Mantid is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# File change history is stored at: <https://github.com/mantidproject/mantid>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>

from __future__ import (absolute_import, division, print_function)

import os
import numpy as np
import re
from parsing import fitbm_problem

from utils.logging_setup import logger


class FittingProblem(fitbm_problem.BaseFittingProblem):
    """
    Definition of the NIST problem class

    Types of data:
        - strings: name, type, equation
        - floats: start_x, end_x, ref_residual_sum_sq
        - numpy arrays: data_x, data_y, data_e
        - arrays: starting_values
    """

    def __init__(self, fname):

        super(FittingProblem, self).__init__(fname)
        super(FittingProblem, self).read_file()

        equation_text, data_pattern_text, starting_values, \
            residual_sum_sq = self.parse_line_by_line(self.contents)
        data_pattern = self.parse_data_pattern(data_pattern_text)

        self._data_x = data_pattern[:, 1]
        self._data_y = data_pattern[:, 0]

        self._ref_residual_sum_sq = 0

        self._name = os.path.basename(self.contents.name.split('.')[0])
        self._equation = self.parse_equation(equation_text)
        self._type = "NIST"

        self._starting_values = starting_values
        # self._start_x = entries['fit_parameters']['StartX']
        # self._end_x = entries['fit_parameters']['EndX']

        super(FittingProblem, self).close_file()

    def store_prob_details(self, spec_file, parsed_eq, starting_values, data_pattern,
                           residual_sum_sq):
        """
        Helper function that stores all the parsed nist problem definiton
        information into a problem object.

        @param spec_file :: path to the nist problem definition file
                            that is being loaded
        @param parsed_eq :: the equation used in fitting the problem
        @param starting_values :: the starting values from where the
                                  fitting will commence
        @param data_pattern :: numpy array containing the raw data
        @param residual_sum_sq :: a reference sum of all the residuals squared
                                  of the fit
        """

        prob = fitbm_problem.FittingProblem(spec_file)
        prob.equation = parsed_eq
        prob.starting_values = starting_values
        prob.ref_residual_sum_sq = residual_sum_sq

        return prob

    def parse_line_by_line(self, contents):
        """
        Parses the NIST file one line at the time. Very unstable parser
        but gets the job done.

        @param lines :: array of all the lines in the imported nist file

        @returns :: strings of the equation, data pattern, array of starting
                    values and the reference residual sum from the file
        """
        lines = contents.readlines()
        idx, ignored_lines, residual_sum_sq = 0, 0, 0

        while idx < len(lines):
            line = lines[idx].strip()
            idx += 1
            if not line:
                continue

            if line.startswith('Model:'):
                equation_text, idx = self.get_nist_model(lines, idx)
            elif 'Starting values' in line or 'Starting Values' in line:
                starting_values, idx = self.get_nist_starting_values(lines, idx)
            elif line.startswith('Residual Sum of Squares'):
                residual_sum_sq = float(line.split()[4])
            elif line.startswith("Data:"):
                if " x" in line and " y " in line:
                    data_pattern_text, idx = self.get_data_pattern_txt(lines, idx)
            else:
                ignored_lines += 1
                # print("unknown line in supposedly NIST test file, ignoring: {0}".
                #       format(line))

        logger.info("%d lines were ignored in this problem file.\n"
                    "If any problems occur, please uncomment line above this print "
                    "to display the full output." % ignored_lines)

        return equation_text, data_pattern_text, starting_values, residual_sum_sq

    def get_nist_model(self, lines, idx):
        """
        Gets the model equation used in the fitting process from the
        NIST file.

        @param lines :: array of all the lines in the imported nist file
        @param idx :: the line at which the parser is at

        @returns :: string of the equation from the NIST file and the
                    new index
        """

        equation_text, idxerr = None, False
        try:
            while (not re.match(r'\s*y\s*=(.+)', lines[idx])
                   and not re.match(r'\s*log\[y\]\s*=(.+)', lines[idx]))\
                    and idx < len(lines):

                idx += 1
        except IndexError as err:
            logger.error("Could not find equation, index went out of bounds!")
            idxerr = True

        equation_text, idx = self.get_equation_text(lines, idxerr, idx)

        return equation_text, idx

    def get_equation_text(self, lines, idxerr, idx):
        """
        Gets the equation text from the NIST file.

        @param lines :: array of all the lines in the imported nist file
        @param idxerr :: boolean that points out if there were any problems
                         in finding the equation in the file
        @param idx :: the line at which the parser is at

        @returns :: string of the equation from the NIST file and the
                    new index
        """

        # Next non-empty lines are assumed to continue the equation
        equation_text = ''
        if idxerr is False:
            while lines[idx].strip():
                equation_text += lines[idx].strip()
                idx += 1

        if not equation_text:
            raise RuntimeError("Could not find the equation!")

        return equation_text, idx

    def get_data_pattern_txt(self, lines, idx):
        """
        Gets the data pattern from the NIST problem file.

        @param lines :: array of all the lines in the imported nist file
        @param idx :: the line at which the parser is at

        @returns :: string of the data pattern and the new index
        """

        data_pattern_text = None
        data_pattern_text = lines[idx:]
        idx = len(lines)

        if not data_pattern_text:
            raise RuntimeError("Could not find the data!")

        return data_pattern_text, idx

    def parse_data_pattern(self, data_pattern_text):
        """
        Parses the data pattern string and returns a numpy array of the
        data points of the problem.

        @param data_pattern_text :: string of the data pattern from the
                                    NIST problem file

        @returns :: numpy array of the data points of the problem
        """

        if not data_pattern_text:
            return None

        first = data_pattern_text[0].strip()
        dim = len(first.split())
        data_points = np.zeros((len(data_pattern_text), dim))

        for idx, line in enumerate(data_pattern_text):
            line = line.strip()
            point_text = line.split()
            point = [float(val) for val in point_text]
            data_points[idx, :] = point

        return data_points

    def parse_equation(self, eq_text):
        """
        Parses the equation and converts it to the right format.

        @param eq_text :: string of the equation

        @returns :: formatted equation string
        """

        start_normal = r'\s*y\s*=(.+)'
        if re.match(start_normal, eq_text):
            match = re.search(r'y\s*=(.+)\s*\+\s*e', eq_text)
            equation = match.group(1).strip()
        else:
            raise RuntimeError("Unrecognized equation syntax when trying to parse "
                               "a NIST equation: " + eq_text)

        equation = self.convert_nist_to_muparser(equation)
        return equation

    def convert_nist_to_muparser(self, equation):
        """
        Converts the raw equation from the NIST file into muparser format.

        @param equation :: string of the raw equation

        @returns :: formatted muparser equation
        """

        # 'NIST equation syntax' => muparser syntax
        equation = equation.replace('[', '(')
        equation = equation.replace(']', ')')
        equation = equation.replace('arctan', 'atan')
        equation = equation.replace('**', '^')
        return equation

    def get_nist_starting_values(self, lines, idx):
        """
        Gets the function starting values from the NIST problem file.

        @param lines :: array of all the lines in the imported nist file
        @param idx :: the line at which the parser is at

        @returns :: an array of the starting values and the new index
        """

        starting_values = None
        idx += 2
        starting_values = self.parse_starting_values(lines[idx:])
        idx += len(starting_values)

        return starting_values, idx

    def parse_starting_values(self, lines):
        """
        Parses the starting values of a NIST file and converts them into an
        array.

        @param lines :: array of all the lines in the imported nist file

        @returns :: array of the starting values used in NIST problem
        """
        starting_vals = []
        for line in lines:
            if not line.strip() or line.startswith('Residual'):
                break

            startval_str = line.split()
            self.check_startval_validity(startval_str, line)
            alt_values = self.get_startvals_floats(startval_str)
            starting_vals.append([startval_str[0], alt_values])

        return starting_vals

    def check_startval_validity(self, startval_str, line):
        """
        Checks the validity of the starting value raw string.
        There can only be 2 cases when parsing nist files
        i.e. line can only have six or 7 strings separated by white space.

        @param startval_str :: raw string of the starting values
        """

        if 6 != len(startval_str) and 5 != len(startval_str):
            raise RuntimeError("Failed to parse this line as starting "
                               "values information: {0}".format(line))

    def get_startvals_floats(self, startval_str):
        """
        Converts the starting values into floats.

        @param startval_str :: string of raw starting values

        @returns :: starting values array of floats
        """

        # A bit weak/lax parsing, if there is one less column,
        # assume only one start point
        if 6 == len(startval_str):
            alt_values = [float(startval_str[2]), float(startval_str[3])]
        elif 5 == len(startval_str):
            alt_values = [float(startval_str[2])]

        return alt_values
