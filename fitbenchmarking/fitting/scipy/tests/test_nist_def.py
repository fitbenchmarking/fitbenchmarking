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

from fitting.scipy.nist_def import nist_func_definitions
from fitting.scipy.nist_def import get_nist_param_names_and_values
from fitting.scipy.nist_def import format_function_scipy

from utils import fitbm_problem

class ScipyTests(unittest.TestCase):

    def create_expected_function_definitions(self):
        function = "b1*(1-np.exp(-b2*x))"
        exec "def fitting_function(x,b1,b2): return " + function

        function_defs = [[fitting_function, [500.0, 0.0001], function],
                         [fitting_function, [250.0, 0.0005], function]]

        return function_defs

    def test_nistFuncDefinitions_return_function_definitions(self):

        function = "b1*(1-exp(-b2*x))"
        startvals = [['b1', [500.0,250.0]], ['b2', [0.0001,0.0005]]]

        function_defs = nist_func_definitions(function, startvals)
        expected_function_defs = self.create_expected_function_definitions()

        self.assertListEqual(expected_function_defs[0][1], function_defs[0][1])
        self.assertListEqual(expected_function_defs[1][1], function_defs[1][1])
        self.assertEqual(expected_function_defs[0][2], function_defs[0][2])
        self.assertEqual(expected_function_defs[1][2], function_defs[1][2])
        np.testing.assert_equal(expected_function_defs[0][0](1,2,3),
                                function_defs[0][0](1,2,3))
        np.testing.assert_equal(expected_function_defs[1][0](1,2,3),
                                function_defs[1][0](1,2,3))

    def test_getNistParamNamesAndValues_return_correct_output(self):

        startvals = [['b1', [500.0,250.0]], ['b2', [0.0001,0.0005]]]

        param_names, all_values = get_nist_param_names_and_values(startvals)
        expected_param_names = "b1, b2"
        expected_all_values = [[500.0, 0.0001], [250.0, 0.0005]]

        self.assertEqual(expected_param_names, param_names)
        np.testing.assert_equal(expected_all_values, all_values)

    def test_formatFunctionScipy_return_formatted_function(self):

        function = "b1*(1-exp(-b2*x))"

        function = format_function_scipy(function)
        expected_function = "b1*(1-np.exp(-b2*x))"

        self.assertEqual(expected_function, function)


if __name__ == "__main__":
    unittest.main()
