from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

# Delete four lines below when automated tests are enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
parent_dir = os.path.dirname(os.path.normpath(parent_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from fitting.scipy.main import benchmark
from fitting.scipy.main import fit
from fitting.scipy.main import execute_fit
from fitting.scipy.main import chisq
from fitting.scipy.main import parse_result
from fitting.scipy.main import get_fittedy


class ScipyTests(unittest.TestCase):

    def setup_problem_success(self):
        """
        Helper function.
        Sets up the parameters needed to run fitting.mantid
        """
        data_pattern = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        data = np.array([data_pattern[:, 1], data_pattern[:, 0],
                         np.sqrt(data_pattern[:, 0])])
        exec "def fitting_function(x,b1,b2): return b1*(1-np.exp(-b2*x))"
        function = [fitting_function, [500.0, 250.0], "b1*(1-np.exp(-b2*x))"]
        minimizer = "lm"
        cost_function = "least squares"
        init_function_def = "b1*(1-exp(-b2*x)) | b1, b2"

        return data, function, minimizer, cost_function, init_function_def

    def setup_problem_fail(self):
        """
        Helper function.
        Sets up the parameters needed to run fitting.mantid
        """
        data_pattern = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        data = np.array([data_pattern[:, 1], data_pattern[:, 0],
                         np.sqrt(data_pattern[:, 0])])
        exec "def fitting_function(x,b1,b2): return b1*(1-np.exp(-b2*x))"
        function = [fitting_function, [500.0, 250.0], "b1*(1-np.exp(-b2*x))"]
        minimizer = "lmsda"  # the error
        cost_function = "least squares"
        init_function_def = "b1*(1-exp(-b2*x)) | b1, b2"

        return data, function, minimizer, cost_function, init_function_def

    def expected_results_problem_success(self):
        """
        Helper function.
        Sets up the expected results after running
        fitting.mantid with Misra1a.dat problem data.
        """

        fit_status = 'success'
        fin_function_def = "b1*(1-exp(-b2*x))  |  b1, b2"
        fitted_y_expected = [2.4, 2.4, 2.4, 2.4]

        return fit_status, fitted_y_expected, fin_function_def

    def setup_chisq_success(self):

        status = 'success'
        fitted_y = [2.4, 2.4, 2.4, 2.4]
        min_chi_sq = 30
        best_fit = None
        minimizer_name = 'lm'
        data_pattern = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        data = np.array([data_pattern[:, 1], data_pattern[:, 0],
                         np.sqrt(data_pattern[:, 0])])

        return status, data, fitted_y, min_chi_sq, best_fit, minimizer_name

    def test_fit_return_success_for_NIST_prob_file(self):

        data, function, minimizer, cost_function, init_function_def = \
            self.setup_problem_success()

        status, fitted_y, fin_def, runtime = \
            fit(data, function, minimizer, cost_function, init_function_def)
        status_expected, fitted_y_expected, fin_def_expected = \
            self.expected_results_problem_success()

        self.assertEqual(status_expected, status)
        np.testing.assert_allclose(fitted_y_expected, fitted_y, rtol=0.1)
        self.assertEqual(fin_def_expected, fin_def)

    def test_fit_return_fail_for_NIST_prob_file(self):

        data, function, minimizer, cost_function, init_function_def = \
            self.setup_problem_fail()

        status, fitted_y, fin_def, runtime = \
            fit(data, function, minimizer, cost_function, init_function_def)

        self.assertEqual("failed", status)
        self.assertEqual(None, fitted_y)
        self.assertEqual(None, fin_def)
        np.testing.assert_equal(np.nan, runtime)

    def test_chisq_status_failed(self):

        chi_sq, min_chi_sq, best_fit = \
            chisq('failed', None, None, None, None, None)

        self.assertEqual(None, min_chi_sq)
        self.assertEqual(None, best_fit)
        np.testing.assert_equal(np.nan, chi_sq)

    def test_chisq_status_success(self):

        status, data, fitted_y, min_chi_sq, best_fit, minimizer_name = \
            self.setup_chisq_success()

        chi_sq, min_chi_sq, best_fit = \
            chisq(status, data, fitted_y, min_chi_sq, best_fit, minimizer_name)

        np.testing.assert_allclose(30, chi_sq, rtol=1)
        np.testing.assert_allclose(30, min_chi_sq, rtol=1)

    def test_execute_fit_cost_function_least_squares(self):

        data, function, minimizer, cost_function, init_function_def = \
            self.setup_problem_success()
        initial_params = [500.0, 250.0]
        popt = execute_fit(function[0], data, initial_params,
                           minimizer, cost_function)
        expected_popt = np.array([2.4, 250.])

        np.testing.assert_allclose(expected_popt, popt, rtol=2)

    def test_execute_fit_cost_function_unweight_least_squares(self):

        data, function, minimizer, cost_function, init_function_def = \
            self.setup_problem_success()
        initial_params = [500.0, 250.0]
        cost_function = 'unweighted least squares'

        popt = execute_fit(function[0], data, initial_params,
                           minimizer, cost_function)
        expected_popt = np.array([4, 250.])

        np.testing.assert_allclose(expected_popt, popt, rtol=2)

    def test_parse_result_status_success(self):

        data, function, minimizer, cost_function, init_function_def = \
            self.setup_problem_success()
        popt = np.array([2.4, 250.])

        status, fitted_y, runtime = \
            parse_result(function[0], popt, 1, 15, data[0])

        self.assertEqual('success', status)
        self.assertEqual(14, runtime)
        np.testing.assert_allclose(np.array([2.4, 2.4, 2.4, 2.4]), fitted_y)

    def test_parse_result_status_fail(self):

        status, fitted_y, runtime = \
            parse_result(None, None, None, None, None)

        self.assertEqual('failed', status)
        self.assertEqual(None, fitted_y)
        np.testing.assert_equal(np.nan, runtime)

    def test_get_fittedy_get_fittedy(self):

        exec "def fitting_function(x,b1,b2): return b1*(1-np.exp(-b2*x))"
        popt = np.array([2.4, 250.])
        data_x = np.array([1, 3, 5, 7])

        fitted_y = get_fittedy(fitting_function, data_x, popt)

        np.testing.assert_allclose(np.array([2.4, 2.4, 2.4, 2.4]), fitted_y)


if __name__ == "__main__":
    unittest.main()
