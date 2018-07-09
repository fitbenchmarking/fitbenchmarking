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

class LoadAndParseNistFiles(unittest.TestCase):

    def nistPorblemDirPath(self):
        ''' Helper function that returns the directory path ../NIST_nonlinear_regression/ '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        bench_prob_dir = os.path.join(base_dir, 'benchmark_problems')
        nist_problems_path = os.path.join(bench_prob_dir,
        								  'NIST_nonlinear_regression')

        return nist_problems_path

    def Misra1aLines(self):
        ''' Helper function that returns the lines of problem file Misra1a.dat '''

        nist_problems_path = self.nistPorblemDirPath()
        problem_filename = os.path.join(nist_problems_path , 'Misra1a.dat')
        print(problem_filename)
        with open(problem_filename) as spec_file:
    	   lines = spec_file.readlines()

        return lines

    def Bennett5Lines(self):
        ''' Helper function that returns the lines of problem file Bennett5.dat '''

    	nist_problems_path = self.nistPorblemDirPath()
    	problem_filename = os.path.join(nist_problems_path , 'Bennett5.dat')
        print(problem_filename)
        with open(problem_filename) as spec_file:
           lines = spec_file.readlines()

        return lines


    def ResultsMisra1a(self):
    	''' What parsing the Misra1a.dat file should return '''


    	equation_text_actual = 'y = b1*(1-exp[-b2*x])  +  e'
    	starting_values_actual = [['b1', [500.0,250.0]],
    							  ['b2', [0.0001,0.0005]]]
    	residual_sum_sq_actual = 1.2455138894E-01
    	data_pattern_text_actual = ['      10.07E0      77.6E0\n',
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

        return (equation_text_actual, starting_values_actual,
                residual_sum_sq_actual, data_pattern_text_actual)


    def test_parse_nist_file_line_by_line(self):

        lines = self.Misra1aLines()

    	(equation_text, data_pattern_text,
    	 starting_values, residual_sum_sq) = parse_nist_file_line_by_line(lines)

    	(equation_text_actual, starting_values_actual,
    	 residual_sum_sq_actual, data_pattern_text_actual) = self.ResultsMisra1a()

    	self.assertEqual(equation_text, equation_text_actual,
                         msg = "Test failed when comparing equations")
    	self.assertItemsEqual(data_pattern_text, data_pattern_text_actual,
    						  msg = "Test failed comparing data pattern length")
    	self.assertListEqual(data_pattern_text, data_pattern_text_actual,
    						 msg = "Test failed comparing data pattern content")
    	self.assertEqual(residual_sum_sq, residual_sum_sq_actual,
    					 msg = "Test failed when comparing residual sums")
    	for idx in range(0, len(starting_values_actual)):
    		self.assertEqual(starting_values_actual[idx][0],
    						 starting_values[idx][0],
    						 msg = "Test failed at starting values")
    		self.assertListEqual(starting_values_actual[idx][1],
    			                 starting_values_actual[idx][1],
    			                 msg = "Test failed at starting values")


    def test_parse_nist_file_line_by_line_fail_wrong_file(self):

    	lines = self.Bennett5Lines()
    	(equation_text, data_pattern_text,
    	 starting_values, residual_sum_sq) = parse_nist_file_line_by_line(lines)

    	(equation_text_actual, starting_values_actual,
    	 residual_sum_sq_actual, data_pattern_text_actual) = self.ResultsMisra1a()

    	self.assertEqual(equation_text, equation_text_actual,
    					 msg = "Test failed when comparing equations")
    	self.assertItemsEqual(data_pattern_text, data_pattern_text_actual,
    						  msg = "Test failed comparing data pattern length")
    	self.assertListEqual(data_pattern_text, data_pattern_text_actual,
    						 msg = "Test failed comparing data pattern content")
    	self.assertEqual(residual_sum_sq, residual_sum_sq_actual,
    					 msg = "Test failed when comparing residual sums")
    	for idx in range(0, len(starting_values_actual)):
    		self.assertEqual(starting_values_actual[idx][0],
    						 starting_values[idx][0],
    						 msg = "Test failed at starting values")
    		self.assertListEqual(starting_values_actual[idx][1],
    			                 starting_values_actual[idx][1],
    			                 msg = "Test failed at starting values")


    def test_parse_starting_values(self):

        idx = 0
        lines = self.Misra1aLines()
        while idx < len(lines):
            line = lines[idx].strip()
            idx += 1

            if not line:
                continue

            if 'Starting values' in line or 'Starting Values' in line:
                idx += 2
                starting_values = parse_starting_values(lines[idx:])

        starting_values_actual = [['b1', [500.0,250.0]],
                                  ['b2', [0.0001,0.0005]]]

        for idx in range(0, len(starting_values_actual)):
            self.assertEqual(starting_values_actual[idx][0],
                             starting_values[idx][0])
            self.assertListEqual(starting_values_actual[idx][1],
                                 starting_values_actual[idx][1])


    def test_parse_data_pattern(self):

        lines = self.Misra1aLines()

        (equation_text, data_pattern_text,
         starting_values, residual_sum_sq) = parse_nist_file_line_by_line(lines)

        data_pattern = parse_data_pattern(data_pattern_text)
        data_pattern_actual = [ [10.07, 77.6],
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
                                [81.78, 760.0] ]

        data_pattern_actual = np.asarray(data_pattern_actual)

        for i in range(0,len(data_pattern_actual)):
            test_result = np.testing.assert_array_equal(data_pattern_actual[i],
                                                        data_pattern[i])
            self.assertTrue(test_result is None)


    def test_parse_equation(self):

        lines = self.Misra1aLines()
        (equation_text, data_pattern_text,
         starting_values, residual_sum_sq) = parse_nist_file_line_by_line(lines)

        parsed_eq = parse_equation(equation_text)
        parsed_eq_actual = 'b1*(1-exp(-b2*x))'

        self.assertEqual(parsed_eq, parsed_eq_actual,
                         msg = "Test failed at parsing equations normal")

        self.assertRaises(RuntimeError, parse_equation, 'lol = b1*(1-exp(-b2*x))')



    def test_parse_nist_file(self):

        data_pattern_actual = [ [10.07, 77.6],
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
                                [81.78, 760.0] ]
        data_pattern_actual = np.asarray(data_pattern_actual)

        prob_actual = test_problem.FittingTestProblem()
        prob_actual.name = 'Misra1a.dat'
        prob_actual.linked_name = ("`Misra1a.dat <http://www.itl.nist.gov/"
                                   "div898/strd/nls/data/misra1a.dat.shtml>`__")
        prob_actual.equation = 'b1*(1-exp(-b2*x))'
        prob_actual.starting_values = [['b1', [500.0,250.0]],
                                       ['b2', [0.0001,0.0005]]]
        prob_actual.data_pattern_in = data_pattern_actual[:, 1:]
        prob_actual.data_pattern_out = data_pattern_actual[:, 0]
        prob_actual.ref_residual_sum_sq = 1.2455138894E-01

        base_path = self.nistPorblemDirPath()
        path_to_misra1a = os.path.join(base_path,'Misra1a.dat')
        with open(path_to_misra1a) as spec_file:
            prob = parse_nist_file(spec_file)

        self.assertEqual(prob.name, prob_actual.name,
                         msg = "Fail at name")
        self.assertEqual(prob.linked_name, prob_actual.linked_name,
                         msg = "Fail at linked name")
        self.assertEqual(prob.equation, prob_actual.equation,
                         msg = "Fail at equation")
        self.assertEqual(prob.starting_values, prob_actual.starting_values,
                         msg = "Fail at starting values")
        test_result = np.testing.assert_array_equal(prob_actual.data_pattern_in,
                                                        prob.data_pattern_in)
        self.assertTrue(test_result is None, msg = "Fail at data pattern in")

        test_result = np.testing.assert_array_equal(prob_actual.data_pattern_out,
                                                        prob.data_pattern_out)
        self.assertTrue(test_result is None, msg = "Fail at data pattern out")

        self.assertEqual(prob.ref_residual_sum_sq, prob_actual.ref_residual_sum_sq,
                         msg = "Fail at ref residual sum sq")


if __name__ == "__main__":
    unittest.main()
