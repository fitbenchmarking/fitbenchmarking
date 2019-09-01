from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
parent_dir = os.path.dirname(os.path.normpath(parent_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from fitting.scipy.prepare_data import prepare_data
from fitting.scipy.prepare_data import misc_preparations
from fitting.scipy.prepare_data import apply_x_data_range

from parsing.parse_nist_data import FittingProblem
from mock_problem_files.get_problem_files import get_file


class ScipyTests(unittest.TestCase):

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

        fname = get_file('NIST_Misra1a.dat')
        prob = FittingProblem(fname)
        prob.name = 'Misra1a'
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0, 250.0]],
                                ['b2', [0.0001, 0.0005]]]
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]

        return prob

    def get_expected_data(self):

        problem = self.NIST_problem()
        data_x = problem.data_x
        data_y = problem.data_y
        data_e = np.sqrt(abs(data_y))

        return  np.array([data_x, data_y, data_e])

    def test_prepareData_use_errors_true(self):

        problem = self.NIST_problem()
        use_errors = True

        data, cost_function = prepare_data(problem, use_errors)
        expected_data = self.get_expected_data()

        np.testing.assert_array_equal(expected_data, data)
        self.assertEqual("least squares", cost_function)

    def test_prepareData_use_errors_false(self):

        problem = self.NIST_problem()
        use_errors = False

        data, cost_function = prepare_data(problem, use_errors)
        data_x, data_y, _ = self.get_expected_data()
        expected_data = np.array([data_x, data_y])

        np.testing.assert_equal(expected_data, data)
        self.assertEqual("unweighted least squares", cost_function)

    def test_miscPreparations_no_errors_no_limits(self):

        problem = self.NIST_problem()

        problem = \
            misc_preparations(problem, problem.data_x, problem.data_y, problem.data_e)

        expected_data = self.get_expected_data()

        np.testing.assert_equal(expected_data[0], problem.data_x)
        np.testing.assert_equal(expected_data[1], problem.data_y)
        np.testing.assert_equal(expected_data[2], problem.data_e)

    def test_miscPreparations_uneq_length_constrained(self):

        problem = self.NIST_problem()
        problem.data_x = np.append(problem.data_x, 0)
        problem.start_x = 115
        problem.end_x = 540

        problem = \
            misc_preparations(problem, problem.data_x, problem.data_y, problem.data_e)
        expected_data = self.get_expected_data()
        expected = [[None] * 3] * 10
        expected[0] = np.array(expected_data[0])[2:11]
        expected[1] = np.array(expected_data[1])[2:11]

        np.testing.assert_equal(expected[0], problem.data_x)
        np.testing.assert_equal(expected[1], problem.data_y)

    def test_applyXRange_return_data(self):

        problem = self.NIST_problem()
        problem.start_x = 115
        problem.end_x = 540
        problem.data_e = np.sqrt(abs(problem.data_y))

        problem = \
            apply_x_data_range(problem)
        expected_data = self.get_expected_data()
        expected = [ [ None ] * 3 ] * 10
        expected[0] = np.array(expected_data[0])[2:11]
        expected[1] = np.array(expected_data[1])[2:11]
        expected[2] = np.array(expected_data[2])[2:11]

        np.testing.assert_equal(expected[0], problem.data_x)
        np.testing.assert_equal(expected[1], problem.data_y)
        np.testing.assert_equal(expected[2], problem.data_e)


if __name__ == "__main__":
    unittest.main()
