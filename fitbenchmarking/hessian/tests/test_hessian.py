"""
Unit testing for the hessian directory.
"""
from unittest import TestCase

import numpy as np

from fitbenchmarking.cost_func.hellinger_nlls_cost_func import \
    HellingerNLLSCostFunc
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.cost_func.poisson_cost_func import PoissonCostFunc
from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.hessian.analytic_hessian import Analytic
from fitbenchmarking.hessian.best_available_hessian import BestAvailable
from fitbenchmarking.hessian.hessian_factory import create_hessian
from fitbenchmarking.hessian.numdifftools_hessian import Numdifftools
from fitbenchmarking.hessian.scipy_hessian import Scipy
from fitbenchmarking.jacobian.analytic_jacobian import \
    Analytic as JacobianClass
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.log import get_logger
from fitbenchmarking.utils.options import Options

LOGGER = get_logger()


def f_ls(x, p1, p2):
    """
    Test function for numerical Hessians, to
    be used with nlls cost functions
    """
    return (x*(p1+p2)**2)**2


def J_ls(x, p):
    """
    Analyic Jacobian evaluation of f_ls
    """
    return np.column_stack((4*x**2*(p[0]+p[1])**3,
                            4*x**2*(p[0]+p[1])**3))


def H_ls(x, p):
    """
    Analyic Hessian evaluation of f_ls
    """
    return np.array([[12*x**2*(p[0]+p[1])**2, 12*x**2*(p[0]+p[1])**2],
                     [12*x**2*(p[0]+p[1])**2, 12*x**2*(p[0]+p[1])**2], ])


def grad2_r_nlls(x, p):
    """
    Calculate 2nd partial derivatives of residuals (y-f_ls)
    for nlls cost function
    """
    return np.array([[-12*x**2*(p[0]+p[1])**2, -12*x**2*(p[0]+p[1])**2],
                     [-12*x**2*(p[0]+p[1])**2, -12*x**2*(p[0]+p[1])**2], ])


def grad2_r_weighted_nlls(x, e, p):
    """
    Calculate 2nd partial derivatives of residuals (y-f_ls)/e
    for weighted nlls cost function
    """
    return np.array([[-12*x**2*(p[0]+p[1])**2/e, -12*x**2*(p[0]+p[1])**2/e],
                     [-12*x**2*(p[0]+p[1])**2/e, -12*x**2*(p[0]+p[1])**2/e], ])


def grad2_r_hellinger(x):
    """
    Calculate 2nd partial derivatives of residuals (sqrt(y)-sqrt(f_ls))
    for hellinger nlls cost function
    """
    return np.array([[-2*x, -2*x], [-2*x, -2*x], ])


def f_poisson(x, p1, p2):
    """
    Test function for numerical Hessians, to
    be used with poisson cost function
    """
    return p1*np.exp(p2*x)


def J_poisson(x, p):
    """
    Analyic Jacobian evaluation of f_poisson
    """
    return np.column_stack((np.exp(p[1]*x),
                            p[0]*x*np.exp(p[1]*x)))


def H_poisson(x, p):
    """
    Analyic Hessian evaluation of f_poisson
    """
    return np.array([[np.zeros(x.shape[0]),
                      x*np.exp((x*p[1]))],
                     [x*np.exp((x*p[1])),
                      p[0]*x**2*np.exp((x*p[1]))], ])


def grad2_r_poisson(x, y, p):
    """
    Calculate 2nd partial derivatives of residuals
    (y(log(y)-log(f_poisson))-(y-f_poisson))
    for poisson cost function
    """
    return np.array([[y/p[0]**2,
                      x*np.exp(p[1]*x)],
                     [x*np.exp((x*p[1])),
                      p[0]*x**2*np.exp((x*p[1]))], ])


class TestHessianName(TestCase):
    """
    Tests for the name function
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        self.fitting_problem = FittingProblem(options)
        self.fitting_problem.function = f_ls
        self.fitting_problem.jacobian = J_ls
        self.fitting_problem.hessian = H_ls
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.jacobian = JacobianClass(self.fitting_problem)

    def test_scipy_hessian(self):
        """
        Test the name is correct for the scipy hessian.
        """
        hessian = Scipy(self.fitting_problem, self.jacobian)
        hessian.method = 'some_method'
        self.assertEqual(hessian.name(), "scipy some_method")

    def test_analytic_hessian(self):
        """
        Test the name is correct for the analytic hessian.
        """
        hessian = Analytic(self.fitting_problem, self.jacobian)
        hessian.method = 'some_method'
        self.assertEqual(hessian.name(), "analytic")


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
        self.fitting_problem.function = f_ls
        self.fitting_problem.jacobian = J_ls
        self.fitting_problem.hessian = H_ls
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.params = [6, 0.1]
        self.actual_hessian = H_ls(x=self.fitting_problem.data_x,
                                   p=self.params)
        self.cost_func = NLLSCostFunc(self.fitting_problem)
        self.jacobian = JacobianClass(self.fitting_problem)
        self.hessian = Analytic(self.fitting_problem, self.jacobian)

    def test_analytic_nlls(self):
        """
        Test analytic Hessian
        """
        self.cost_func.jacobian = self.jacobian
        self.cost_func.hessian = self.hessian
        eval_result, _ = self.cost_func.hes_res(params=self.params)
        actual_hessian = grad2_r_nlls(self.fitting_problem.data_x,
                                      self.params)

        self.assertTrue(np.isclose(actual_hessian, eval_result).all())

    def test_analytic_weighted_nlls(self):
        """
        Test analytic Hessian for weighted_nlls
        """
        e = np.array([1, 2, 1, 3, 1])
        self.fitting_problem.data_e = e
        self.cost_func = WeightedNLLSCostFunc(self.fitting_problem)
        self.cost_func.jacobian = self.jacobian
        self.cost_func.hessian = self.hessian
        eval_result, _ = self.cost_func.hes_res(params=self.params)
        actual_hessian = grad2_r_weighted_nlls(
            self.fitting_problem.data_x, e, self.params)

        self.assertTrue(np.isclose(actual_hessian, eval_result).all())

    def test_analytic_hellinger_nlls(self):
        """
        Test analytic Hessian for hellinger_nlls
        """
        self.cost_func = HellingerNLLSCostFunc(self.fitting_problem)
        self.cost_func.jacobian = self.jacobian
        self.cost_func.hessian = self.hessian
        eval_result, _ = self.cost_func.hes_res(params=self.params)
        actual_hessian = grad2_r_hellinger(self.fitting_problem.data_x)

        self.assertTrue(np.isclose(actual_hessian, eval_result).all())

    def test_poisson(self):
        """
        Test analytic Hessian for poisson cost function
        """
        self.fitting_problem.function = f_poisson
        self.fitting_problem.jacobian = J_poisson
        self.fitting_problem.hessian = H_poisson
        self.cost_func = PoissonCostFunc(self.fitting_problem)
        self.cost_func.jacobian = self.jacobian
        self.cost_func.hessian = self.hessian
        eval_result, _ = self.cost_func.hes_res(params=self.params)
        actual_hessian = grad2_r_poisson(self.fitting_problem.data_x,
                                         self.fitting_problem.data_y,
                                         self.params)

        self.assertTrue(np.isclose(actual_hessian, eval_result).all())

    def test_scipy_eval(self):
        """
        Test whether Scipy evaluation is correct
        """
        for method in ['2-point',
                       '3-point',
                       'cs']:
            hes = Scipy(self.cost_func.problem, self.jacobian)
            hes.method = method
            eval_result = hes.eval(params=self.params)
            self.assertTrue(np.isclose(self.actual_hessian, eval_result).all())

    def test_numdifftools(self):
        """
        Test whether numdifftools evaluation is correct
        """
        for method in ['central',
                       'forward',
                       'backward',
                       'complex',
                       'multicomplex']:
            hes = Numdifftools(self.cost_func.problem, self.jacobian)
            hes.method = method
            eval_result = hes.eval(params=self.params)
            self.assertTrue(np.isclose(self.actual_hessian, eval_result).all())

    def test_analytic_raise_error(self):
        """
        Test analytic Hessian raises an exception when problem.hessian is
        not callable
        """
        self.fitting_problem.hessian = None
        with self.assertRaises(exceptions.NoHessianError):
            Analytic(self.cost_func.problem, self.jacobian)


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
        self.fitting_problem.function = f_ls
        self.fitting_problem.jacobian = J_ls
        self.fitting_problem.hessian = H_ls
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.params = [6, 0.1]
        self.cost_func = NLLSCostFunc(self.fitting_problem)
        self.cost_func.jacobian = JacobianClass(self.cost_func.problem)

        J_eval = -1*J_ls(x=self.fitting_problem.data_x,
                         p=self.params)
        r_nlls = self.fitting_problem.data_y - \
            f_ls(self.fitting_problem.data_x, self.params[0], self.params[1])
        actual_hessian = grad2_r_nlls(self.fitting_problem.data_x, self.params)
        self.actual = 2.0 * (np.matmul(J_eval.T, J_eval)
                             + np.matmul(actual_hessian, r_nlls))

    def test_scipy_eval(self):
        """
        Test whether Scipy evaluation is correct
        """
        for method in ['2-point',
                       '3-point',
                       'cs']:
            hes = Scipy(self.cost_func.problem, self.cost_func.jacobian)
            hes.method = method
            self.cost_func.hessian = hes
            eval_result = self.cost_func.hes_cost(params=self.params)
            self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_numdifftools(self):
        """
        Test whether numdifftools evaluation is correct
        """
        for method in ['central',
                       'forward',
                       'backward',
                       'complex',
                       'multicomplex']:
            hes = Numdifftools(self.cost_func.problem, self.cost_func.jacobian)
            hes.method = method
            self.cost_func.hessian = hes
            eval_result = self.cost_func.hes_cost(params=self.params)
            self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_analytic_cutest(self):
        """
        Test analytic hessian
        """
        self.fitting_problem.format = "cutest"
        self.cost_func.hessian = Analytic(self.cost_func.problem,
                                          self.cost_func.jacobian)
        eval_result = self.cost_func.hes_cost(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())


class TestBestAvailable(TestCase):
    """
    Additional tests to check the best_available jacobian
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        self.fitting_problem = FittingProblem(options)
        self.fitting_problem.function = f_ls
        self.fitting_problem.jacobian = J_ls
        self.fitting_problem.hessian = H_ls
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.jacobian = JacobianClass(self.fitting_problem)

    def test_name(self):
        """
        Test the name is not taken from a sub jacobian.
        """
        hes = BestAvailable(self.fitting_problem, self.jacobian)
        self.assertNotEqual(hes.name(), hes.sub_hes.name())

    def test_set_method_warning(self):
        """
        Test that setting the method raises a warning.
        """
        hes = BestAvailable(self.fitting_problem, self.jacobian)
        with self.assertLogs(LOGGER, level='WARNING') as log:
            hes.method = "three"
            self.assertTrue("Method cannot be selected" in log.output[0])

    def test_set_method_value(self):
        """
        Test that setting the method does not work.
        """
        hes = BestAvailable(self.fitting_problem, self.jacobian)
        hes.method = "three"
        self.assertNotEqual(hes.method, "three")

    def test_eval_callable_jac(self):
        """
        Test that an analytic jacobian is used when jac is callable.
        """
        hes = BestAvailable(self.fitting_problem, self.jacobian)
        self.assertEqual(type(hes.sub_hes), Analytic)

    def test_eval_not_callable_jac(self):
        """
        Test that a scipy jacobian is used when jac is not callable.
        """
        self.fitting_problem.hessian = None
        hes = BestAvailable(self.fitting_problem, self.jacobian)
        self.assertEqual(type(hes.sub_hes), Scipy)


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
