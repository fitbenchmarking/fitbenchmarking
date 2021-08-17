"""
Unit testing for the hessian directory.
"""
from unittest import TestCase

import numpy as np

from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.cost_func.weighted_nlls_cost_func import\
    WeightedNLLSCostFunc
from fitbenchmarking.cost_func.hellinger_nlls_cost_func import\
    HellingerNLLSCostFunc
from fitbenchmarking.cost_func.poisson_cost_func import\
    PoissonCostFunc
from fitbenchmarking.hessian.analytic_hessian import Analytic
from fitbenchmarking.jacobian.analytic_jacobian import Analytic\
    as JacobianClass
from fitbenchmarking.hessian.hessian_factory import create_hessian
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


def f(x, p1, p2):
    """
    Test function for numerical Hessians

    :param x: x data points, defaults to self.data_x
    :type x: numpy array, optional
    :param p1: parameter 1
    :type p1: float
    :param p2: parameter 1
    :type p2: float

    :return: function evaluation
    :rtype: numpy array
    """
    return p1 * np.exp(p2 * x)


def J(x, p):
    """
    Analytic Jacobian evaluation

    :param x: x data points, defaults to self.data_x
    :type x: numpy array, optional
    :param p: list of parameters to fit
    :type p: list

    :return: Jacobian evaluation
    :rtype: numpy array
    """

    return np.column_stack((-np.exp(p[1] * x),
                            -x * p[0] * np.exp(p[1] * x)))


def H(x, p):
    """
    Analytic Hessian evaluation

    :param x: x data points, defaults to self.data_x
    :type x: numpy array, optional
    :param p: list of parameters to fit
    :type p: list

    :return: Hessian evaluation
    :rtype: numpy array
    """
    return np.array([[0*(np.ones(x.shape[0])), x*np.exp(p[1]*x)],
                    [x*np.exp(p[1]*x), p[0]*x**2*np.exp(p[1]*x)], ])


class TestHessianClass(TestCase):
    """
    Tests for Hessian classes
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        options.cost_func_type = "nlls"
        self.fitting_problem = FittingProblem(options)
        self.fitting_problem.function = f
        self.fitting_problem.jacobian = J
        self.fitting_problem.hessian = H
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.cost_func = NLLSCostFunc(self.fitting_problem)
        self.jacobian = JacobianClass(self.cost_func)
        self.params = [6, 0.1]
        self.actual = H(x=self.fitting_problem.data_x, p=self.params)
        self.jac_actual = J(x=self.fitting_problem.data_x, p=self.params)

    def test_analytic_cutest_no_errors(self):
        """
        Test analytic Hessian
        """
        self.fitting_problem.options.cost_func_type = "nlls"
        self.fitting_problem.format = "cutest"
        hes = Analytic(self.cost_func, self.jacobian)
        eval_result, _ = hes.eval(params=self.params)
        self.actual = np.matmul(self.actual,
                                self.fitting_problem.data_y -
                                f(self.fitting_problem.data_x,
                                  self.params[0], self.params[1]))
        self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_analytic_cutest_weighted(self):
        """
        Test analytic Hessian for weighted_nlls
        """
        self.cost_func = WeightedNLLSCostFunc(self.fitting_problem)
        self.fitting_problem.options.cost_func_type = "weighted_nlls"
        self.jacobian = JacobianClass(self.cost_func)
        e = np.array([1, 2, 1, 3, 1])
        self.fitting_problem.data_e = e
        self.fitting_problem.format = "cutest"
        hes = Analytic(self.cost_func, self.jacobian)
        eval_result, _ = hes.eval(params=self.params)
        scaled_actual = self.actual
        for i in range(len(e)):
            scaled_actual[:, :, i] = self.actual[:, :, i] / e[i]
        scaled_actual = np.matmul(scaled_actual,
                                  (self.fitting_problem.data_y -
                                   f(self.fitting_problem.data_x,
                                     self.params[0], self.params[1]))/e)
        self.assertTrue(np.isclose(scaled_actual, eval_result).all())

    def test_analytic_cutest_hellinger(self):
        """
        Test analytic Hessian for hellinger_nlls
        """
        self.cost_func = HellingerNLLSCostFunc(self.fitting_problem)
        self.fitting_problem.options.cost_func_type = "hellinger_nlls"
        self.jacobian = JacobianClass(self.cost_func)
        self.fitting_problem.format = "cutest"
        hes = Analytic(self.cost_func, self.jacobian)
        eval_result, _ = hes.eval(params=self.params)
        #jac_actual_h = self.jac_actual / \
        #    (2*np.sqrt(f(self.fitting_problem.data_x, *self.params)[:, None]))
        scaled_actual = self.actual
        # using jac_actual instad of jac scaled for hessian should return same
        # result as hessian.eval (where the scaled jac has been subbed in for
        # jac actual using formula J =  2*sqrt(f)*J_scaled)
        for i in range(len(self.fitting_problem.data_x)):
            scaled_actual[:, :, i] = 1/2*(
                f(self.fitting_problem.data_x, *self.params)**(-1/2))[i]\
                * self.actual[:, :, i] + \
                1/4*(f(self.fitting_problem.data_x, *self.params)**(-3/2))[i]\
                * np.matmul(self.jac_actual.T, self.jac_actual)
        scaled_actual = np.matmul(scaled_actual, np.sqrt(
            self.fitting_problem.data_y)-np.sqrt(f(self.fitting_problem.data_x,
                                                   self.params[0],
                                                   self.params[1])))
        print('actual')
        print(scaled_actual)
        print('eval')
        print(eval_result)
        self.assertTrue(np.isclose(scaled_actual, eval_result).all())

    def test_analytic_cutest_poisson(self):
        """
        Test analytic Hessian for poisson cost func
        """
        self.cost_func = PoissonCostFunc(self.fitting_problem)
        self.fitting_problem.options.cost_func_type = "poisson"
        self.jacobian = JacobianClass(self.cost_func)
        self.fitting_problem.format = "cutest"
        hes = Analytic(self.cost_func, self.jacobian)
        eval_result, _ = hes.eval(params=self.params)
        jac_actual_p = -np.matmul(self.jac_actual.T,
                                  (1 - self.fitting_problem.data_y /
                                   f(self.fitting_problem.data_x,
                                     *self.params)))
        scaled_actual = self.actual
        for i in range(len(self.fitting_problem.data_x)):
            scaled_actual[:, :, i] = scaled_actual[:, :, i]\
                * (1-self.fitting_problem.data_y /
                   f(self.fitting_problem.data_x, *self.params))[i]\
                + (self.fitting_problem.data_y /
                   f(self.fitting_problem.data_x, *self.params)**2)[i]\
                * np.matmul(jac_actual_p.T, jac_actual_p)
        scaled_actual = np.sum(scaled_actual, 2)
        self.assertTrue(np.isclose(scaled_actual, eval_result).all())

    def test_analytic_raise_error(self):
        """
        Test analytic Hessian raises an exception when problem.hessian is
        not callable
        """
        self.fitting_problem.hessian = None
        with self.assertRaises(exceptions.NoHessianError):
            Analytic(self.cost_func, self.jacobian)


class TestHesCostFunc(TestCase):
    """
    Tests for Hessian classes
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        options.cost_func_type = "nlls"
        self.fitting_problem = FittingProblem(options)
        self.fitting_problem.function = f
        self.fitting_problem.jacobian = J
        self.fitting_problem.hessian = H
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.params = [6, 0.1]
        self.cost_func = NLLSCostFunc(self.fitting_problem)
        self.jacobian = JacobianClass(self.cost_func)
        J_eval = J(x=self.fitting_problem.data_x,
                   p=self.params)
        H_eval = H(x=self.fitting_problem.data_x,
                   p=self.params)
        f_eval = self.fitting_problem.data_y - f(x=self.fitting_problem.data_x,
                                                 p1=self.params[0],
                                                 p2=self.params[1])
        self.actual = np.matmul(H_eval, f_eval) + np.matmul(J_eval.T, J_eval)

    def test_analytic_cutest(self):
        """
        Test analytic hessian
        """
        self.fitting_problem.format = "cutest"
        hes = Analytic(self.cost_func, self.jacobian)
        self.fitting_problem.hes = hes
        eval_result = hes.eval_cost(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())


class TestFactory(TestCase):
    """
    Tests for the Hessian factory
    """

    def setUp(self):
        self.options = Options()

    def test_imports(self):
        """
        Test that the factory returns the correct class for inputs
        """
        valid = ['analytic']

        invalid = ['random_hes']

        for hes_method in valid:
            hes = create_hessian(hes_method)
            self.assertTrue(hes.__name__.lower().startswith(hes_method))

        for hes_method in invalid:
            self.assertRaises(exceptions.NoHessianError,
                              create_hessian,
                              hes_method)
