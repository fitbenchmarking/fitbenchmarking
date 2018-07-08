# Unit testing the file importing functions
import unittest
import os

# DELETE RELATIVE PATH WHEN GIT TESTS ARE ENABLED
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from input_parsing.py import load_nist_fitting_problem_file
from input_parsing.py import parse_nist_file
from input_parsing.py import parse_nist_file_line_by_line
from input_parsing.py import parse_data_pattern
from input_parsing.py import parse_equation
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
        
        nist_problems_path = self.nistPorblemDirPath
    	spec_file = open(os.path.join(nist_problems_path , 'Misra1a.dat'),'r')
    	lines = spec_file.readlines()
    	spec_file.close()

        return lines

    def Bennett5Lines(self):
        ''' Helper function that returns the lines of problem file Bennett5.dat '''
                
    	nist_problems_path = self.nistPorblemDirPath
    	spec_file = open(os.path.join(nist_problems_path , 'Bennett5.dat'),'r')
    	lines = spec_file.readlines()
    	spec_file.close()

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


    def parse_nist_file_line_by_line_test(self):

    	lines = self.Misra1aLines()
    	(equation_text, data_pattern_text, 
    	 starting_values, residual_sum_sq) = parse_nist_file_line_by_line(lines)

    	(equation_text_actual, starting_values_actual, 
    	 residual_sum_sq_actual, data_pattern_text_actual) = self.ResultsMisra1a()

    	self.assertEqual(equation_text, equation_text_actual,
    					 msg = "Test failed when comparing equations")
    	self.assertCountEqual(data_pattern_text, data_pattern_text_actual,
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

    		
    def parse_nist_file_line_by_line_fail_wrong_file(self):

    	lines = self.Bennett5Lines()
    	(equation_text, data_pattern_text, 
    	 starting_values, residual_sum_sq) = parse_nist_file_line_by_line(lines)

    	(equation_text_actual, starting_values_actual, 
    	 residual_sum_sq_actual, data_pattern_text_actual) = self.ResultsMisra1a()

    	self.assertEqual(equation_text, equation_text_actual,
    					 msg = "Test failed when comparing equations")
    	self.assertCountEqual(data_pattern_text, data_pattern_text_actual,
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