from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np
import mantid.simpleapi as msapi

import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
parent_dir = os.path.dirname(os.path.normpath(parent_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from fitting.mantid.main import benchmark
from fitting.mantid.main import fit
from fitting.mantid.main import chisq
from fitting.mantid.main import parse_result
from fitting.mantid.main import optimum
from fitting.mantid.main import get_ignore_invalid

from parsing.fitbm_problem import BaseFittingProblem


class MantidTests(unittest.TestCase):

    def misra1a_file(self):
        """
        Helper function that returns the path to
        /fitbenchmarking/benchmark_problems
        """

        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(os.path.normpath(test_dir))
        main_dir = os.path.dirname(os.path.normpath(parent_dir))
        root_dir = os.path.dirname(os.path.normpath(main_dir))
        bench_prob_dir = os.path.join(root_dir, 'benchmark_problems')
        fname = os.path.join(bench_prob_dir, 'NIST', 'low_difficulty',
                             'Misra1a.dat')

        return fname

    def NIST_problem(self):
        """
        Helper function.
        Sets up the problem object for the nist problem file Misra1a.dat
        """

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

        fname = self.misra1a_file()
        prob = BaseFittingProblem(fname)
        prob.name = 'Misra1a'
        prob.type = 'NIST'
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0, 250.0]],
                                ['b2', [0.0001, 0.0005]]]
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]

        return prob

    def setup_problem_Misra1a_success(self):
        """
        Helper function.
        Sets up the parameters needed to run fitting.mantid
        """

        prob = self.NIST_problem()
        wks = msapi.CreateWorkspace(DataX=prob.data_x,
                                    DataY=prob.data_y,
                                    DataE=np.sqrt(prob.data_y))
        function = ("name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                    "b1=500.0,b2=0.0001,")
        minimizer = 'Levenberg-Marquardt'
        cost_function = 'Least squares'

        return prob, wks, function, minimizer, cost_function

    def setup_problem_Misra1a_fail(self):
        """
        Helper function.
        Sets up the parameters needed to run fitting.mantid
        but fail due to incorrect minimizer name.
        """

        prob = self.NIST_problem()
        wks = msapi.CreateWorkspace(DataX=prob.data_x,
                                    DataY=prob.data_y,
                                    DataE=np.sqrt(prob.data_y))
        function = \
            "name=UserFunction,Formula=b1*(1-exp(-b2*x)),b1=500.0,b2=0.0001"
        minimizer = 'Levenberg-Merquardtss'
        cost_function = 'Least squared'

        return prob, wks, function, minimizer, cost_function

    def expected_results_problem_Misra1a_success(self):
        """
        Helper function.
        Sets up the expected results after running
        fitting.mantid with Misra1a.dat problem data.
        """

        fit_status = 'success'
        fin_function_def = \
            "name=UserFunction,Formula=b1*(1-exp( -b2*x)),b1=234.534,b2=0.00056228"

        return fit_status, fin_function_def

    def expected_results_problem_Misra1a_fail(self):
        """
        Helper function.
        Sets up the expected failure results after running
        fitting.mantid with Misra1a.dat problem data but
        fail parameters.
        """

        status = 'failed'
        fit_wks = None
        fin_function_def = None
        runtime = np.nan

        return status, fit_wks, fin_function_def, runtime

    def test_fit_return_success_for_NIST_Misra1a_prob_file(self):

        prob, wks, function, minimizer, cost_function = \
            self.setup_problem_Misra1a_success()

        status, fit_wks, fin_function_def, runtime = \
            fit(prob, wks, function, minimizer, cost_function)
        status_expected, fin_function_def_expected = \
            self.expected_results_problem_Misra1a_success()

        self.assertEqual(status_expected, status)
        self.assertEqual(fin_function_def_expected[:44], fin_function_def[:44])

    def test_fit_fails(self):

        prob, wks, function, minimizer, cost_function = \
            self.setup_problem_Misra1a_fail()

        status, fit_wks, fin_function_def, runtime = \
            fit(prob, wks, function, minimizer, cost_function)
        (status_expected, fit_wks_expected, fin_function_def_expected,
         runtime_expected) = self.expected_results_problem_Misra1a_fail()

        self.assertEqual(status_expected, status)
        self.assertEqual(fin_function_def_expected, fin_function_def)
        np.testing.assert_equal(runtime_expected, runtime)
        np.testing.assert_equal(fit_wks_expected, fit_wks)

    def test_chisq_status_failed(self):

        status = 'failed'

        chi_sq, min_chi_sq, best_fit = chisq(status, 1, 1, 1, 1)
        chi_sq_expected, min_chi_sq_expected, best_fit_expected = np.nan, 1, 1

        np.testing.assert_equal(chi_sq_expected, chi_sq)
        self.assertEqual(min_chi_sq_expected, min_chi_sq)
        self.assertEqual(best_fit_expected, best_fit)

    def test_chisq_status_succeeded_greater_chisq(self):

        status = 'success'
        wks = msapi.CreateWorkspace(DataX=np.array([1, 2, 3, 4, 5, 6]),
                                    DataY=np.array([1, 2, 3, 4, 5, 6]),
                                    DataE=np.sqrt(np.array([1, 2, 3, 4, 5, 6])),
                                    NSpec=3)
        minimizer = 'Levenberg-Marquardt'
        min_chi_sq = 1000000
        best_fit = None

        chi_sq, min_chi_sq, best_fit = \
            chisq(status, wks, min_chi_sq, best_fit, minimizer)
        chi_sq_expected = 61.0
        min_chi_sq_expected = chi_sq

        self.assertEqual(chi_sq_expected, chi_sq)
        self.assertEqual(min_chi_sq_expected, min_chi_sq)
        self.assertTrue(best_fit is not None)

    def test_parse_result_failed(self):

        fit_result = None
        t_start = 1
        t_end = 2

        status, fit_wks, fin_function_def, runtime = \
            parse_result(fit_result, t_start, t_end)
        status_expected = 'failed'
        fit_wks_expected = None
        fin_function_def_expected = None
        runtime_expected = np.nan

        self.assertEqual(status_expected, status)
        self.assertEqual(fit_wks_expected, fit_wks)
        self.assertEqual(fin_function_def_expected, fin_function_def)
        np.testing.assert_equal(runtime_expected, runtime)

    def test_ignoreInvalid_return_True(self):

        fname = self.misra1a_file()
        prob = BaseFittingProblem(fname)
        prob.name = 'notWish'
        cost_function = 'Least squares'

        ign_invalid = get_ignore_invalid(prob, cost_function)
        ign_invalid_expected = True

        self.assertEqual(ign_invalid_expected, ign_invalid)

    def test_ignoreInvalid_return_False_because_of_WISH17701(self):

        fname = self.misra1a_file()
        prob = BaseFittingProblem(fname)
        prob.name = 'WISH17701lol'
        cost_function = 'Least squares'

        ign_invalid = get_ignore_invalid(prob, cost_function)
        ign_invalid_expected = False

        self.assertEqual(ign_invalid_expected, ign_invalid)


if __name__ == "__main__":
    unittest.main()
