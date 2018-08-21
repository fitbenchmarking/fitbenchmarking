from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np
import mantid.simpleapi as msapi

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from fitting.fit_algorithms import mantid
from utils import test_problem


class FittingAlgorithmsTests(unittest.TestCase):

    def NIST_problem(self):
        """
        Helper function.
        Sets up the problem object for the nist problem file Misra1a.dat
        """

        data_pattern = np.array([ [10.07, 77.6],
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
                                  [81.78, 760.0] ])

        prob = test_problem.FittingTestProblem()
        prob.name = 'Misra1a'
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]

        return prob


    def setup_problem_Misra1a_success(self):
        """
        Helper function.
        Sets up the parameters needed to run fit_algorithms.mantid
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
        Sets up the parameters needed to run fit_algorithms.mantid
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
        fit_algorithms.mantid with Misra1a.dat problem data.
        """

        fit_status = 'success'
        fin_function_def = \
        "name=UserFunction,Formula=b1*(1-exp( -b2*x)),b1=234.534,b2=0.00056228"

        return fit_status, fin_function_def


    def expected_results_problem_Misra1a_fail(self):
        """
        Helper function.
        Sets up the expected failure results after running
        fit_algorithms.mantid with Misra1a.dat problem data but
        fail parameters.
        """

        status = 'failed'
        fit_wks = None
        fin_function_def = None
        runtime = np.nan

        return status, fit_wks, fin_function_def, runtime


    def test_fitAlgorithms_mantid_return_success_for_NIST_Misra1a_prob_file(self):

        prob, wks, function, minimizer, cost_function = \
        self.setup_problem_Misra1a_success()

        status, fit_wks, fin_function_def, runtime = \
        mantid(prob, wks, function, minimizer, cost_function)
        status_expected, fin_function_def_expected = \
        self.expected_results_problem_Misra1a_success()

        self.assertEqual(status_expected, status)
        self.assertEqual(fin_function_def_expected[:44], fin_function_def[:44])


    def test_runFit_mantidFit_fails(self):

        prob, wks, function, minimizer, cost_function = \
        self.setup_problem_Misra1a_fail()

        status, fit_wks, fin_function_def, runtime = \
        mantid(prob, wks, function, minimizer, cost_function)
        (status_expected, fit_wks_expected, fin_function_def_expected,
        runtime_expected) = self.expected_results_problem_Misra1a_fail()

        self.assertEqual(status_expected, status)
        self.assertEqual(fin_function_def_expected, fin_function_def)
        np.testing.assert_equal(runtime_expected, runtime)
        np.testing.assert_equal(fit_wks_expected, fit_wks)


if __name__ == "__main__":
    unittest.main()
