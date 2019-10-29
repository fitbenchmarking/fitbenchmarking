from __future__ import (absolute_import, division, print_function)

import unittest
import numpy as np

from fitbenchmarking.parsing.fitbenchmark_data_functions import fitbenchmark_func_definitions
from fitbenchmarking.parsing.fitbenchmark_data_functions import get_all_fitbenchmark_func_names
from fitbenchmarking.parsing.fitbenchmark_data_functions import get_all_fitbenchmark_func_params
from fitbenchmarking.parsing.fitbenchmark_data_functions import get_fitbenchmark_func_names
from fitbenchmarking.parsing.fitbenchmark_data_functions import get_fitbenchmark_func_params
from fitbenchmarking.parsing.fitbenchmark_data_functions import get_fitbenchmark_initial_params_values
from fitbenchmarking.parsing.fitbenchmark_data_functions import get_fitbenchmark_params
from fitbenchmarking.mock_problem_files.get_problem_files import get_file


from fitbenchmarking.parsing.parse_fitbenchmark_data import FittingProblem


class ScipyTests(unittest.TestCase):

    def test_txtFuncDefinitions_create_function_definitions(self):

        functions_string = ("name=LinearBackground,A0=0,A1=0;"
                            "name=BackToBackExponential,"
                            "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")

        function_defs = fitbenchmark_func_definitions(functions_string)
        expected_params_array = np.array([0, 0, 597.076, 1, 0.05, 24027.5, 22.9096])

        np.testing.assert_equal(expected_params_array, function_defs[0][1])

    def test_FunctionDefinitions_Dat_return_function_definitions(self):

        fname = get_file('FB_ENGINX193749_calibration_peak19.txt')
        prob = FittingProblem(fname)
        prob.equation = ("name=LinearBackground,A0=0,A1=0;"
                         "name=BackToBackExponential,"
                         "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")

        function_defs = prob.get_function()
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

        params = get_fitbenchmark_params(param_set)
        expected_params = [0, 0]

        self.assertListEqual(expected_params, params)


if __name__ == "__main__":
    unittest.main()
