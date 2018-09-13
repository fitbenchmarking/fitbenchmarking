from __future__ import (absolute_import, division, print_function)

import unittest
import os

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from resproc.fitdetails_tbls import parse_nist_mantid_function_def
from resproc.fitdetails_tbls import parse_neutron_function_def
from resproc.fitdetails_tbls import fit_details_table_hdims


class FitDetailsTblsTests(unittest.TestCase):

    def test_parseNistFunctionDef_return_proper_parsed_string(self):

        function = ("name=UserFunction,Formula=b1*(1-exp(-b2*x)),"
                    "b1=500.0,b2=0.0001")

        function_name, function_parameters = parse_nist_function_def(function)
        function_name_expected = "b1*(1-exp(-b2*x))"
        function_parameters_expected = "b1=500.0, b2=0.0001"

        self.assertEqual(function_name_expected, function_name[0])
        self.assertEqual(function_parameters_expected, function_parameters[0])


    def test_parseNeutronFunctionDef_return_parsed_string_no_comma_found(self):

        function = "name=LinearBackground"
        func_names = []
        func_parameters = []

        function_names, function_parameters = \
        parse_neutron_function_def(function, func_names, func_parameters)
        func_names_expected = "LinearBackground"
        func_parameters_expected = "None"

        self.assertEqual(func_names_expected, func_names[0])
        self.assertEqual(func_parameters_expected, func_parameters[0])


    def test_parseNeutronFunctionDef_return_parsed_string_comma_found(self):

        function = ("name=BackToBackExponential,I=597.076,A=1,B=0.05,"
                    "X0=24027.5,S=22.9096")
        func_names = []
        func_parameters = []

        function_names, function_parameters = \
        parse_neutron_function_def(function, func_names, func_parameters)
        func_names_expected = "BackToBackExponential"
        func_parameters_expected = ("I=597.076, A=1, B=0.05, X0=24027.5, "
                                    "S=22.9096")

        self.assertEqual(func_names_expected, func_names[0])
        self.assertEqual(func_parameters_expected, func_parameters[0])


    def test_fitDetailsTableHdims_return_proper_table_dimensions(self):

        func_names = ["LinearBackground", "BackToBackExponential"]
        func_parameters = ["None",
                           "I=597.076, A=1, B=0.05, X0=24027.5,S=22.9096"]

        name_hdim, params_hdim = \
        fit_details_table_hdims(func_names, func_parameters)
        name_hdim_expected = 21
        params_hdim_expected = 44

        self.assertEqual(name_hdim_expected, name_hdim)
        self.assertEqual(params_hdim_expected, params_hdim)


if __name__ == "__main__":
    unittest.main()

