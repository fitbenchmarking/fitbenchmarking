from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from fitting.mantid_utils import parse_result
from fitting.mantid_utils import optimum
from fitting.mantid_utils import wks_cost_function
from fitting.mantid_utils import function_definitions
from fitting.mantid_utils import ignore_invalid
from fitting.mantid_utils import parse_nist_function_definitions
from fitting.mantid_utils import setup_errors


class MantidUtilsTests(unittest.TestCase):

    def setup_fit_result(self):

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


    def test_parseResult_return_successful_fit(self):

    def test_parseResult_return_failed_fit(self):

    def test_wksCostFunction_return_with_errors(self):

    def test_wksCostFunction_return_without_errors(self):

    def test_functionDefinitions_return_NIST_functions(self):

    def test_functionDefinitions_return_neutron_function(self):

    def test_ignoreInvalid_return_True(self):

    def test_ignoreInvalid_return_False(self):

    def test_ignoreInvalid_return_False_because_of_WISH17701(self):

    def test_parseNISTfunctionDefinitions_return_Misra1a_function_defs(self):

    def test_setupErrors_return_dataE_true_errors(self):

    def test_setupErrors_return_dataE_fake_errors(self):












if __name__ == "__main__":
    unittest.main()
