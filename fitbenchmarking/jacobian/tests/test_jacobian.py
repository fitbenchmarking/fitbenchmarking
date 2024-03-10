"""
Unit testing for the jacobian directory.
"""
from unittest import TestCase

import numpy as np
from scipy import sparse
from scipy.sparse import issparse

from fitbenchmarking.cost_func.hellinger_nlls_cost_func import \
    HellingerNLLSCostFunc
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.cost_func.poisson_cost_func import PoissonCostFunc
from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.jacobian.analytic_jacobian import Analytic
from fitbenchmarking.jacobian.default_jacobian import Default
from fitbenchmarking.jacobian.jacobian_factory import create_jacobian
from fitbenchmarking.jacobian.numdifftools_jacobian import Numdifftools
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.exceptions import (NoSparseJacobianError,
                                              SparseJacobianIsDenseError)
from fitbenchmarking.utils.options import Options


def f(x, p1, p2):
    """
    Test function for numerical Jacobians

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


def j(x, p):
    """
    Analytic Jacobian evaluation

    :param x: x data points, defaults to self.data_x
    :type x: numpy array, optional
    :param p: list of parameters to fit
    :type p: list

    :return: Jacobian evaluation
    :rtype: 1D numpy array
    """
    return np.column_stack((np.exp(p[1] * x),
                            x * p[0] * np.exp(p[1] * x)))


def j_sparse(x, p):
    """
    Sparse Jacobian evaluation

    :param x: x data points, defaults to self.data_x
    :type x: numpy array, optional
    :param p: list of parameters to fit
    :type p: list

    :return: Sparse Jacobian evaluation
    :rtype: 1D numpy array
    """
    return sparse.csr_matrix(j(x, p))


def J(x, p):
    """
    Analytic Jacobian residuals evaluation

    :param x: x data points, defaults to self.data_x
    :type x: numpy array, optional
    :param p: list of parameters to fit
    :type p: list

    :return: Jacobian residuals evaluation
    :rtype: 1D numpy array
    """
    # pylint: disable=invalid-unary-operand-type
    return - j(x, p)


def J_weighted(x, e, p):
    """
    Analytic Jacobian evaluation for weighted_nlls
    cost function
    """
    return np.column_stack((-(np.exp(p[1] * x) / e),
                            -(x * p[0] * np.exp(p[1] * x)) / e))


def J_hellinger(x, p):
    """
    Analytic Jacobian evaluation for hellinger_nlls
    cost function
    """
    return np.column_stack((-1/2*(p[0]*np.exp(p[1]*x))**(-1/2)*np.exp(p[1]*x),
                            -1/2*(p[0]*np.exp(p[1]*x))**(-1/2)
                            * p[0]*x*np.exp(p[1]*x)))


def J_poisson(x, y, p):
    """
    Analytic Jacobian evaluation for poisson
    cost function
    """
    return np.column_stack((-y/p[0]+np.exp(p[1]*x),
                            -y*x+p[0]*x*np.exp(p[1]*x)))


class TestJacobianName(TestCase):
    """
    Tests for the name function
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        self.fitting_problem = FittingProblem(options)
        self.fitting_problem.function = f
        self.fitting_problem.jacobian = j
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])

    def test_scipy_jacobian(self):
        """
        Test the name is correct for the scipy jacobian.
        """
        jacobian = Scipy(self.fitting_problem)
        jacobian.method = 'some_method'
        self.assertEqual(jacobian.name(), "scipy some_method")

    def test_analytic_jacobian(self):
        """
        Test the name is correct for the analytic jacobian.
        """
        jacobian = Analytic(self.fitting_problem)
        jacobian.method = 'some_method'
        self.assertEqual(jacobian.name(), "analytic")


class TestJacobianClass(TestCase):
    """
    Tests for Jacobian classes
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        options.cost_func_type = "nlls"
        self.fitting_problem = FittingProblem(options)
        self.fitting_problem.function = f
        self.fitting_problem.jacobian = j
        self.fitting_problem.sparse_jacobian = j_sparse
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.cost_func = NLLSCostFunc(self.fitting_problem)
        self.params = [6, 0.1]
        self.actual = j(x=self.fitting_problem.data_x, p=self.params)

    def test_default(self):
        """
        Test that minimizer default jacobian does what it should
        """
        jac = Default(self.cost_func.problem)
        self.assertTrue(jac.use_default_jac)

        eval_result = jac.eval(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_scipy_eval(self):
        """
        Test whether Scipy evaluation is correct
        """
        for method in ['2-point',
                       '3-point',
                       'cs']:
            jac = Scipy(self.cost_func.problem)
            jac.method = method
            eval_result = jac.eval(params=self.params)
            self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_scipy_eval_returns_correct_sparse_jac(self):
        """
        Test whether Scipy evaluation is correct when
        using sparsity
        """
        jac = Scipy(self.cost_func.problem)
        jac.method = '2-point_sparse'
        eval_result = jac.eval(params=self.params)

        self.assertTrue(np.isclose(self.actual, eval_result.todense()).all())
        self.assertTrue(issparse(eval_result))

    def test_scipy_eval_raises_error_sparsej_dense(self):
        """
        Test that Scipy evaluation raises error when
        result of sparse jacobian is not in sparse format
        """
        self.fitting_problem.sparse_jacobian = j
        jac = Scipy(self.cost_func.problem)
        jac.method = '2-point_sparse'
        with self.assertRaises(SparseJacobianIsDenseError):
            jac.eval(params=self.params)

    def test_scipy_eval_raises_error_no_sparsej(self):
        """
        Test that Scipy evaluation raises error when
        result of sparse jacobian is None
        """
        self.fitting_problem.sparse_jacobian = None
        jac = Scipy(self.cost_func.problem)
        jac.method = '2-point_sparse'
        with self.assertRaises(NoSparseJacobianError):
            jac.eval(params=self.params)

    def test_scipy_eval_calls_slagjac_when_cutest(self):
        """
        Test scipy eval calls slagjac with cutest
        problems
        """
        # TO DO
        return

    def test_numdifftools_eval(self):
        """
        Test whether numdifftools evaluation is correct
        """
        for method in ['central',
                       'forward',
                       'backward',
                       'complex',
                       'multicomplex']:
            jac = Numdifftools(self.cost_func.problem)
            jac.method = method
            eval_result = jac.eval(params=self.params)
            self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_analytic_cutest_no_errors(self):
        """
        Test analytic Jacobian
        """
        self.fitting_problem.format = "cutest"
        jac = Analytic(self.cost_func.problem)
        self.cost_func.jacobian = jac
        eval_result = self.cost_func.jac_res(params=self.params)
        actual = J(self.fitting_problem.data_x, self.params)
        self.assertTrue(np.isclose(actual, eval_result).all())

    def test_analytic_eval_returns_correct_sparse_jac(self):
        """
        Test whether analytic jac evaluation is correct
        when using sparsity
        """
        jac = Analytic(self.cost_func.problem)
        self.cost_func.jacobian = jac
        jac.method = 'sparse'
        eval_result = self.cost_func.jac_res(params=self.params)
        actual = J(self.fitting_problem.data_x, self.params)
        self.assertTrue(np.isclose(actual, eval_result.todense()).all())
        self.assertTrue(issparse(eval_result))
        return

    def test_analytic_eval_raises_error_no_sparsej(self):
        """
        Test that analytic jac evaluation raises error when
        result of sparse jacobian is None
        """
        self.fitting_problem.sparse_jacobian = None
        jac = Analytic(self.cost_func.problem)
        self.cost_func.jacobian = jac
        jac.method = 'sparse'
        with self.assertRaises(NoSparseJacobianError):
            self.cost_func.jac_res(params=self.params)

    def test_analytic_eval_raises_error_sparsej_dense(self):
        """
        Test that analytic jac evaluation raises error when
        result of sparse jacobian is not in sparse format
        """
        self.fitting_problem.sparse_jacobian = j
        jac = Analytic(self.cost_func.problem)
        self.cost_func.jacobian = jac
        jac.method = 'sparse'
        with self.assertRaises(SparseJacobianIsDenseError):
            self.cost_func.jac_res(params=self.params)

    def test_analytic_cutest_weighted(self):
        """
        Test analytic Jacobian
        """
        self.fitting_problem.data_e = np.array([1, 2, 1, 3, 1])
        self.fitting_problem.format = "cutest"
        self.cost_func = WeightedNLLSCostFunc(self.fitting_problem)
        self.cost_func.jacobian = Analytic(self.cost_func.problem)
        eval_result = self.cost_func.jac_res(params=self.params)
        actual = J_weighted(self.fitting_problem.data_x,
                            self.fitting_problem.data_e, self.params)
        self.assertTrue(np.isclose(actual, eval_result).all())

    def test_analytic_cutest_hellinger(self):
        """
        Test analytic Jacobian
        """
        self.fitting_problem.format = "cutest"
        self.cost_func = HellingerNLLSCostFunc(self.fitting_problem)
        self.cost_func.jacobian = Analytic(self.cost_func.problem)
        eval_result = self.cost_func.jac_res(params=self.params)
        actual = J_hellinger(self.fitting_problem.data_x, self.params)
        self.assertTrue(np.isclose(actual, eval_result).all())

    def test_analytic_cutest_poisson(self):
        """
        Test analytic jacobian for the poisson cost function.
        """
        self.fitting_problem.format = "cutest"
        self.cost_func = PoissonCostFunc(self.fitting_problem)
        self.cost_func.jacobian = Analytic(self.cost_func.problem)
        eval_result = self.cost_func.jac_res(params=self.params)
        actual = J_poisson(self.fitting_problem.data_x,
                           self.fitting_problem.data_y, self.params)
        print(str(actual))
        print(str(eval_result))
        self.assertTrue(np.isclose(actual, eval_result).all())

    def test_analytic_raise_error(self):
        """
        Test analytic Jacobian raises an exception when problem.jacobian is
        not callable
        """
        self.fitting_problem.jacobian = None
        with self.assertRaises(exceptions.NoJacobianError):
            Analytic(self.cost_func.problem)


class TestDerivCostFunc(TestCase):
    """
    Tests for Jacobian classes
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        options.cost_func_type = "nlls"
        self.fitting_problem = FittingProblem(options)
        self.fitting_problem.function = f
        self.fitting_problem.jacobian = j
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.params = [6, 0.1]
        self.cost_func = NLLSCostFunc(self.fitting_problem)
        J_eval = J(x=self.fitting_problem.data_x,
                   p=self.params)
        f_eval = self.fitting_problem.data_y - f(x=self.fitting_problem.data_x,
                                                 p1=self.params[0],
                                                 p2=self.params[1])
        self.actual = 2.0 * np.matmul(J_eval.T, f_eval)

    def test_scipy_eval(self):
        """
        Test whether Scipy evaluation is correct
        """
        for method in ['2-point',
                       '3-point',
                       'cs']:
            jac = Scipy(self.cost_func.problem)
            jac.method = method
            self.cost_func.jacobian = jac
            eval_result = self.cost_func.jac_cost(params=self.params)
            self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_numdifftools_eval(self):
        """
        Test whether numdifftools evaluation is correct
        """
        for method in ['central',
                       'forward',
                       'backward',
                       'complex',
                       'multicomplex']:
            jac = Numdifftools(self.cost_func.problem)
            jac.method = method
            self.cost_func.jacobian = jac
            eval_result = self.cost_func.jac_cost(params=self.params)
            self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_analytic_cutest(self):
        """
        Test analytic jacobian
        """
        self.fitting_problem.format = "cutest"
        jac = Analytic(self.cost_func.problem)
        self.fitting_problem.jac = jac
        self.cost_func.jacobian = jac
        eval_result = self.cost_func.jac_cost(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())


class TestFactory(TestCase):
    """
    Tests for the Jacobian factory
    """

    def setUp(self):
        self.options = Options()

    def test_imports(self):
        """
        Test that the factory returns the correct class for inputs
        """
        valid = ['scipy', 'analytic']

        invalid = ['numpy', 'random_jac']

        for jac_method in valid:
            jac = create_jacobian(jac_method)
            self.assertTrue(jac.__name__.lower().startswith(jac_method))

        for jac_method in invalid:
            self.assertRaises(exceptions.NoJacobianError,
                              create_jacobian,
                              jac_method)
