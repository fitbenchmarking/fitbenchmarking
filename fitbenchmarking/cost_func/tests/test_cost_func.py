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


class DummyCostFunc(CostFunc):
    """
    Minimal instantiatable subclass of CostFunc class for testing
    """

    def __init__(self, problem):
        super(DummyCostFunc, self).__init__(problem)

    def eval_model(self, params, **kwargs):
        """
        Dummy function evaluation method

        :param params: parameter value(s)
        :type params: list

        :return: data values evaluated from the function of the problem
        :rtype: numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        return self.problem.function(x, *params)

    def eval_cost(self, params, **kwargs):
        raise NotImplementedError


class TestBaseCostFunc(TestCase):
    """
    Tests for the base cost function class
    """

    def setUp(self):
        """
        Setting up options to use for tests
        """
        self.options = Options()

    def test_eval_starting_params_raises_error(self):
        """
        Test that eval_starting_params raises an error
        """
        fitting_problem = FittingProblem(self.options)
        cost_func = DummyCostFunc(fitting_problem)
        self.assertRaises(exceptions.CostFuncError,
                          cost_func.eval_starting_params,
                          param_set=0)

    def test_eval_starting_params_correct(self):
        """
        Test that eval_starting_params returns the correct result
        """
        fitting_problem = FittingProblem(self.options)
        fitting_problem.function = lambda x, p1: x + p1
        fitting_problem.starting_values = [OrderedDict([('p1', 3)]),
                                           OrderedDict([('p1', 7)])]
        fitting_problem.data_x = np.array([1])
        cost_func = DummyCostFunc(fitting_problem)
        eval_result = cost_func.eval_starting_params(0)
        self.assertTrue(all(eval_result == np.array([4])))
        eval_result = cost_func.eval_starting_params(1)
        self.assertTrue(all(eval_result == np.array([8])))


class TestNLLSCostFunc(TestCase):
    """
    Class to test the NLLSCostFunc class
    """

    def setUp(self):
        """
        Setting up nonlinear least squares cost function tests
        """
        self.options = Options()

    def test_eval_model_raise_error(self):
        """
        Test that eval_model raises and error
        """
        fitting_problem = FittingProblem(self.options)
        cost_function = NLLSCostFunc(fitting_problem)
        self.assertRaises(exceptions.CostFuncError,
                          cost_function.eval_model,
                          x=2,
                          params=[1, 2, 3])

    def test_eval_model_correct_evaluation(self):
        """
        Test that eval_model is running the correct function
        """
        fitting_problem = FittingProblem(self.options)
        cost_function = NLLSCostFunc(fitting_problem)
        fitting_problem.function = lambda x, p1: x + p1
        x_val = np.array([1, 8, 11])
        eval_result = cost_function.eval_model(x=x_val,
                                           params=[5])
        self.assertTrue(all(eval_result == np.array([6, 13, 16])))

        fitting_problem.data_x = np.array([20, 21, 22])
        eval_result = cost_function.eval_model(params=[5])
        self.assertTrue(all(eval_result == np.array([25, 26, 27])))

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
        Test that eval_model is running the correct function
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
