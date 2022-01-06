"""
Tests for FitBenchmarking object
"""
from __future__ import absolute_import, division, print_function

import inspect
import os
import unittest

import numpy as np

from fitbenchmarking import mock_problems
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.hessian.analytic_hessian import \
    Analytic as AnalyticHessian
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


class FitbmResultTests(unittest.TestCase):
    """
    Tests for FitBenchmarking results object
    """

    def setUp(self):
        """
        Setting up FitBenchmarking results object
        """
        self.options = Options()
        mock_problems_dir = os.path.dirname(inspect.getfile(mock_problems))
        problem_dir = os.path.join(mock_problems_dir, "cubic.dat")
        self.problem = parse_problem_file(problem_dir, self.options)
        self.problem.correct_data()

        self.chi_sq = 10
        self.minimizer = "test_minimizer"
        self.runtime = 0.01
        self.params = np.array([1, 3, 4, 4])
        self.initial_params = np.array([0, 0, 0, 0])
        self.cost_func = NLLSCostFunc(self.problem)
        self.jac = Scipy(self.cost_func)
        self.jac.method = "2-point"
        self.hess = AnalyticHessian(self.cost_func.problem, self.jac)
        self.result = FittingResult(
            options=self.options, cost_func=self.cost_func, jac=self.jac,
            hess=self.hess, chi_sq=self.chi_sq, runtime=self.runtime,
            minimizer=self.minimizer, initial_params=self.initial_params,
            params=self.params, error_flag=0)

        self.min_chi_sq = 0.1
        self.result.min_chi_sq = self.min_chi_sq
        self.min_runtime = 1
        self.result.min_runtime = self.min_runtime

    def test_fitting_result_str(self):
        """
        Test that the fitting result can be printed as a readable string.
        """
        self.assertEqual(str(self.result),
                         "+================================+\n"
                         "| FittingResult                  |\n"
                         "+================================+\n"
                         "| Cost Function | NLLSCostFunc   |\n"
                         "+--------------------------------+\n"
                         "| Problem       | cubic          |\n"
                         "+--------------------------------+\n"
                         "| Software      | None           |\n"
                         "+--------------------------------+\n"
                         "| Minimizer     | test_minimizer |\n"
                         "+--------------------------------+\n"
                         "| Jacobian      | Scipy          |\n"
                         "+--------------------------------+\n"
                         "| Hessian       | Analytic       |\n"
                         "+--------------------------------+\n"
                         "| Chi Squared   | 10             |\n"
                         "+--------------------------------+\n"
                         "| Runtime       | 0.01           |\n"
                         "+--------------------------------+")

    def test_init_with_dataset_id(self):
        """
        Tests to check that the multifit id is setup correctly
        """
        chi_sq = [10, 5, 1]
        minimizer = "test_minimizer"
        runtime = 0.01
        params = [np.array([1, 3, 4, 4]),
                  np.array([2, 3, 57, 8]),
                  np.array([4, 2, 5, 1])]
        initial_params = np.array([0, 0, 0, 0])

        self.problem.data_x = [np.array([3, 2, 1, 4]),
                               np.array([5, 1, 2, 3]),
                               np.array([6, 7, 8, 1])]
        self.problem.data_y = [np.array([2, 1, 7, 40]),
                               np.array([8, 9, 4, 2]),
                               np.array([7, 4, 4, 2])]
        self.problem.data_e = [np.array([1, 1, 1, 1]),
                               np.array([2, 2, 2, 1]),
                               np.array([2, 3, 4, 4])]
        self.problem.sorted_index = [np.array([2, 1, 0, 3]),
                                     np.array([1, 2, 3, 0]),
                                     np.array([3, 0, 1, 2])]
        self.cost_func = NLLSCostFunc(self.problem)
        self.jac = Scipy(self.cost_func)
        self.jac.method = "2-point"
        self.hess = AnalyticHessian(self.cost_func.problem, self.jac)
        self.result = FittingResult(
            options=self.options, cost_func=self.cost_func, jac=self.jac,
            hess=self.hess, chi_sq=chi_sq, runtime=runtime,
            minimizer=minimizer, initial_params=initial_params, params=params,
            error_flag=0, dataset_id=1)

        self.assertTrue(
            np.isclose(self.result.data_x, self.problem.data_x[1]).all())
        self.assertTrue(
            np.isclose(self.result.data_y, self.problem.data_y[1]).all())
        self.assertTrue(
            np.isclose(self.result.data_e, self.problem.data_e[1]).all())
        self.assertTrue(
            np.isclose(self.result.sorted_index,
                       self.problem.sorted_index[1]).all())

        self.assertTrue(np.isclose(params[1], self.result.params).all())
        self.assertEqual(chi_sq[1], self.result.chi_sq)

    def test_norm_acc_finite_min(self):
        """
        Test that sanitised names are correct when min_chi_sq is finite.
        """
        expected = self.chi_sq / self.min_chi_sq
        self.assertEqual(self.result.norm_acc, expected)

    def test_norm_acc_infinite_min(self):
        """
        Test that sanitised names are correct when min_chi_sq is infinite.
        """
        expected = np.inf
        self.result.chi_sq = np.inf
        self.result.min_chi_sq = np.inf
        self.assertEqual(self.result.norm_acc, expected)

    def test_norm_runtime_finite_min(self):
        """
        Test that sanitised names are correct when min_runtime is finite.
        """
        expected = self.runtime / self.min_runtime
        self.assertEqual(self.result.norm_runtime, expected)

    def test_norm_runtime_infinite_min(self):
        """
        Test that sanitised names are correct when min_runtime is infinite.
        """
        expected = np.inf
        self.result.runtime = np.inf
        self.result.min_runtime = np.inf
        self.assertEqual(self.result.norm_runtime, expected)

    def test_sanitised_name(self):
        """
        Test that sanitised names are correct.
        """
        self.result.name = 'test, name with commas'
        self.assertEqual(self.result.sanitised_name, 'test_name_with_commas')

    def test_sanitised_min_name(self):
        """
        Test that sanitised minimizer names are correct.
        """
        self.result.minimizer = 'test: name with colon'
        self.assertEqual(self.result.sanitised_min_name,
                         'test_name_with_colon')


if __name__ == "__main__":
    unittest.main()
