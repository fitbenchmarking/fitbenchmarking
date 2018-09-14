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

from fitting.mantid import fit
from fitting.mantid import parse_result
from fitting.mantid import optimum
from fitting.mantid import wks_cost_function
from fitting.mantid import function_definitions
from fitting.mantid import get_ignore_invalid
from fitting.mantid import parse_nist_function_definitions
from fitting.mantid import setup_errors
from utils import test_problem


class MantidTests(unittest.TestCase):

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
        prob.type = 'nist'
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0,250.0]],
                                ['b2', [0.0001,0.0005]]]
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]

        return prob


    def Neutron_problem(self):
        """
        Sets up the problem object for the neutron problem file:
        ENGINX193749_calibration_peak19.txt
        """

        prob = test_problem.FittingTestProblem()
        prob.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
        prob.type = 'neutron'
        prob.equation = ("name=LinearBackground,A0=0,A1=0;"
                         "name=BackToBackExponential,"
                         "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        prob.starting_values = None
        prob.start_x = 23919.5789114
        prob.end_x = 24189.3183142

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


    def create_wks_NIST_problem_with_errors(self):
        """
        Helper function.
        Creates a mantid workspace using the data provided by the
        NIST problem Misra1a.
        """

        prob = self.NIST_problem()
        data_e = np.sqrt(abs(prob.data_y))
        wks_exp = msapi.CreateWorkspace(DataX=prob.data_x, DataY=prob.data_y,
                                        DataE=data_e)
        return wks_exp


    def create_wks_NIST_problem_without_errors(self):
        """
        Helper function.
        Creates a mantid workspace using the data provided by the
        NIST problem Misra1a.
        """

        prob = self.NIST_problem()
        wks_exp = msapi.CreateWorkspace(DataX=prob.data_x, DataY=prob.data_y)
        return wks_exp


    def test_fitting_mantid_return_success_for_NIST_Misra1a_prob_file(self):

        prob, wks, function, minimizer, cost_function = \
        self.setup_problem_Misra1a_success()

        status, fit_wks, fin_function_def, runtime = \
        fit(prob, wks, function, minimizer, cost_function)
        status_expected, fin_function_def_expected = \
        self.expected_results_problem_Misra1a_success()

        self.assertEqual(status_expected, status)
        self.assertEqual(fin_function_def_expected[:44], fin_function_def[:44])


    def test_runFit_mantidFit_fails(self):

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


    def test_wksCostFunction_return_with_errors(self):

        prob = self.NIST_problem()
        use_errors = True

        wks, cost_function = wks_cost_function(prob, use_errors)
        wks_expected = self.create_wks_NIST_problem_with_errors()
        cost_function_expected = 'Least squares'

        self.assertEqual(cost_function_expected, cost_function)
        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertTrue(result)


    def test_wksCostFunction_return_without_errors(self):

        prob = self.NIST_problem()
        use_errors = False

        wks, cost_function = wks_cost_function(prob, use_errors)
        wks_expected = self.create_wks_NIST_problem_without_errors()
        cost_function_expected = 'Unweighted least squares'

        self.assertEqual(cost_function_expected, cost_function)
        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertTrue(result)


    def test_functionDefinitions_return_NIST_functions(self):

        prob = self.NIST_problem()

        function_defs = function_definitions(prob)
        function_defs_expected = \
        ["name=UserFunction,Formula=b1*(1-exp(-b2*x)),b1=500.0,b2=0.0001",
         "name=UserFunction,Formula=b1*(1-exp(-b2*x)),b1=250.0,b2=0.0005"]

        self.assertListEqual(function_defs_expected, function_defs)


    def test_functionDefinitions_return_neutron_function(self):

        prob = self.Neutron_problem()

        function_defs = function_definitions(prob)
        function_defs_expected = \
        [("name=LinearBackground,A0=0,A1=0;name=BackToBackExponential,"
          "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")]

        self.assertListEqual(function_defs_expected, function_defs)


    def test_ignoreInvalid_return_True(self):

        prob = test_problem.FittingTestProblem()
        prob.name = 'notWish'
        cost_function = 'Least squares'

        ign_invalid = get_ignore_invalid(prob, cost_function)
        ign_invalid_expected = True

        self.assertEqual(ign_invalid_expected, ign_invalid)


    def test_ignoreInvalid_return_False_because_of_WISH17701(self):

        prob = test_problem.FittingTestProblem()
        prob.name = 'WISH17701lol'
        cost_function = 'Least squares'

        ign_invalid = get_ignore_invalid(prob, cost_function)
        ign_invalid_expected = False

        self.assertEqual(ign_invalid_expected, ign_invalid)


if __name__ == "__main__":
    unittest.main()
