"""
Tests available cost function classes in FitBenchmarking.
"""

from collections import OrderedDict
from unittest import TestCase

import numpy as np

from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.cost_func.base_cost_func import CostFunc
from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


class TestNLLSCostFunc(TestCase):
    """
    Class to test the NLLSCostFunc class
    """

    def setUp(self):
        """
        Setting up nonlinear least squares cost function tests
        """
        self.options = Options()

    def test_eval_r_raise_error(self):
        """
        Test that eval_r raises and error
        """
        fitting_problem = FittingProblem(self.options)
        cost_function = NLLSCostFunc(fitting_problem)
        self.assertRaises(exceptions.CostFuncError,
                          cost_function.eval_r,
                          params=[1, 2, 3],
                          x=2)

    def test_eval_r_correct_evaluation(self):
        """
        Test that eval_r is running the correct function
        """
        fitting_problem = FittingProblem(self.options)
        cost_function = NLLSCostFunc(fitting_problem)

        fitting_problem.function = lambda x, p1: x + p1
        x_val = np.array([1, 8, 11])
        y_val = np.array([6, 10, 20])

        eval_result = cost_function.eval_r(x=x_val,
                                           y=y_val,
                                           params=[5])
        self.assertTrue(all(eval_result == np.array([0, -3, 4])))

        e_val = np.array([2, 4, 1])
        eval_result = cost_function.eval_r(x=x_val,
                                           y=y_val,
                                           e=e_val,
                                           params=[5])
        self.assertTrue(all(eval_result == np.array([0, -0.75, 4])))

        fitting_problem.data_x = np.array([20, 21, 22])
        fitting_problem.data_y = np.array([20, 30, 35])
        eval_result = cost_function.eval_r(params=[5])
        self.assertTrue(all(eval_result == np.array([-5, 4, 8])))

        fitting_problem.data_e = np.array([2, 5, 10])
        eval_result = cost_function.eval_r(params=[5])
        self.assertTrue(all(eval_result == np.array([-2.5, 0.8, 0.8])))

    def test_eval_cost(self):
        """
        Test that eval_cost is correct
        """
        fitting_problem = FittingProblem(self.options)
        cost_function = NLLSCostFunc(fitting_problem)

        fitting_problem.function = lambda x, p1: x + p1
        x_val = np.array([1, 8, 11])
        y_val = np.array([6, 10, 20])
        e_val = np.array([0.5, 10, 0.1])

        eval_result = cost_function.eval_cost(params=[5],
                                              x=x_val,
                                              y=y_val,
                                              e=e_val)
        self.assertEqual(eval_result, 1600.09)

        fitting_problem.data_x = x_val
        fitting_problem.data_y = y_val
        eval_result = cost_function.eval_cost(params=[5])
        self.assertEqual(eval_result, 25)


class FactoryTests(TestCase):
    """
    Tests for the cost function factory
    """

    def test_imports(self):
        """
        Test that the factory returns the correct class for inputs
        """
        self.options = Options()

        valid = ['nlls']
        invalid = ['normal']

        for cost_func_type in valid:
            cost_func = create_cost_func(cost_func_type)
            self.assertTrue(
                cost_func.__name__.lower().startswith(cost_func_type))

        for jac_method in invalid:
            self.assertRaises(exceptions.CostFuncError,
                              create_cost_func,
                              jac_method)
