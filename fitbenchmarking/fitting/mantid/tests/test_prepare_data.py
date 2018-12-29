from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np
import mantid.simpleapi as msapi

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
parent_dir = os.path.dirname(os.path.normpath(parent_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from fitting.mantid.prepare_data import wks_cost_function
from fitting.mantid.prepare_data import setup_errors
from fitting.mantid.prepare_data import convert_back

from utils import fitbm_problem


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

        prob = fitbm_problem.FittingProblem()
        prob.name = 'Misra1a'
        prob.type = 'nist'
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0,250.0]],
                                ['b2', [0.0001,0.0005]]]
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]

        return prob

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

    def test_setupErrors_no_errors(self):

        prob = self.NIST_problem()

        errors = setup_errors(prob)
        errors_expected = np.sqrt(abs(prob.data_y))

        np.testing.assert_allclose(errors_expected, errors)

    def test_setupErrors_errors(self):

        prob = self.NIST_problem()
        prob.data_e = [1,2,3]

        errors = setup_errors(prob)
        errors_expected = [1,2,3]

        self.assertListEqual(errors_expected, errors)

if __name__ == "__main__":
    unittest.main()
