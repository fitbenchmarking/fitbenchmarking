"""
Tests available cost function classes in FitBenchmarking.
"""

import logging
from unittest import TestCase
from unittest.mock import MagicMock

import numpy as np

from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.cost_func.hellinger_nlls_cost_func import (
    HellingerNLLSCostFunc,
)
from fitbenchmarking.cost_func.loglike_nlls_cost_func import (
    LoglikeNLLSCostFunc,
)
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.cost_func.poisson_cost_func import (
    PoissonCostFunc,
    _safe_a_log_b,
)
from fitbenchmarking.cost_func.weighted_nlls_cost_func import (
    WeightedNLLSCostFunc,
)
from fitbenchmarking.cost_func.whitened_nlls_cost_func import (
    WhitenedNLLSCostFunc,
)
from fitbenchmarking.hessian.analytic_hessian import Analytic
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.exceptions import IncompatibleCostFunctionError
from fitbenchmarking.utils.options import Options


def fun(x, p):
    """
    Analytic function evaluation
    """
    return (x * p**2) ** 2


def jac(x, p):
    """
    Analytic Jacobian evaluation
    """
    return np.column_stack((4 * x**2 * p[0] ** 3, 4 * x**2 * p[0] ** 3))


def hes(x, p):
    """
    Analytic Hessian evaluation
    """
    return np.array(
        [
            [12 * x**2 * p[0] ** 2, 12 * x**2 * p[0] ** 2],
            [12 * x**2 * p[0] ** 2, 12 * x**2 * p[0] ** 2],
        ]
    )


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
        self.assertRaises(
            exceptions.CostFuncError,
            self.cost_function.eval_r,
            params=[1, 2, 3],
            x=[2],
            y=[3, 4],
        )

    def test_eval_r_correct_evaluation(self):
        """
        Test that eval_r is running the correct function
        """
        eval_result = self.cost_function.eval_r(
            x=self.x_val, y=self.y_val, params=[5]
        )
        self.assertTrue(all(eval_result == np.array([0, -3, 4])))

    def test_eval_cost(self):
        """
        Test that eval_cost is correct
        """
        eval_result = self.cost_function.eval_cost(
            params=[5], x=self.x_val, y=self.y_val
        )
        self.assertEqual(eval_result, 25)

    def test_validate_algorithm_type_error(self):
        """
        Test that validate_algorithm_type raises an error
        for incompatible options
        """
        self.cost_function.invalid_algorithm_types = ["ls"]
        algorithm_check = {"ls": ["ls-min"]}
        minimizer = "ls-min"

        self.assertRaises(
            exceptions.IncompatibleMinimizerError,
            self.cost_function.validate_algorithm_type,
            algorithm_check=algorithm_check,
            minimizer=minimizer,
        )

    def test_validate_algorithm_type_correct(self):
        """
        Test that validate_algorithm_type does not raise
        an error for compatible options
        """
        self.cost_function.invalid_algorithm_types = []
        algorithm_check = {"ls": ["ls-min"]}
        minimizer = "ls-min"

        self.cost_function.validate_algorithm_type(algorithm_check, minimizer)

    def test_validate_problem_correct(self):
        """
        Test that validate_problem does not raise an error
        """
        self.cost_function.validate_problem()

    def test_validate_problem_no_warning_without_covariance(self):
        """
        No warning is emitted when the problem has no covariance matrix
        """
        with self.assertLogs("fitbenchmarking", level="WARNING") as cm:
            # emit an unrelated warning so assertLogs does not fail on empty
            logging.getLogger("fitbenchmarking").warning("sentinel")
            self.cost_function.validate_problem()
        self.assertEqual(len(cm.output), 1, "Expected no covariance warning")

    def test_validate_problem_warns_when_covariance_present(self):
        """
        A warning is emitted when the problem supplies a covariance matrix
        but the cost function does not use it
        """
        self.cost_function.problem.additional_info = {
            "covariance": np.diag([4.0, 16.0, 1.0])
        }
        with self.assertLogs("fitbenchmarking", level="WARNING") as cm:
            self.cost_function.validate_problem()
        self.assertTrue(
            any("covariance" in msg for msg in cm.output),
            "Expected a covariance warning in log output",
        )

    def test_jac_res(self):
        """
        Test that jac_res works for the NLLs cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        jacobian_of_residual = self.cost_function.jac_res(
            params=[5], x=self.x_val, y=self.y_val
        )

        expected = np.array([[-1.0], [-1.0], [-1.0]])
        self.assertTrue(np.allclose(jacobian_of_residual, expected))

    def test_jac_cost(self):
        """
        Test that jac_cost works for the NLLs cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        jac_cost = self.cost_function.jac_cost(
            params=[5], x=self.x_val, y=self.y_val
        )

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
        hessian = Analytic(
            self.cost_function.problem, self.cost_function.jacobian
        )
        self.cost_function.hessian = hessian

        hessian_of_residual, _ = self.cost_function.hes_res(
            params=[5], x=self.x_val, y=self.y_val
        )

        expected = np.array(
            [
                [[-300.0, -19200.0, -36300.0], [-300.0, -19200.0, -36300.0]],
                [[-300.0, -19200.0, -36300.0], [-300.0, -19200.0, -36300.0]],
            ]
        )
        self.assertTrue(np.allclose(hessian_of_residual, expected))

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
        hessian = Analytic(
            self.cost_function.problem, self.cost_function.jacobian
        )
        self.cost_function.hessian = hessian

        hes_cost = self.cost_function.hes_cost(
            params=[0.01], x=self.x_val, y=self.y_val
        )

        expected = np.array(
            [[-7.35838895, -7.35838895], [-7.35838895, -7.35838895]]
        )
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
        self.assertRaises(
            exceptions.CostFuncError,
            self.cost_function.eval_r,
            params=[1, 2, 3],
            x=[2],
            y=[3, 4, 5],
            e=[23, 4],
        )

    def test_eval_r_correct_evaluation(self):
        """
        Test that eval_r is running the correct function
        """

        eval_result = self.cost_function.eval_r(
            x=self.x_val, y=self.y_val, e=self.e_val, params=[5]
        )
        self.assertTrue(all(eval_result == np.array([0, -0.75, 4])))

    def test_eval_cost(self):
        """
        Test that eval_cost is correct
        """
        eval_result = self.cost_function.eval_cost(
            params=[5], x=self.x_val, y=self.y_val, e=self.e_val
        )
        self.assertEqual(eval_result, 16.5625)

    def test_eval_r_multifit(self):
        """
        Test that eval_r evaluates the residuals for each dataset and
        concatenates them in the multifit case
        """
        options = Options()
        fitting_problem = FittingProblem(options)
        fitting_problem.multifit = True
        fitting_problem.function = lambda x, p1: x + p1
        # d0.p1=5, d1.p1=100
        fitting_problem.multifit_param_names = ["d0.p1", "d1.p1"]
        fitting_problem.data_x = [
            np.array([1.0, 2.0]),
            np.array([3.0, 4.0]),
        ]
        fitting_problem.data_y = [
            np.array([10.0, 10.0]),
            np.array([110.0, 110.0]),
        ]
        fitting_problem.data_e = [
            np.array([1.0, 1.0]),
            np.array([1.0, 1.0]),
        ]
        cost_function = WeightedNLLSCostFunc(fitting_problem)

        eval_result = cost_function.eval_r(params=[5, 100])

        expected = np.array([4.0, 3.0, 7.0, 6.0])
        self.assertTrue(np.allclose(eval_result, expected))

    def test_jac_res_multifit_concatenates_errors(self):
        """
        Test that jac_res concatenates the per-dataset error arrays into a
        single array before scaling the Jacobian in the multifit case
        """
        # 4 residuals (2 per dataset) and a single parameter
        jac = np.array([[2.0], [2.0], [4.0], [4.0]])
        mock_jacobian = MagicMock()
        mock_jacobian.eval.return_value = jac
        self.cost_function.jacobian = mock_jacobian

        e = [np.array([2.0, 2.0]), np.array([4.0, 4.0])]
        jacobian_of_residual = self.cost_function.jac_res(params=[5], e=e)

        expected = np.array([[-1.0], [-1.0], [-1.0], [-1.0]])
        self.assertTrue(np.allclose(jacobian_of_residual, expected))

    def test_jac_res(self):
        """
        Test that jac_res works for the Weighted NLLs cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        jacobian_of_residual = self.cost_function.jac_res(
            params=[5], x=self.x_val, y=self.y_val, e=self.e_val
        )

        expected = np.array([[-0.5], [-0.25], [-1.0]])
        self.assertTrue(np.allclose(jacobian_of_residual, expected))

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
        hessian = Analytic(
            self.cost_function.problem, self.cost_function.jacobian
        )
        self.cost_function.hessian = hessian

        hessian_of_residual, _ = self.cost_function.hes_res(
            params=[5], x=self.x_val, y=self.y_val, e=self.e_val
        )

        expected = np.array(
            [
                [[-150.0, -4800.0, -36300.0], [-150.0, -4800.0, -36300.0]],
                [[-150.0, -4800.0, -36300.0], [-150.0, -4800.0, -36300.0]],
            ]
        )
        self.assertTrue(np.allclose(hessian_of_residual, expected))

    def test_validate_problem_correct(self):
        """
        Test that validate_problem does not raise an error
        """
        self.cost_function.validate_problem()


class TestLoglikeNLLSCostFunc(TestCase):
    """
    Class to test the LoglikeNLLSCostFunc class
    """

    def setUp(self):
        """
        Setting up log-likelihood nonlinear least squares cost function tests
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
        self.cost_function = LoglikeNLLSCostFunc(fitting_problem)

    def test_eval_r_raise_error(self):
        """
        Test that eval_r raises and error
        """
        self.assertRaises(
            exceptions.CostFuncError,
            self.cost_function.eval_r,
            params=[1, 2, 3],
            x=[2],
            y=[3, 4, 5],
            e=[23, 4],
        )

    def test_eval_r_correct_evaluation(self):
        """
        Test that eval_r is running the correct function
        """

        eval_result = self.cost_function.eval_r(
            x=self.x_val, y=self.y_val, e=self.e_val, params=[5]
        )
        self.assertTrue(all(eval_result == np.array([0, -0.75, 4])))

    def test_eval_cost(self):
        """
        Test that eval_cost is correct
        """
        eval_result = self.cost_function.eval_cost(
            params=[5], x=self.x_val, y=self.y_val, e=self.e_val
        )
        self.assertEqual(eval_result, 16.5625)

    def test_jac_res(self):
        """
        Test that jac_res works for the Log-likelihood NLLS cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        jacobian_of_residual = self.cost_function.jac_res(
            params=[5], x=self.x_val, y=self.y_val, e=self.e_val
        )

        expected = np.array([[-0.5], [-0.25], [-1.0]])
        self.assertTrue(np.allclose(jacobian_of_residual, expected))

    def test_hes_res(self):
        """
        Test that hes_res works for the Log-likelihood NLLS cost function
        """
        self.cost_function.problem.function = fun
        self.cost_function.problem.jacobian = jac
        self.cost_function.problem.hessian = hes
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian
        hessian = Analytic(
            self.cost_function.problem, self.cost_function.jacobian
        )
        self.cost_function.hessian = hessian

        hessian_of_residual, _ = self.cost_function.hes_res(
            params=[5], x=self.x_val, y=self.y_val, e=self.e_val
        )

        expected = np.array(
            [
                [[-150.0, -4800.0, -36300.0], [-150.0, -4800.0, -36300.0]],
                [[-150.0, -4800.0, -36300.0], [-150.0, -4800.0, -36300.0]],
            ]
        )
        self.assertTrue(np.allclose(hessian_of_residual, expected))

    def test_validate_problem_correct(self):
        """
        Test that validate_problem does not raise an error
        """
        self.cost_function.validate_problem()

    def test_eval_loglike(self):
        """
        Test that log-likelihood is evaluated correctly
        """
        loglike_result = self.cost_function.eval_loglike([5])
        self.assertEqual(loglike_result, -8.28125)


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
        self.assertRaises(
            exceptions.CostFuncError,
            self.cost_function.eval_r,
            params=[1, 2, 3],
            x=[2],
            y=[3, 4, 5],
        )

    def test_eval_r_correct_evaluation(self):
        """
        Test that eval_r is running the correct function
        """
        eval_result = self.cost_function.eval_r(
            x=self.x_val, y=self.y_val, params=[0]
        )
        expected = np.array(
            [1.4494897427831779, 0.33385053542218923, 1.1555111646441798]
        )
        self.assertTrue(all(eval_result == expected))

    def test_eval_cost(self):
        """
        Test that eval_cost is correct
        """
        eval_result = self.cost_function.eval_cost(
            params=[5], x=self.x_val, y=self.y_val
        )
        self.assertEqual(eval_result, 0.4194038580206052)

    def test_jac_res(self):
        """
        Test that jac_res works for the Hellinger NLLs cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        jacobian_of_residual = self.cost_function.jac_res(
            params=[5], x=self.x_val, y=self.y_val
        )

        expected = np.array([[-0.20412415], [-0.13867504], [-0.125]])
        self.assertTrue(np.allclose(jacobian_of_residual, expected))

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
        hessian = Analytic(
            self.cost_function.problem, self.cost_function.jacobian
        )
        self.cost_function.hessian = hessian

        hessian_of_residual, _ = self.cost_function.hes_res(
            params=[5], x=self.x_val, y=self.y_val
        )
        expected = np.array(
            [
                [[-2.0, -16.0, -22.0], [-2.0, -16.0, -22.0]],
                [[-2.0, -16.0, -22.0], [-2.0, -16.0, -22.0]],
            ]
        )
        self.assertTrue(np.allclose(hessian_of_residual, expected))

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
            _ = self.cost_function.eval_cost(params=[5], x=[2], y=[1, 3, 5])

    def test_eval_cost_correct(self):
        """
        Test that the eval cost function returns the correct value
        """
        eval_result = self.cost_function.eval_cost(
            params=[5], x=self.x_val, y=self.y_val
        )

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
        self.assertTrue(
            np.isclose(
                res,
                np.array(
                    [0.0, 2 * np.log(2), 3 * np.log(3), 0.0, 5 * np.log(5)]
                ),
            ).all()
        )

    def test_jac_res(self):
        """
        Test that jac_res works for the Poisson cost function
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        jacobian_of_residual = self.cost_function.jac_res(
            params=[5], x=self.x_val, y=self.y_val
        )

        expected = np.array([[0.0], [0.23076923], [-0.25]])
        self.assertTrue(np.allclose(jacobian_of_residual, expected))

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
        hessian = Analytic(
            self.cost_function.problem, self.cost_function.jacobian
        )
        self.cost_function.hessian = hessian

        hessian_of_residual, _ = self.cost_function.hes_res(
            params=[5], x=self.x_val, y=self.y_val
        )

        expected = np.array(
            [
                [[300.96, 19201.6, 36303.2], [300.96, 19201.6, 36303.2]],
                [[300.96, 19201.6, 36303.2], [300.96, 19201.6, 36303.2]],
            ]
        )
        self.assertTrue(np.allclose(hessian_of_residual, expected))

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


class TestWhitenedNLLSCostFunc(TestCase):
    """
    Tests for the WhitenedNLLSCostFunc class
    """

    def setUp(self):
        """
        Set up a problem with a diagonal covariance matching e=[2, 4, 1].
        The diagonal case lets us cross-check against WeightedNLLSCostFunc.
        """
        self.options = Options()
        fitting_problem = FittingProblem(self.options)
        fitting_problem.function = lambda x, p1: x + p1
        self.x_val = np.array([1.0, 8.0, 11.0])
        self.y_val = np.array([6.0, 10.0, 20.0])
        # diagonal covariance: e = [2, 4, 1] -> C = diag([4, 16, 1])
        self.cov = np.diag([4.0, 16.0, 1.0])
        fitting_problem.data_x = self.x_val
        fitting_problem.data_y = self.y_val
        fitting_problem.data_e = np.array([2.0, 4.0, 1.0])
        fitting_problem.additional_info = {"covariance": self.cov}
        self.cost_function = WhitenedNLLSCostFunc(fitting_problem)

    def test_init_raises_without_covariance(self):
        """
        Test that __init__ raises CostFuncError if covariance is absent
        """
        fitting_problem = FittingProblem(self.options)
        fitting_problem.function = lambda x, p1: x + p1
        fitting_problem.data_x = self.x_val
        fitting_problem.data_y = self.y_val
        fitting_problem.additional_info = {}
        self.assertRaises(
            exceptions.CostFuncError,
            WhitenedNLLSCostFunc,
            fitting_problem,
        )

    def test_eval_r_diagonal_matches_weighted_nlls(self):
        """
        Whitened residuals with diagonal C must equal (y - f) / e
        """
        result = self.cost_function.eval_r(
            x=self.x_val, y=self.y_val, params=[5]
        )
        expected = np.array([0.0, -0.75, 4.0])
        self.assertTrue(np.allclose(result, expected))

    def test_eval_cost_diagonal_matches_weighted_nlls(self):
        """
        Cost with diagonal C must equal sum((y - f)^2 / e^2)
        """
        result = self.cost_function.eval_cost(
            params=[5], x=self.x_val, y=self.y_val
        )
        self.assertAlmostEqual(result, 16.5625)

    def test_eval_r_off_diagonal_covariance(self):
        """
        Whitened residuals for a non-diagonal covariance are correct
        """
        # C = [[4, 2, 0], [2, 4, 0], [0, 0, 1]]
        # L = [[2, 0, 0], [1, sqrt(3), 0], [0, 0, 1]]
        # r = y - f(x, 5) = [0, -3, 4]
        # r_white = L^{-1} r = [0, -sqrt(3), 4]
        cov = np.array([[4.0, 2.0, 0.0], [2.0, 4.0, 0.0], [0.0, 0.0, 1.0]])
        fitting_problem = FittingProblem(self.options)
        fitting_problem.function = lambda x, p1: x + p1
        fitting_problem.data_x = self.x_val
        fitting_problem.data_y = self.y_val
        fitting_problem.additional_info = {"covariance": cov}
        cf = WhitenedNLLSCostFunc(fitting_problem)

        result = cf.eval_r(x=self.x_val, y=self.y_val, params=[5])
        expected = np.array([0.0, -np.sqrt(3), 4.0])
        self.assertTrue(np.allclose(result, expected))

    def test_jac_res_diagonal_matches_weighted_nlls(self):
        """
        Whitened Jacobian with diagonal C must equal -J / e
        """
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian

        result = self.cost_function.jac_res(
            params=[5], x=self.x_val, y=self.y_val
        )
        expected = np.array([[-0.5], [-0.25], [-1.0]])
        self.assertTrue(np.allclose(result, expected, atol=1e-5))

    def test_hes_res(self):
        """
        Test that hes_res returns sensible shapes for a linear model
        """
        self.cost_function.problem.function = fun
        self.cost_function.problem.jacobian = jac
        self.cost_function.problem.hessian = hes
        jacobian = Scipy(self.cost_function.problem)
        jacobian.method = "2-point"
        self.cost_function.jacobian = jacobian
        hessian = Analytic(
            self.cost_function.problem, self.cost_function.jacobian
        )
        self.cost_function.hessian = hessian

        hessian_of_residual, jacobian_of_residual = self.cost_function.hes_res(
            params=[5], x=self.x_val, y=self.y_val
        )
        # fun/jac helpers above use 2 Jacobian columns regardless of params
        n = len(self.x_val)
        self.assertEqual(hessian_of_residual.shape[2], n)
        self.assertEqual(
            hessian_of_residual.shape[0], hessian_of_residual.shape[1]
        )
        self.assertEqual(jacobian_of_residual.shape[0], n)

    def test_validate_problem_correct(self):
        """
        validate_problem must not raise when covariance is present
        """
        self.cost_function.validate_problem()

    def test_validate_problem_incorrect(self):
        """
        validate_problem must raise CostFuncError when covariance is absent
        """
        self.cost_function.problem.additional_info = {}
        self.assertRaises(
            exceptions.CostFuncError,
            self.cost_function.validate_problem,
        )

    def test_validate_problem_wrong_covariance_shape(self):
        """
        validate_problem must raise CostFuncError when covariance shape
        does not match the number of data points
        """
        self.cost_function.problem.additional_info = {
            "covariance": np.diag([1.0, 1.0])  # 2x2 but data has 3 points
        }
        self.assertRaises(
            exceptions.CostFuncError,
            self.cost_function.validate_problem,
        )


class FactoryTests(TestCase):
    """
    Tests for the cost function factory
    """

    def test_imports(self):
        """
        Test that the factory returns the correct class for inputs
        """
        self.options = Options()

        valid = ["weighted_nlls", "nlls", "hellinger_nlls", "poisson"]
        invalid = ["normal"]

        for cost_func_type in valid:
            cost_func = create_cost_func(cost_func_type)
            self.assertTrue(
                cost_func.__name__.lower().startswith(
                    cost_func_type.replace("_", "")
                )
            )

        for cost_func_type in invalid:
            self.assertRaises(
                exceptions.CostFuncError, create_cost_func, cost_func_type
            )
