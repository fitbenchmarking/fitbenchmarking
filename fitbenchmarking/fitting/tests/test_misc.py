from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

from fitbenchmarking.utils import fitbm_result
from fitbenchmarking.parsing.fitting_problem import FittingProblem

from fitbenchmarking.fitting.misc import compute_chisq
from fitbenchmarking.fitting.misc import create_result_entry


class FitMiscTests(unittest.TestCase):

    def setup_misra1a_expected_data_points(self):

        data_pattern = np.array([[10.07, 77.6],
                                 [14.73, 114.9],
                                 [17.94, 141.1],
                                 [23.93, 190.8],
                                 [29.61, 239.9],
                                 [35.18, 289.0],
                                 [40.02, 332.8],
                                 [44.82, 378.4],
                                 [50.76, 434.8],
                                 [55.05, 477.3],
                                 [61.01, 536.8],
                                 [66.40, 593.1],
                                 [75.47, 689.1],
                                 [81.78, 760.0]])

        return data_pattern

    def setup_nist_expected_problem(self):

        prob = FittingProblem()

        prob.name = 'Misra1a'
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0, 250.0]],
                                ['b2', [0.0001, 0.0005]]]
        data_pattern = self.setup_misra1a_expected_data_points()
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]
        prob.ref_residual_sum_sq = 1.2455138894e-01

        return prob

    def create_expected_result(self):

        result = fitbm_result.FittingResult()
        problem = self.setup_nist_expected_problem()
        result.problem = problem
        result.fit_status = 'success'
        result.chi_sq = 1
        result.runtime = 1
        result.minimizer = 'Test'
        result.ini_function_def = 'ini_def_test'
        result.fin_function_def = 'fin_def_test'

        return result

    def test_compute_chisq_no_errors(self):

        actual = np.array([1, 2, 3])
        calculated = np.array([2, 4, 6])
        errors = None

        chi_sq = compute_chisq(actual, calculated, errors)
        chi_sq_expected = 14

        self.assertEqual(chi_sq_expected, chi_sq)

    def test_compute_chisq_errors(self):

        actual = np.array([1, 2, 3])
        calculated = np.array([2, 4, 6])
        errors = np.array([5, 0.1, 0.5])

        chi_sq = compute_chisq(actual, calculated, errors)
        chi_sq_expected = 436.04

        self.assertEqual(chi_sq_expected, chi_sq)

    def test_createResultEntry(self):

        problem = self.setup_nist_expected_problem()
        status = 'success'
        chi_sq = 1
        runtime = 1
        minimizer = 'Test'
        ini_function_def = 'ini_def_test'
        fin_function_def = 'fin_def_test'

        result = \
            create_result_entry(problem, status, chi_sq, runtime, minimizer,
                                ini_function_def, fin_function_def)
        result_expected = self.create_expected_result()

        self.assertEqual(result_expected.fit_status, result.fit_status)
        self.assertEqual(result_expected.chi_sq, result.chi_sq)
        self.assertEqual(result_expected.runtime, result.runtime)
        self.assertEqual(result_expected.minimizer, result.minimizer)
        self.assertEqual(result_expected.ini_function_def,
                         result.ini_function_def)
        self.assertEqual(result_expected.fin_function_def,
                         result.fin_function_def)


if __name__ == "__main__":
    unittest.main()
