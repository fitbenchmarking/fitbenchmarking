"""
Tests available cost function classes in FitBenchmarking.
"""

from unittest import TestCase

import numpy as np

from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.cost_func.hellinger_nlls_cost_func import \
    HellingerNLLSCostFunc
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.cost_func.poisson_cost_func import (PoissonCostFunc,
                                                         _safe_a_log_b)
from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.hessian.analytic_hessian import Analytic
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.exceptions import IncompatibleCostFunctionError
from fitbenchmarking.utils.options import Options

# pylint: disable=attribute-defined-outside-init


def fun(x, p):
    """
    Analytic function evaluation
    """
    return (x*p**2)**2


def jac(x, p):
    """
    Analytic Jacobian evaluation
    """
    return np.column_stack((4*x**2*p[0]**3,
                            4*x**2*p[0]**3))


def hes(x, p):
    """
    Analytic Hessian evaluation
    """
    return np.array([[12*x**2*p[0]**2, 12*x**2*p[0]**2],
                     [12*x**2*p[0]**2, 12*x**2*p[0]**2], ])


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
        fitting_problem.function = lambda x, p1: x + p1
        self.x_val = np.array([1.0, 8.0, 11.0])
        self.y_val = np.array([6.0, 10.0, 20.0])
        fitting_problem.data_x = self.x_val
        fitting_problem.data_y = self.y_val
        self.cost_function = NLLSCostFunc(fitting_problem)

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

    def test_validate_algorithm_type_error(self):
        """
        Test that validate_algorithm_type raises an error
        for incompatible options
        """
        self.cost_function.invalid_algorithm_types = ['ls']
        algorithm_check = {'ls': ['ls-min']}
        minimizer = 'ls-min'

        self.assertRaises(exceptions.IncompatibleMinimizerError,
                          self.cost_function.validate_algorithm_type,
                          algorithm_check=algorithm_check,
                          minimizer=minimizer)

    def test_validate_algorithm_type_correct(self):
        """
        Test that validate_algorithm_type does not raise
        an error for compatible options
        """
        self.cost_function.invalid_algorithm_types = []
        algorithm_check = {'ls': ['ls-min']}
        minimizer = 'ls-min'

        self.cost_function.validate_algorithm_type(algorithm_check, minimizer)

    def test_validate_problem_correct(self):
        """
        Test that validate_problem does not raise an error
        """
        self.cost_function.validate_problem()

    def test_jac_res(self):
        """
        Test that jac_res works for the NLLs cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        J = self.cost_function.jac_res(params=[5],
                                       x=self.x_val,
                                       y=self.y_val)

        expected = np.array([[-1.0], [-1.0], [-1.0]])
        self.assertTrue(np.allclose(J, expected))

    def test_jac_cost(self):
        """
        Test that jac_cost works for the NLLs cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        jac_cost = self.cost_function.jac_cost(params=[5],
                                               x=self.x_val,
                                               y=self.y_val)

        expected = np.array([-2.0])
        self.assertTrue(np.allclose(jac_cost, expected))

    def test_hes_res(self):
        """
        Test that hes_res works for the NLLs cost function
        """
        self.cost_function.problem.function = fun
        self.cost_function.problem.jacobian = jac
        self.cost_function.problem.hessian = hes
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian
        hessian = Analytic(self.cost_function.problem,
                           self.cost_function.jacobian)
        self.cost_function.hessian = hessian

        H, _ = self.cost_function.hes_res(params=[5],
                                          x=self.x_val,
                                          y=self.y_val)

        expected = np.array([[[-300.0, -19200.0, -36300.0],
                              [-300.0, -19200.0, -36300.0]],
                             [[-300.0, -19200.0, -36300.0],
                              [-300.0, -19200.0, -36300.0]]])
        self.assertTrue(np.allclose(H, expected))

    def test_hes_cost(self):
        """
        Test that hes_cost works for the NLLs cost function
        """
        self.cost_function.problem.function = fun
        self.cost_function.problem.jacobian = jac
        self.cost_function.problem.hessian = hes
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian
        hessian = Analytic(self.cost_function.problem,
                           self.cost_function.jacobian)
        self.cost_function.hessian = hessian

        hes_cost = self.cost_function.hes_cost(params=[0.01],
                                               x=self.x_val,
                                               y=self.y_val)

        expected = np.array([[-7.35838895, -7.35838895],
                             [-7.35838895, -7.35838895]])
        self.assertTrue(np.allclose(hes_cost, expected))


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
        fitting_problem.function = lambda x, p1: x + p1
        self.x_val = np.array([1.0, 8.0, 11.0])
        self.y_val = np.array([6.0, 10.0, 20.0])
        self.e_val = np.array([2.0, 4.0, 1.0])
        fitting_problem.data_x = self.x_val
        fitting_problem.data_y = self.y_val
        fitting_problem.data_e = self.e_val
        self.cost_function = WeightedNLLSCostFunc(fitting_problem)

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

    def test_jac_res(self):
        """
        Test that jac_res works for the Weighted NLLs cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        J = self.cost_function.jac_res(params=[5],
                                       x=self.x_val,
                                       y=self.y_val,
                                       e=self.e_val)

        expected = np.array([[-0.5], [-0.25], [-1.0]])
        self.assertTrue(np.allclose(J, expected))

    def test_hes_res(self):
        """
        Test that hes_res works for the Weighted NLLs cost function
        """
        self.cost_function.problem.function = fun
        self.cost_function.problem.jacobian = jac
        self.cost_function.problem.hessian = hes
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian
        hessian = Analytic(self.cost_function.problem,
                           self.cost_function.jacobian)
        self.cost_function.hessian = hessian

        H, _ = self.cost_function.hes_res(params=[5],
                                          x=self.x_val,
                                          y=self.y_val,
                                          e=self.e_val)

        expected = np.array([[[-150.0, -4800.0, -36300.0],
                              [-150.0, -4800.0, -36300.0]],
                             [[-150.0, -4800.0, -36300.0],
                              [-150.0, -4800.0, -36300.0]]])
        self.assertTrue(np.allclose(H, expected))

    def test_validate_problem_correct(self):
        """
        Test that validate_problem does not raise an error
        """
        self.cost_function.validate_problem()


class TestHellingerNLLSCostFunc(TestCase):
    """
    Class to test the HellingerNLLSCostFunc class
    """

    def setUp(self):
        """
        Setting up root nonlinear least squares cost function tests
        """
        self.options = Options()
        fitting_problem = FittingProblem(self.options)
        fitting_problem.function = lambda x, p1: x + p1
        self.x_val = np.array([1.0, 8.0, 11.0])
        self.y_val = np.array([6.0, 10.0, 20.0])
        fitting_problem.data_x = self.x_val
        fitting_problem.data_y = self.y_val
        self.cost_function = HellingerNLLSCostFunc(fitting_problem)

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

    def test_jac_res(self):
        """
        Test that jac_res works for the Hellinger NLLs cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        J = self.cost_function.jac_res(params=[5],
                                       x=self.x_val,
                                       y=self.y_val)

        expected = np.array([[-0.20412415],
                             [-0.13867504],
                             [-0.125]])
        self.assertTrue(np.allclose(J, expected))

    def test_hes_res(self):
        """
        Test that hes_res works for the Hellinger NLLs cost function
        """
        self.cost_function.problem.function = fun
        self.cost_function.problem.jacobian = jac
        self.cost_function.problem.hessian = hes
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian
        hessian = Analytic(self.cost_function.problem,
                           self.cost_function.jacobian)
        self.cost_function.hessian = hessian

        H, _ = self.cost_function.hes_res(params=[5],
                                          x=self.x_val,
                                          y=self.y_val)
        print(H)
        expected = np.array([[[-2.0, -16.0, -22.0],
                              [-2.0, -16.0, -22.0]],
                             [[-2.0, -16.0, -22.0],
                              [-2.0, -16.0, -22.0]]])
        self.assertTrue(np.allclose(H, expected))

    def test_validate_problem_correct(self):
        """
        Test that validate_problem does not raise an error
        """
        self.cost_function.validate_problem()

    def test_validate_problem_incorrect(self):
        """
        Test that validate_problem does raise an error when y has negative vals
        """
        self.cost_function.problem.data_y[2] = -0.05
        with self.assertRaises(IncompatibleCostFunctionError):
            self.cost_function.validate_problem()


class TestPoissonCostFunc(TestCase):
    """
    Class to test the PoissonCostFunc class
    """

    def setUp(self):
        """
        Setting up poisson cost function tests
        """
        self.options = Options()
        fitting_problem = FittingProblem(self.options)
        fitting_problem.function = lambda x, p1: x + p1
        self.x_val = np.array([1.0, 8.0, 11.0])
        self.y_val = np.array([6.0, 10.0, 20.0])
        fitting_problem.data_x = self.x_val
        fitting_problem.data_y = self.y_val
        self.cost_function = PoissonCostFunc(fitting_problem)

    def test_eval_cost_raise_error(self):
        """
        Test that eval_cost raises an error if inputs are bad.
        """
        with self.assertRaises(exceptions.CostFuncError):
            _ = self.cost_function.eval_cost(
                params=[5],
                x=[2],
                y=[1, 3, 5])

    def test_eval_cost_correct(self):
        """
        Test that the eval cost function returns the correct value
        """
        eval_result = self.cost_function.eval_cost(params=[5],
                                                   x=self.x_val,
                                                   y=self.y_val)

        # 6*(log(6) - log(6))
        # + 10*(log(10) - log(13))
        # + 20*(log(20) - log(16))
        # - (6 - 6) - (10 - 13) - (20 - 16)
        # == 30*log(5) - 10*log(13) - 30*log(2) - 1
        self.assertAlmostEqual(eval_result, 0.8392283816092849, places=12)

    def test_safe_a_log_b(self):
        """
        Test the safe_a_log_b function.
        """
        a = np.array([1, 2, 3, 0, 5])
        b = np.array([1, 2, 3, 4, 5])
        res = _safe_a_log_b(a, b)
        self.assertTrue(np.isclose(res,
                                   np.array([0.0,
                                             2*np.log(2),
                                             3*np.log(3),
                                             0.0,
                                             5*np.log(5)])
                                   ).all())

    def test_jac_res(self):
        """
        Test that jac_res works for the Poisson cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        J = self.cost_function.jac_res(params=[5],
                                       x=self.x_val,
                                       y=self.y_val)

        expected = np.array([[0.0],
                             [0.23076923],
                             [-0.25]])
        self.assertTrue(np.allclose(J, expected))

    def test_hes_res(self):
        """
        Test that hes_res works for the Poisson NLLs cost function
        """
        self.cost_function.problem.function = fun
        self.cost_function.problem.jacobian = jac
        self.cost_function.problem.hessian = hes
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian
        hessian = Analytic(self.cost_function.problem,
                           self.cost_function.jacobian)
        self.cost_function.hessian = hessian

        H, _ = self.cost_function.hes_res(params=[5],
                                          x=self.x_val,
                                          y=self.y_val)

        expected = np.array([[[300.96, 19201.6, 36303.2],
                              [300.96, 19201.6, 36303.2]],
                             [[300.96, 19201.6, 36303.2],
                              [300.96, 19201.6, 36303.2]]])
        print(H)
        self.assertTrue(np.allclose(H, expected))

    def test_validate_problem_correct(self):
        """
        Test that validate_problem does not raise an error
        """
        self.cost_function.validate_problem()

    def test_validate_problem_incorrect(self):
        """
        Test that validate_problem does raise an error when y has negative vals
        """
        self.cost_function.problem.data_y[2] = -0.05
        with self.assertRaises(IncompatibleCostFunctionError):
            self.cost_function.validate_problem()


class FactoryTests(TestCase):
    """
    Tests for the cost function factory
    """

    def test_imports(self):
        """
        Test that the factory returns the correct class for inputs
        """
        self.options = Options()

        valid = ['weighted_nlls', 'nlls', 'hellinger_nlls', 'poisson']
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
