from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

# Delete four lines below when automated tests are enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from parsing.parse import parse_problem_file
from parsing.parse_nist_data import FittingProblem
from mock_problem_files.get_problem_files import get_file


class ParseNistTests(unittest.TestCase):

    def setup_misra1a_data_pattern_lines(self):

        lines = ['Data:   y               x',
                 '10.07E0      77.6E0',
                 '14.73E0     114.9E0',
                 '17.94E0     141.1E0',
                 '23.93E0     190.8E0',
                 '29.61E0     239.9E0',
                 '35.18E0     289.0E0',
                 '40.02E0     332.8E0',
                 '44.82E0     378.4E0',
                 '50.76E0     434.8E0',
                 '55.05E0     477.3E0',
                 '61.01E0     536.8E0',
                 '66.40E0     593.1E0',
                 '75.47E0     689.1E0',
                 '81.78E0     760.0E0'
                 ]

        return lines

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
                 "      5.5015643181E-04  7.2668688436E-06"]

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
                                      '      81.78E0     760.0E0\n']

        return data_pattern_text_expected

    def setup_misra1a_expected_data_points(self):

        data_pattern = np.array([[10.07, 77.6],
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
                                 [81.78, 760.0]])

        return data_pattern

    def setup_misra1a_expected_data_points_with_data_e(self):

        data_pattern = np.array([[10.07, 77.6, 0.1],
                                 [14.73, 114.9, 0.1],
                                 [17.94, 141.1, 0.1],
                                 [23.93, 190.8, 0.1],
                                 [29.61, 239.9, 0.1],
                                 [35.18, 289.0, 0.1],
                                 [40.02, 332.8, 0.1],
                                 [44.82, 378.4, 0.1],
                                 [50.76, 434.8, 0.1],
                                 [55.05, 477.3, 0.1],
                                 [61.01, 536.8, 0.1],
                                 [66.40, 593.1, 0.1],
                                 [75.47, 689.1, 0.1],
                                 [81.78, 760.0, 0.1]])

        return data_pattern

    def setup_nist_expected_problem(self):
        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)
        prob.name = 'NIST_Misra1a'
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0, 250.0]], ['b2', [0.0001, 0.0005]]]
        data_pattern = self.setup_misra1a_expected_data_points()
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]

        return prob

    def test_eval_f(self):

        fname = get_file('NIST_Misra1a.dat')
        problem = FittingProblem(fname)

        y_values = problem.eval_f(problem.data_x,[0.0001,0.0005])

        y_values_expected = np.array([3.80569215e-06, 5.58309023e-06, 6.81188557e-06, 9.09907420e-06,
                            1.13035216e-05, 1.34545088e-05, 1.53292517e-05, 1.72379034e-05,
                            1.95391938e-05, 2.12309474e-05, 2.35398121e-05, 2.56621543e-05,
                            2.91460876e-05, 3.16138591e-05])

        np.testing.assert_allclose(y_values_expected, y_values, rtol=1e-5, atol=0)

    def test_getFunction_returns_correct_function(self):

        fname = get_file('NIST_Misra1a.dat')
        problem = FittingProblem(fname)

        function = problem.get_function()

        function_obj = function[0][0]

        y_values = function_obj(problem.data_x,0.0001,0.0005)

        y_values_expected = np.array([3.80569215e-06, 5.58309023e-06, 6.81188557e-06, 9.09907420e-06,
                            1.13035216e-05, 1.34545088e-05, 1.53292517e-05, 1.72379034e-05,
                            1.95391938e-05, 2.12309474e-05, 2.35398121e-05, 2.56621543e-05,
                            2.91460876e-05, 3.16138591e-05])

        param_array = function[0][1:]

        param_array_expeacted = [[500.0, 0.0001], 'b1*(1-np.exp(-b2*x))']

        np.testing.assert_allclose(y_values_expected, y_values, rtol=1e-5, atol=0)
        self.assertListEqual(param_array_expeacted, param_array)

    def test_ParseProblemFileNIST_returns_correct_problem_object(self):

        fname = get_file('NIST_Misra1a.dat')
        problem = parse_problem_file(fname)
        problem_expected = self.setup_nist_expected_problem()

        self.assertEqual(problem_expected.name, problem.name)
        self.assertEqual(problem_expected.equation, problem.equation)
        self.assertEqual(problem_expected.starting_values,
                         problem.starting_values)
        np.testing.assert_allclose(problem_expected.data_x, problem.data_x)
        np.testing.assert_allclose(problem_expected.data_y, problem.data_y)


    def test_storeProbDetails_correct_storing(self):

        fname = get_file('NIST_Misra1a.dat')
        parsed_eq = 'b1*(1-exp(-b2*x))'
        starting_values = [['b1', [500.0, 250.0]], ['b2', [0.0001, 0.0005]]]
        data_pattern = self.setup_misra1a_expected_data_points()

        prob = FittingProblem(fname)

        prob_expected = self.setup_nist_expected_problem()

        self.assertEqual(prob_expected.name, prob.name)
        self.assertEqual(prob_expected.equation, prob.equation)
        self.assertEqual(prob_expected.starting_values,
                         prob.starting_values)
        np.testing.assert_allclose(prob_expected.data_x, prob.data_x)
        np.testing.assert_allclose(prob_expected.data_y, prob.data_y)

    def test_parseLineByLine_correct_lines(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        equation_text, data_pattern_text, starting_values = prob.parse_line_by_line(open(fname))

        equation_text_expected = 'y = b1*(1-exp[-b2*x])  +  e'
        data_pattern_text_expected = self.setup_misra1a_data_pattern_text()
        starting_values_expected = [['b1', [500.0, 250.0]],
                                    ['b2', [0.0001, 0.0005]]]

        self.assertEqual(equation_text_expected, equation_text)
        self.assertListEqual(data_pattern_text_expected, data_pattern_text)
        self.assertListEqual(starting_values_expected, starting_values)

    def test_getNistModel_return_proper_eqtxt(self):

        lines = self.setup_misra1a_model_lines()
        idx = 0
        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        equation_text, idx = prob.get_nist_model(lines, idx)
        equation_text_expected = 'y = b1*(1-exp[-b2*x])  +  e'
        idx_expected = 4

        self.assertEqual(equation_text_expected, equation_text)
        self.assertEqual(idx_expected, idx)

    def test_getNistModel_fail_runtimeError(self):
        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)
        lines = ["\n", "\n"]
        idx = 33

        self.assertRaises(RuntimeError, prob.get_nist_model, lines, idx)

    def test_getNistStartingValues_return_proper_startvaltxt(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        lines = self.setup_misra1a_startvals_lines()
        idx = 0

        starting_vals, idx = prob.get_nist_starting_values(lines, idx)
        starting_vals_expected = [['b1', [500.0, 250.0]],
                                  ['b2', [0.0001, 0.0005]]]
        idx = 3

        for idx in range(0, len(starting_vals_expected)):
            self.assertEqual(starting_vals_expected[idx][0],
                             starting_vals[idx][0])
            self.assertListEqual(starting_vals_expected[idx][1],
                                 starting_vals[idx][1])

    def test_getNistStartingValues_fail_startvals_invalid(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        lines = ["\n",
                 "\n",
                 "  b1 =   500         250   ",
                 "  b2 =     0.0001      0.0005"
                 "      5.5015643181E-04  7.2668688436E-06"]
        idx = 0

        self.assertRaises(RuntimeError, prob.get_nist_starting_values, lines, idx)

    def test_getDataPatternTxt_correct_data(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        lines = self.setup_misra1a_data_pattern_lines()
        idx = 0

        data_pattern_text, idx = prob.get_data_pattern_txt(lines, idx)
        data_pattern_text_expected = self.setup_misra1a_data_pattern_lines()
        idx_expected = 15

        self.assertEqual(idx_expected, idx)
        self.assertListEqual(data_pattern_text_expected, data_pattern_text)

    def test_getDataPatternTxt_raises_error(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        lines = []
        idx = 0

        self.assertRaises(RuntimeError, prob.get_data_pattern_txt, lines, idx)

    def test_parseDataPattern_return_parsed_data_pattern_array(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        data_pattern_text = self.setup_misra1a_data_pattern_text()

        data_points = prob.parse_data_pattern(data_pattern_text)
        data_points_expected = self.setup_misra1a_expected_data_points()

        np.testing.assert_array_equal(data_points_expected, data_points)

    def test_parseEquation_return_proper_equation_form(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        equation_text = 'y = b1*(1-exp[-b2*x])  +  e'

        equation = prob.parse_equation(equation_text)
        equation_expected = 'b1*(1-exp(-b2*x))'

        self.assertEqual(equation_expected, equation)

    def test_parseEquation_fail_runtimeError(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        equation_text = 'LULy = bf1*(1-exdsp[-b2as*x])  +  e'

        self.assertRaises(RuntimeError, prob.parse_equation, equation_text)

    def test_get_start_x_and_end_x(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        data_pattern = self.setup_misra1a_expected_data_points()
        x_data = data_pattern[:,1]

        expected_start_x = 77.6
        expected_end_x = 760.0

        start_x, end_x = prob.get_start_x_and_end_x(x_data)

        self.assertEqual(expected_start_x, start_x)
        self.assertEqual(expected_end_x, end_x)

    def test_get_data_e_expect_None(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        data_pattern = self.setup_misra1a_expected_data_points()

        expected_data_e = None

        data_e = prob.get_data_e(data_pattern)

        self.assertEqual(expected_data_e, data_e)

    def test_get_data_e_expect_array(self):

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)

        data_pattern = self.setup_misra1a_expected_data_points_with_data_e()

        expected_data_e = data_pattern[:,2]

        data_e = prob.get_data_e(data_pattern)

        np.testing.assert_array_equal(expected_data_e, data_e)

if __name__ == "__main__":
    unittest.main()
