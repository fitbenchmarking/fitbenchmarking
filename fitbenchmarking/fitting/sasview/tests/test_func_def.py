from __future__ import (absolute_import, division, print_function)

import unittest
import numpy as np

from fitbenchmarking.fitting.sasview.func_def import function_definitions
from fitbenchmarking.fitting.sasview.func_def import get_fin_function_def
from fitbenchmarking.fitting.sasview.func_def import get_init_function_def
from fitbenchmarking.parsing.parse_nist_data import (
    FittingProblem as NISTFittingProblem
)
from fitbenchmarking.parsing.parse_fitbenchmark_data import (
    FittingProblem as FBFittingProblem
)

from fitbenchmarking.mock_problem_files.get_problem_files import get_file


class SasViewTests(unittest.TestCase):
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
        prob = NISTFittingProblem(fname)
        prob.name = 'Misra1a'
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0, 250.0]],
                                ['b2', [0.0001, 0.0005]]]
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]

        return prob

    def Neutron_problem(self):
        """
        Sets up the problem object for the neutron problem file:
        ENGINX193749_calibration_peak19.txt
        """

        fname = get_file('FB_ENGINX193749_calibration_peak19.txt')
        prob = FBFittingProblem(fname)
        prob.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
        prob.equation = ("name=LinearBackground,A0=0,A1=0;"
                         "name=BackToBackExponential,"
                         "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        prob.starting_values = None
        prob.start_x = 23919.5789114
        prob.end_x = 24189.3183142

        return prob

    def test_functionDefinitions_return_NIST_functions(self):

        prob = self.NIST_problem()

        function_defs = function_definitions(prob)
        function_defs_expected = prob.get_function()

        function = function_defs[0][0]
        function_expected = function_defs_expected[0][0]

        np.testing.assert_array_equal(
            function(prob.data_x, 500.0, 250.0),
            function_expected(prob.data_x, 500.0, 250.0))
        np.testing.assert_array_equal(
            function(prob.data_x, 0.0001, 0.0005),
            function_expected(prob.data_x, 0.0001, 0.0005))

        self.assertListEqual(function_defs_expected[0][1:],
                             function_defs[0][1:])

    def test_functionDefinitions_return_neutron_functions(self):

        prob = self.Neutron_problem()

        function_defs = function_definitions(prob)
        function_defs_expected = prob.get_bumps_function()

        function = function_defs[0][0]
        function_expected = function_defs_expected[0][0]

        y_values = function(prob.data_x[:10], 0.0, 0.0, 597.076, 1.0, 0.05,
                            24027.5, 22.9096)
        y_values_expected = function_expected(prob.data_x[:10], 0.0, 0.0,
                                              597.076, 1.0, 0.05, 24027.5,
                                              22.9096)

        np.testing.assert_array_equal(y_values_expected, y_values)
        np.testing.assert_array_equal(function_defs_expected[0][1],
                                      function_defs[0][1])

    def test_get_init_function_def_return_NIST_init_func_def(self):

        prob = self.NIST_problem()

        init_func_def = get_init_function_def((prob.get_function())[0], prob)

        init_func_def_expected = "b1*(1-np.exp(-b2*x)) | b1= 500.0, b2= 0.0001"

        self.assertEqual(init_func_def_expected, init_func_def)

    def test_get_init_function_def_return_neutron_init_func_def(self):

        prob = self.Neutron_problem()

        init_func_def = get_init_function_def((prob.get_function())[0], prob)

        init_func_def_expected  = "name=LinearBackground,A0=0.0,A1=0.0;name=BackToBackExponential,I=597.076,A=1.0,B=0.05,X0=24027.5,S=22.9096"

        self.assertEqual(init_func_def_expected, init_func_def)

    def test_get_fin_function_def_return_NIST_fin_func_def(self):

        prob = self.NIST_problem()

        init_func_def = "b1*(1-np.exp(-b2*x)) | b1= 500.0, b2= 0.0001"

        final_param_values = np.array([2.4, 250.])

        fin_func_def = get_fin_function_def(final_param_values, prob, init_func_def)

        fin_func_def_expected = "b1*(1-np.exp(-b2*x))  |  b1= 2.4, b2= 250.0"

        self.assertEqual(fin_func_def_expected, fin_func_def)

    def test_get_fin_function_def_return_neutron_fin_func_def(self):

        prob = self.Neutron_problem()

        init_func_def = "name=LinearBackground,A0=0.0,A1=0.0;name=BackToBackExponential,I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096"

        final_param_values = np.array([0.0,0.0,-2.28680098e+01, 9.80089245e-04, 7.10042119e+02, 3.58802084e+00,
                        3.21533386e-02, 2.40053562e+04, 1.65148875e+01])

        fin_func_def = get_fin_function_def(final_param_values, prob, init_func_def)

        fin_func_def_expected = "name=LinearBackground,A0=0.0,A1=0.0;name=BackToBackExponential,I=-22.868,A=1,B=0.001,X0=710.042,S=3.588"

        self.assertEqual(fin_func_def_expected, fin_func_def)


if __name__ == "__main__":
  unittest.main()
