from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from parsing.parse_nist import get_nist_model
from parsing.parse_nist import get_nist_starting_values
from parsing.parse_nist import get_data_pattern_txt
from parsing.parse_nist import parse_data_pattern
from parsing.parse_nist import parse_equation


class ParseNistTests(unittest.TestCase):

    def setup_misra1a_model_lines(self):

        lines = ["Model:         Exponential Class\n",
                 "               2 Parameters (b1 and b2)\n",
                 "\n",
                 "               y = b1*(1-exp[-b2*x])  +  e\n",
                 "\n"]

        return lines


    def setup_misra1a_startvals_lines(self):

        lines = ["\n",
                 "\n",
                 "  b1 =   500         250"
                 "           2.3894212918E+02  2.7070075241E+00",
                 "  b2 =     0.0001      0.0005"
                 "      5.5015643181E-04  7.2668688436E-06" ]

        return lines


    def setup_misra1a_data_pattern_text(self):

        data_pattern_text_expected = ['      10.07E0      77.6E0\n',
                                      '      14.73E0     114.9E0\n',
                                      '      17.94E0     141.1E0\n',
                                      '      23.93E0     190.8E0\n',
                                      '      29.61E0     239.9E0\n',
                                      '      35.18E0     289.0E0\n',
                                      '      40.02E0     332.8E0\n',
                                      '      44.82E0     378.4E0\n',
                                      '      50.76E0     434.8E0\n',
                                      '      55.05E0     477.3E0\n',
                                      '      61.01E0     536.8E0\n',
                                      '      66.40E0     593.1E0\n',
                                      '      75.47E0     689.1E0\n',
                                      '      81.78E0     760.0E0\n' ]

        return data_pattern_text_expected


    def setup_misra1a_expected_data_points(self):

        data_pattern = np.array([ [10.07, 77.6],
                                  [14.73, 114.9],
                                  [17.94, 141.1],
                                  [23.93, 190.8],
                                  [29.61, 239.9],
                                  [35.18, 289.0],
                                  [40.02, 332.8],
                                  [44.82, 378.4],
                                  [50.76, 434.8],
                                  [55.05, 477.3],
                                  [61.01, 536.8],
                                  [66.40, 593.1],
                                  [75.47, 689.1],
                                  [81.78, 760.0] ])

        return data_pattern


    def test_getNistModel_return_proper_eqtxt(self):

        lines = self.setup_misra1a_model_lines()
        idx = 0

        equation_text, idx = get_nist_model(lines, idx)
        equation_text_expected = 'y = b1*(1-exp[-b2*x])  +  e'
        idx_expected = 4

        self.assertEqual(equation_text_expected, equation_text)
        self.assertEqual(idx_expected, idx)


    def test_getNistModel_fail_runtimeError(self):

        lines = ["\n", "\n"]
        idx = 33

        self.assertRaises(RuntimeError, get_nist_model, lines, idx)


    def test_getNistStartingValues_return_proper_startvaltxt(self):

        lines = self.setup_misra1a_startvals_lines()
        idx = 0

        starting_vals, idx = get_nist_starting_values(lines, idx)
        starting_vals_expected = [['b1', [500.0,250.0]],
                                  ['b2', [0.0001,0.0005]]]
        idx = 3

        for idx in range(0, len(starting_vals_expected)):
            self.assertEqual(starting_vals_expected[idx][0],
                             starting_vals[idx][0])
            self.assertListEqual(starting_vals_expected[idx][1],
                                 starting_vals[idx][1])


    def test_getNistStartingValues_fail_startvals_invalid(self):

        lines = ["\n",
                 "\n",
                 "  b1 =   500         250   ",
                 "  b2 =     0.0001      0.0005"
                 "      5.5015643181E-04  7.2668688436E-06" ]
        idx = 0

        self.assertRaises(RuntimeError, get_nist_starting_values, lines, idx)


    def test_parseDataPattern_return_parsed_data_pattern_array(self):

        data_pattern_text = self.setup_misra1a_data_pattern_text()

        data_points = parse_data_pattern(data_pattern_text)
        data_points_expected = self.setup_misra1a_expected_data_points()

        np.testing.assert_array_equal(data_points_expected, data_points)


    def test_parseEquation_return_proper_equation_form(self):

        equation_text = 'y = b1*(1-exp[-b2*x])  +  e'

        equation = parse_equation(equation_text)
        equation_expected = 'b1*(1-exp(-b2*x))'

        self.assertEqual(equation_expected, equation)

    def test_parseEquation_fail_runtimeError(self):

        equation_text = 'LULy = bf1*(1-exdsp[-b2as*x])  +  e'

        self.assertRaises(RuntimeError, parse_equation, equation_text)


if __name__ == "__main__":
    unittest.main()
