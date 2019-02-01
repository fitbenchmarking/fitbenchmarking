from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
parent_dir = os.path.dirname(os.path.normpath(parent_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from fitting.scipy.main import benchmark
from fitting.scipy.main import fit
from fitting.scipy.main import chisq
from fitting.scipy.main import parse_result
from fitting.scipy.main import get_fittedy


class ScipyTests(unittest.TestCase):

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

    def setup_problem_Misra1a_success(self):
        """
        Helper function.
        Sets up the parameters needed to run fitting.mantid
        """

        data = np.array[np.array([1,2,3]), np.array([1,2,3]), np.array([1,2,3])]
        function = 'b1*(1-exp(-b2*x))'
        minimizer = 'Levenberg-Marquardt'
        cost_function = 'Least squares'

        return data, function, minimizer, cost_function

    def test_fit_return_success_for_NIST_Misra1a_prob_file(self):

    	data, function, minimizer, cost_function, init_function_def = \
    	self.setup_problem_Misra1a_success()




if __name__ == "__main__":
    unittest.main()
