from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

# DELETE RELATIVE PATH WHEN GIT TESTS ARE ENABLED
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from input_parsing import load_nist_fitting_problem_file
from input_parsing import parse_nist_file
from input_parsing import parse_nist_file_line_by_line
from input_parsing import parse_data_pattern
from input_parsing import parse_equation
from input_parsing import parse_starting_values
import test_problem

# Note for readability: all tests follow the same structure, i.e. :
# setting up expected results
# calculating the actual results
# comparing the two
# Each of these sections is delimited by an empty new line.

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
        print(problem_filename)
        with open(problem_filename) as spec_file:
    	   lines = spec_file.readlines()

        return lines


    def Bennett5Lines(self):
        ''' Helper function that returns the lines of problem file Bennett5.dat '''

    	nist_problems_path = self.nistProblemDirPath()
    	problem_filename = os.path.join(nist_problems_path , 'Bennett5.dat')
        print(problem_filename)
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


    def test_parse_nist_file_line_by_line(self):

    	(equation_text_expected, starting_values_expected,
    	 residual_sum_sq_expected, data_pattern_text_expected) = self.ResultsMisra1a()

        lines = self.Misra1aLines()
        (equation_text, data_pattern_text,
         starting_values, residual_sum_sq) = parse_nist_file_line_by_line(lines)

    	self.assertEqual(equation_text_expected, equation_text)
    	self.assertItemsEqual(data_pattern_text_expected, data_pattern_text)
    	self.assertListEqual(data_pattern_text_expected, data_pattern_text)
    	self.assertEqual(residual_sum_sq_expected, residual_sum_sq)
    	for idx in range(0, len(starting_values_expected)):
    		self.assertEqual(starting_values_expected[idx][0], starting_values[idx][0])
    		self.assertListEqual(starting_values_expected[idx][1], starting_values[idx][1])


    def test_fail_wrong_file_parse_nist_file_line_by_line(self):

    	(equation_text_expected, starting_values_expected,
    	 residual_sum_sq_expected, data_pattern_text_expected) = self.ResultsMisra1a()

        lines = self.Bennett5Lines()
        (equation_text, data_pattern_text,
         starting_values, residual_sum_sq) = parse_nist_file_line_by_line(lines)

    	self.assertEqual(equation_text_expected, equation_text)
    	self.assertItemsEqual(data_pattern_text_expected, data_pattern_text)
    	self.assertListEqual(data_pattern_text_expected, data_pattern_text)
    	self.assertEqual(residual_sum_sq_expected, residual_sum_sq)
    	for idx in range(0, len(starting_values_expected)):
    		self.assertEqual(starting_values_expected[idx][0], starting_values[idx][0])
    		self.assertListEqual(starting_values_expected[idx][1], starting_values[idx][1])


    def test_parse_starting_values(self):

        starting_values_expected = [['b1', [500.0,250.0]],
                                    ['b2', [0.0001,0.0005]]]

        lines = ["  b1 =   500         250           2.3894212918E+02  2.7070075241E+00",
                 "  b2 =     0.0001      0.0005      5.5015643181E-04  7.2668688436E-06" ]
        starting_values = parse_starting_values(lines)

        print(starting_values)
        for idx in range(0, len(starting_values_expected)):
            self.assertEqual(starting_values_expected[idx][0], starting_values[idx][0])
            self.assertListEqual(starting_values_expected[idx][1], starting_values[idx][1])


    def test_parse_data_pattern(self):

        data_pattern_actual = np.array([ [10.07, 77.6],
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

        for idx in range(0,len(data_pattern_actual)):
            np.testing.assert_array_equal(data_pattern_actual[idx], data_pattern[idx])


    def test_parse_equation(self):

        parsed_eq_expected = 'b1*(1-exp(-b2*x))'

        equation_text = 'y = b1*(1-exp[-b2*x])  +  e'
        parsed_eq = parse_equation(equation_text)

        self.assertEqual(parsed_eq_expected, parsed_eq)
        self.assertRaises(RuntimeError, parse_equation, 'lol = b1*(1-exp(-b2*x))')


    def test_parse_nist_file(self):

        data_pattern_expected = np.array([ [10.07, 77.6],
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
        prob_expected = test_problem.FittingTestProblem()
        prob_expected.name = 'Misra1a.dat'
        prob_expected.linked_name = ("`Misra1a.dat <http://www.itl.nist.gov/"
                                   "div898/strd/nls/data/misra1a.dat.shtml>`__")
        prob_expected.equation = 'b1*(1-exp(-b2*x))'
        prob_expected.starting_values = [['b1', [500.0,250.0]],
                                       ['b2', [0.0001,0.0005]]]
        prob_expected.data_pattern_in = data_pattern_expected[:, 1:]
        prob_expected.data_pattern_out = data_pattern_expected[:, 0]
        prob_expected.ref_residual_sum_sq = 1.2455138894E-01

        base_path = self.nistProblemDirPath()
        path_to_misra1a = os.path.join(base_path,'Misra1a.dat')
        with open(path_to_misra1a) as spec_file:
            prob = parse_nist_file(spec_file)

        self.assertEqual(prob_expected.name, prob.name)
        self.assertEqual(prob_expected.linked_name, prob.linked_name)
        self.assertEqual(prob_expected.equation, prob.equation)
        self.assertEqual(prob_expected.starting_values, prob.starting_values)
        self.assertEqual(prob_expected.ref_residual_sum_sq, prob.ref_residual_sum_sq)
        np.testing.assert_array_equal(prob_expected.data_pattern_in, prob.data_pattern_in)
        np.testing.assert_array_equal(prob_expected.data_pattern_out, prob.data_pattern_out)


if __name__ == "__main__":
    unittest.main()
