from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from fitting_benchmarking import parse_problem_file
from input_parsing import load_nist_fitting_problem_file
from input_parsing import parse_nist_file_line_by_line
from input_parsing import get_nist_model
from input_parsing import get_nist_starting_values
from input_parsing import get_data_pattern_txt
from input_parsing import parse_data_pattern
from input_parsing import parse_equation
from input_parsing import parse_starting_values
import test_problem


class LoadAndParseNistFiles(unittest.TestCase):

    def nistProblemDirPath(self):
        ''' Helper function that returns the directory path ../NIST_nonlinear_regression/ '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        bench_prob_dir = os.path.join(base_dir, 'benchmark_problems')
        nist_problems_path = os.path.join(bench_prob_dir,
                                          'NIST_nonlinear_regression')

        return nist_problems_path


    def Misra1aLines(self):
        ''' Helper function that returns the lines of problem file Misra1a.dat '''

        nist_problems_path = self.nistProblemDirPath()
        problem_filename = os.path.join(nist_problems_path , 'Misra1a.dat')
        with open(problem_filename) as spec_file:
           lines = spec_file.readlines()

        return lines


    def ResultsMisra1a(self):
        ''' Expected results from parsing the Misra1a.dat file '''

        equation_text = 'y = b1*(1-exp[-b2*x])  +  e'
        starting_values = [['b1', [500.0,250.0]],
                           ['b2', [0.0001,0.0005]]]
        residual_sum_sq = 1.2455138894E-01
        data_pattern_text = ['      10.07E0      77.6E0\n',
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

        return (equation_text, starting_values,
                residual_sum_sq, data_pattern_text)


    def Misra1aExpectedProblemObject(self):
        ''' Helper function that returns the problem object expected
            after parsing the Misra1a.dat data file '''

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
        prob = test_problem.FittingTestProblem()
        prob.name = 'Misra1a'
        prob.linked_name = ("`Misra1a <http://www.itl.nist.gov/"
                            "div898/strd/nls/data/misra1a.shtml>`__")
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0,250.0]],
                                ['b2', [0.0001,0.0005]]]
        prob.data_y = data_pattern[:, 1]
        prob.data_x = data_pattern[:, 0]
        prob.ref_residual_sum_sq = 1.2455138894E-01

        return prob


    def test_loadNistFittingProblemFile_return_Misra1a_problem_definition_object(self):

        base_path = self.nistProblemDirPath()
        problem_filename = os.path.join(base_path, 'Misra1a.dat')

        prob = load_nist_fitting_problem_file(problem_filename)
        prob_expected = self.Misra1aExpectedProblemObject()

        self.assertEqual(prob_expected.name, prob.name)
        self.assertEqual(prob_expected.linked_name, prob.linked_name)
        self.assertEqual(prob_expected.equation, prob.equation)
        self.assertEqual(prob_expected.starting_values, prob.starting_values)
        self.assertEqual(prob_expected.ref_residual_sum_sq,
                         prob.ref_residual_sum_sq)
        np.testing.assert_array_equal(prob_expected.data_x,
                                      prob.data_x)
        np.testing.assert_array_equal(prob_expected.data_y,
                                      prob.data_y)


    def test_parseProblemFile_return_nist_prob_object(self):

        group_name = 'nist'
        prob_file = os.path.join(self.nistProblemDirPath(), 'Misra1a.dat')

        prob = parse_problem_file(group_name, prob_file)
        prob_expected = self.Misra1aExpectedProblemObject()

        self.assertEqual(prob_expected.name, prob.name)
        self.assertEqual(prob_expected.linked_name, prob.linked_name)
        self.assertEqual(prob_expected.equation, prob.equation)
        self.assertEqual(prob_expected.starting_values, prob.starting_values)
        self.assertEqual(prob_expected.ref_residual_sum_sq,
                         prob.ref_residual_sum_sq)
        np.testing.assert_array_equal(prob_expected.data_x,
                                      prob.data_x)
        np.testing.assert_array_equal(prob_expected.data_y,
                                      prob.data_y)


    def test_parseProblemFile_raise_NameError(self):

        prob_file = os.path.join(self.nistProblemDirPath(), 'Misra1a.dat')

        self.assertRaises(NameError, parse_problem_file, 'thiswillfail',
                          prob_file)


    def test_parseNISTfileLineByLine_return_Misra1a_problem_lines(self):

        lines = self.Misra1aLines()

        (equation_text, data_pattern_text,
         starting_values, residual_sum_sq) = parse_nist_file_line_by_line(lines)
        (equation_text_expected, starting_values_expected,
         residual_sum_sq_expected, data_pattern_text_expected) = \
        self.ResultsMisra1a()

        self.assertEqual(equation_text_expected, equation_text)
        self.assertListEqual(data_pattern_text_expected, data_pattern_text)
        self.assertEqual(residual_sum_sq_expected, residual_sum_sq)
        for idx in range(0, len(starting_values_expected)):
            self.assertEqual(starting_values_expected[idx][0],
                             starting_values[idx][0])
            self.assertListEqual(starting_values_expected[idx][1],
                                 starting_values[idx][1])


    def test_getNISTmodel_return_Misra1a_eq_txt_and_idx(self):

        lines = self.Misra1aLines()
        idx = 31

        equation_text, idx = get_nist_model(lines, idx)
        equation_text_expected, idx_expected = 'y = b1*(1-exp[-b2*x])  +  e', 34

        self.assertEqual(equation_text_expected, equation_text)
        self.assertEqual(idx_expected, idx)


    def test_getNISTmodel_fail_to_find_equation(self):

        lines = self.Misra1aLines()
        idx = 35

        self.assertRaises(RuntimeError, get_nist_model, lines, idx)


    def test_getNISTstartingValues_return_Misra1a_starting_values(self):

        lines = self.Misra1aLines()
        idx = 38

        starting_values, idx = get_nist_starting_values(lines, idx)
        starting_values_expected = [['b1', [500.0,250.0]],
                                    ['b2', [0.0001,0.0005]]]
        idx_expected = 42

        for i in range(0, len(starting_values_expected)):
            self.assertEqual(starting_values_expected[i][0],
                             starting_values[i][0])
            self.assertListEqual(starting_values_expected[i][1],
                                 starting_values[i][1])
        self.assertEqual(idx_expected, idx)


    def test_getDataPatternTxt_return_Misra1a_starting_values(self):

        lines = self.Misra1aLines()
        idx = 60

        data_pattern_text, idx = get_data_pattern_txt(lines, idx)
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
        idx_expected = 74

        self.assertListEqual(data_pattern_text_expected, data_pattern_text)
        self.assertEqual(idx_expected, idx)


    def test_getDataPatternTxt_fail_raise_RuntimeError(self):

        lines = self.Misra1aLines()
        idx = 75

        self.assertRaises(RuntimeError, get_data_pattern_txt, lines, idx)


    def test_parseDataPattern_return_data_pattern_Misra1a(self):

        data_pattern_text = ['      10.07E0      77.6E0\n',
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

        data_pattern = parse_data_pattern(data_pattern_text)
        data_pattern_expected = np.array([ [10.07, 77.6], [14.73, 114.9],
                                           [17.94, 141.1], [23.93, 190.8],
                                           [29.61, 239.9], [35.18, 289.0],
                                           [40.02, 332.8], [44.82, 378.4],
                                           [50.76, 434.8], [55.05, 477.3],
                                           [61.01, 536.8], [66.40, 593.1],
                                           [75.47, 689.1], [81.78, 760.0] ])

        np.testing.assert_array_equal(data_pattern_expected, data_pattern)


    def test_parseDataPattern_return_none_as_no_data_text(self):

        data_points_expected = None
        data_text = 0

        data_points = parse_data_pattern(data_text)

        self.assertTrue(data_points is None)


    def test_parseEquation_return_Misra1a_parsed_equation(self):

        equation_text = 'y = b1*(1-exp[-b2*x])  +  e'

        parsed_eq = parse_equation(equation_text)
        parsed_eq_expected = 'b1*(1-exp(-b2*x))'

        self.assertEqual(parsed_eq_expected, parsed_eq)


    def test_parseEquation_fail_wrong_equation_form(self):

        self.assertRaises(RuntimeError, parse_equation,
                          'lol = b1*(1-exp(-b2*x))')


    def test_parseStartingValues_return_Misra1a_starting_values(self):

        lines = ["  b1 =   500         250"
                 "           2.3894212918E+02  2.7070075241E+00",
                 "  b2 =     0.0001      0.0005"
                 "      5.5015643181E-04  7.2668688436E-06" ]

        starting_values = parse_starting_values(lines)
        starting_values_expected = [['b1', [500.0,250.0]],
                                    ['b2', [0.0001,0.0005]]]

        for idx in range(0, len(starting_values_expected)):
            self.assertEqual(starting_values_expected[idx][0],
                             starting_values[idx][0])
            self.assertListEqual(starting_values_expected[idx][1],
                                 starting_values[idx][1])


    def test_parseStartingValues_failed_to_parse_line(self):

        lines = ["  b1 =   500         250   ",
                 "  b2 =     0.0001      0.0005"
                 "      5.5015643181E-04  7.2668688436E-06" ]

        self.assertRaises(RuntimeError, parse_starting_values, lines)


if __name__ == "__main__":
    unittest.main()
