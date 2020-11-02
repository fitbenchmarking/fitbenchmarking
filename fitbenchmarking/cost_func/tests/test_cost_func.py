"""
Tests available cost function classes in FitBenchmarking.
"""

from collections import OrderedDict
from unittest import TestCase

import numpy as np

from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.cost_func.root_nlls_cost_func import RootNLLSCostFunc
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
        fitting_problem = FittingProblem(self.options)
        self.cost_function = NLLSCostFunc(fitting_problem)
        fitting_problem.function = lambda x, p1: x + p1
        self.x_val = np.array([1, 8, 11])
        self.y_val = np.array([6, 10, 20])

    def test_eval_r_raise_error(self):
        """
        Test that eval_r raises and error
        """
        self.assertRaises(exceptions.CostFuncError,
                          self.cost_function.eval_r,
                          params=[1, 2, 3],
                          x=[2],
                          y=[3, 4])

    def test_eval_r_correct_evaluation(self):
        """
        Test that eval_r is running the correct function
        """
        eval_result = self.cost_function.eval_r(x=self.x_val,
                                                y=self.y_val,
                                                params=[5])
        self.assertTrue(all(eval_result == np.array([0, -3, 4])))

    def test_eval_cost(self):
        """
        Test that eval_cost is correct
        """
        eval_result = self.cost_function.eval_cost(params=[5],
                                                   x=self.x_val,
                                                   y=self.y_val)
        self.assertEqual(eval_result, 25)


class TestWeightedNLLSCostFunc(TestCase):
    """
    Class to test the WeightedNLLSCostFunc class
    """

    def setUp(self):
        """
        Setting up weighted nonlinear least squares cost function tests
        """
        self.options = Options()
        fitting_problem = FittingProblem(self.options)
        self.cost_function = WeightedNLLSCostFunc(fitting_problem)
        fitting_problem.function = lambda x, p1: x + p1
        self.x_val = np.array([1, 8, 11])
        self.y_val = np.array([6, 10, 20])
        self.e_val = np.array([2, 4, 1])

    def test_eval_r_raise_error(self):
        """
        Test that eval_r raises and error
        """
        self.assertRaises(exceptions.CostFuncError,
                          self.cost_function.eval_r,
                          params=[1, 2, 3],
                          x=[2],
                          y=[3, 4, 5],
                          e=[23, 4])

    def test_eval_r_correct_evaluation(self):
        """
        Test that eval_r is running the correct function
        """

        eval_result = self.cost_function.eval_r(x=self.x_val,
                                                y=self.y_val,
                                                e=self.e_val,
                                                params=[5])
        self.assertTrue(all(eval_result == np.array([0, -0.75, 4])))

    def test_eval_cost(self):
        """
        Test that eval_cost is correct
        """
        eval_result = self.cost_function.eval_cost(params=[5],
                                                   x=self.x_val,
                                                   y=self.y_val,
                                                   e=self.e_val)
        self.assertEqual(eval_result, 16.5625)


class TestRootNLLSCostFunc(TestCase):
    """
    Class to test the RootNLLSCostFunc class
    """

    def setUp(self):
        """
        Setting up root nonlinear least squares cost function tests
        """
        self.options = Options()
        fitting_problem = FittingProblem(self.options)
        self.cost_function = RootNLLSCostFunc(fitting_problem)
        fitting_problem.function = lambda x, p1: x + p1
        self.x_val = np.array([1, 8, 11])
        self.y_val = np.array([6, 10, 20])

    def test_eval_r_raise_error(self):
        """
        Test that eval_r raises and error
        """
        self.assertRaises(exceptions.CostFuncError,
                          self.cost_function.eval_r,
                          params=[1, 2, 3],
                          x=[2],
                          y=[3, 4, 5])

    def test_eval_r_correct_evaluation(self):
        """
        Test that eval_r is running the correct function
        """
        eval_result = self.cost_function.eval_r(x=self.x_val,
                                                y=self.y_val,
                                                params=[0])
        expected = np.array([1.4494897427831779,
                             0.33385053542218923,
                             1.1555111646441798])
        self.assertTrue(
            all(eval_result == expected))

    def test_eval_cost(self):
        """
        Test that eval_cost is correct
        """
        eval_result = self.cost_function.eval_cost(params=[5],
                                                   x=self.x_val,
                                                   y=self.y_val)
        self.assertEqual(eval_result, 0.4194038580206052)


class FactoryTests(TestCase):
    """
    Tests for the cost function factory
    """

    def test_imports(self):
        """
        Test that the factory returns the correct class for inputs
        """
        self.options = Options()

        valid = ['weighted_nlls', 'nlls', 'root_nlls']
        invalid = ['normal']

        for cost_func_type in valid:
            cost_func = create_cost_func(cost_func_type)
            self.assertTrue(
                cost_func.__name__.lower().startswith(
                    cost_func_type.replace("_", "")))

        for cost_func_type in invalid:
            self.assertRaises(exceptions.CostFuncError,
                              create_cost_func,
                              cost_func_type)
