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

from fitting.scipy.func_def import function_definitions
from fitting.scipy.fitbenchmark_data_functions import fitbenchmark_func_definitions
from fitting.scipy.fitbenchmark_data_functions import get_all_fitbenchmark_func_names
from fitting.scipy.fitbenchmark_data_functions import get_all_fitbenchmark_func_params
from fitting.scipy.fitbenchmark_data_functions import get_fitbenchmark_func_names
from fitting.scipy.fitbenchmark_data_functions import get_fitbenchmark_func_params
from fitting.scipy.fitbenchmark_data_functions import get_fitbenchmark_initial_params_values
from fitting.scipy.fitbenchmark_data_functions import make_fitbenchmark_fit_function
from fitting.scipy.fitbenchmark_data_functions import get_fitbenchmark_params
from fitting.scipy.fitbenchmark_data_functions import get_fitbenchmark_ties

from utils import fitbm_problem


class ScipyTests(unittest.TestCase):

    def Neutron_problem(self):
        """
        Sets up the problem object for the neutron problem file:
        ENGINX193749_calibration_peak19.txt
        """

        prob = fitbm_problem.FittingProblem()
        prob.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
        prob.type = 'FitBenchmark'
        prob.equation = ("name=LinearBackground,A0=0,A1=0;"
                         "name=BackToBackExponential,"
                         "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        prob.starting_values = None
        prob.start_x = 23919.5789114
        prob.end_x = 24189.3183142

        return prob

    def test_txtFuncDefinitions_create_function_definitions(self):

        functions_string = ("name=LinearBackground,A0=0,A1=0;"
                            "name=BackToBackExponential,"
                            "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")

        function_defs = fitbenchmark_func_definitions(functions_string)
        expected_params_array = np.array([0, 0, 597.076, 1, 0.05, 24027.5, 22.9096])

        np.testing.assert_equal(expected_params_array, function_defs[0][1])

    def test_FunctionDefinitions_Dat_return_function_definitions(self):

        prob = fitbm_problem.FittingProblem()
        prob.equation = ("name=LinearBackground,A0=0,A1=0;"
                         "name=BackToBackExponential,"
                         "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        prob.type = 'FitBenchmark'

        function_defs = function_definitions(prob)
        expected_params_array = np.array([0, 0, 597.076, 1, 0.05, 24027.5, 22.9096])

        np.testing.assert_equal(expected_params_array, function_defs[0][1])

    def test_getAllNuetronFuncNames_return_all_function_names(self):

        functions_string = ("name=LinearBackground,A0=0,A1=0;"
                            "name=BackToBackExponential,"
                            "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")

        function_names = get_all_fitbenchmark_func_names(functions_string)
        expected_function_names = ["LinearBackground", "BackToBackExponential"]

        self.assertListEqual(expected_function_names, function_names)

    def test_getAllNeutronFuncParams_return_correct_params(self):

        functions_string = ("name=LinearBackground,A0=0,A1=0;"
                            "name=BackToBackExponential,"
                            "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")

        function_params = get_all_fitbenchmark_func_params(functions_string)
        expected_function_params = ['A0=0, A1=0',
                                    ('I=597.076, A=1, B=0.05, '
                                     'X0=24027.5, S=22.9096')]

        self.assertListEqual(expected_function_params, function_params)

    def test_getNeutronFuncNames_string_has_comma(self):

        function_names = []
        function = "name=LinearBackground,A0=0,A1=0"

        function_names = get_fitbenchmark_func_names(function, function_names)
        expected_function_names = ["LinearBackground"]

        self.assertListEqual(expected_function_names, function_names)

    def test_getNeutronFuncNames_string_does_not_have_comma(self):

        function_names = []
        function = "name=BackToBackExponential"

        function_names = get_fitbenchmark_func_names(function, function_names)
        expected_function_names = ["BackToBackExponential"]

        self.assertListEqual(expected_function_names, function_names)

    def test_getNeutronFuncParams_comma_found(self):

        function = "name=LinearBackground,A0=0,A1=0"
        function_params = []

        function_params = get_fitbenchmark_func_params(function, function_params)
        expected_function_params = ['A0=0, A1=0']

        self.assertListEqual(expected_function_params, function_params)

    def test_getNeutronFuncParams_comma_not_found(self):

        function = ("name=BackToBackExponential")
        function_params = []

        function_params = get_fitbenchmark_func_params(function, function_params)
        expected_function_params = ['']

        self.assertListEqual(expected_function_params, function_params)

    def test_getNeutronInitialParamsValues_return_params_values(self):

        function_params = ['A0=0, A1=0']

        params, ties = get_fitbenchmark_initial_params_values(function_params)
        expected_params, expected_ties = np.array([0, 0]), [[]]

        np.testing.assert_equal(expected_params, params)
        self.assertEqual(expected_ties, ties)

    def test_getNeutronParams_return_params(self):

        param_set = 'A0=0, A1=0'
        params = []

        params = get_fitbenchmark_params(param_set, params)
        expected_params = [0, 0]

        self.assertListEqual(expected_params, params)


if __name__ == "__main__":
    unittest.main()
