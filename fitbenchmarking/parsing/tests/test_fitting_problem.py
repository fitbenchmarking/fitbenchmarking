"""
Test file to test the fitting_problem file.
"""

import numpy as np
from unittest import TestCase

from fitbenchmarking.parsing.fitting_problem import FittingProblem


class TestFittingProblem(TestCase):
    """
    Class to test the FittingProblem class
    """

    def test_verify_problem(self):
        """
        Test that verify only returns True if all required values are set.
        """
        fitting_problem = FittingProblem()
        self.assertFalse(fitting_problem.verify(),
                         'verify() incorrect when no values are set.')
        fitting_problem.starting_values = [['p1', [1]],
                                           ['p2', [2]]]
        self.assertFalse(fitting_problem.verify(),
                         'verify() incorrect when starting values are set.')
        fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.assertFalse(fitting_problem.verify(),
                         'verify() incorrect when data_x is set.')
        fitting_problem.data_y = np.array([1, 2, 3, 4, 5])
        self.assertFalse(fitting_problem.verify(),
                         'verify() incorrect when data_y is set.')
        fitting_problem.functions = [[lambda x, p1, p2: p1+p2, [1, 2]]]
        self.assertTrue(fitting_problem.verify(),
                        'verify() incorrect when all required values set.')
        fitting_problem.data_x = [1, 2, 3]
        self.assertFalse(fitting_problem.verify(),
                         'verify() incorrect for x values not numpy.')

    def test_eval_f(self):
        """
        Test that eval_f is running the correct function
        """
        fitting_problem = FittingProblem()
        self.assertRaises(AttributeError,
                          fitting_problem.eval_f,
                          x=2,
                          params=[1, 2, 3],
                          function_id=0)
        fitting_problem.functions = [[lambda x, p1: x + p1, [3]],
                                     [lambda x, p1: x + p1 + 10, [7]]]
        x_val = np.array([1])
        eval_result = fitting_problem.eval_f(x=x_val,
                                             params=[5],
                                             function_id=0)
        self.assertTrue(all(eval_result == np.array([6])))
        eval_result = fitting_problem.eval_f(x=x_val,
                                             params=[5],
                                             function_id=1)
        self.assertTrue(all(eval_result == np.array([16])))

    def test_eval_starting_params(self):
        """
        Test that eval_starting_params returns the correct result
        """
        fitting_problem = FittingProblem()
        self.assertRaises(AttributeError,
                          fitting_problem.eval_starting_params,
                          function_id=0)
        fitting_problem.functions = [[lambda x, p1: x + p1, [3]],
                                     [lambda x, p1: x + p1 + 10, [7]]]
        fitting_problem.data_x = np.array([1])
        eval_result = fitting_problem.eval_starting_params(0)
        self.assertTrue(all(eval_result == np.array([4])))
        eval_result = fitting_problem.eval_starting_params(1)
        self.assertTrue(all(eval_result == np.array([18])))

    def test_get_function_def(self):
        """
        Tests that the function def is formatted correctly
        """
        fitting_problem = FittingProblem()
        expected_function_def = 'test_function | a=1, b=2.0, c=3.3, d=4.99999999'
        fitting_problem.equation = 'test_function'
        fitting_problem.starting_values = [['a', [0]],
                                           ['b', [0]],
                                           ['c', [0]],
                                           ['d', [0]]]
        params = [1, 2.0, 3.3, 4.99999999]
        function_def = fitting_problem.get_function_def(params=params)
        self.assertEqual(function_def, expected_function_def)
