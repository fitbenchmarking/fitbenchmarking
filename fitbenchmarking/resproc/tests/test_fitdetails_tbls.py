from __future__ import (absolute_import, division, print_function)

import unittest
import os

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from resproc.fitdetails_tbls import create
from resproc.fitdetails_tbls import generate_names_and_params
from resproc.fitdetails_tbls import parse_dat_mantid_function_def
from resproc.fitdetails_tbls import parse_txt_function_def
from resproc.fitdetails_tbls import fit_details_table_hdims
from resproc.fitdetails_tbls import generate_fit_det_header
from resproc.fitdetails_tbls import generate_fit_det_body


class FitDetailsTblsTests(unittest.TestCase):

    def test_create_produces_correct_tbl(self):

        functions_str = ("name=UserFunction,Formula=b1*(1-exp(-b2*x)),"
                         "b1=500.0,b2=0.0001")

        tbl = create(functions_str)
        tbl_expected = '+-------------------+---------------------+\n' + \
                       '| Form              | Parameters          |\n' + \
                       '+===================+=====================+\n' + \
                       '| b1*(1-exp(-b2*x)) | b1=500.0, b2=0.0001 |\n' + \
                       '+-------------------+---------------------+\n\n'
        self.assertEqual(tbl_expected, tbl)

    def test_generateNamesAndParams_for_nist_case(self):

        function = ("name=UserFunction,Formula=b1*(1-exp(-b2*x)),"
                    "b1=500.0,b2=0.0001")
        names, params = generate_names_and_params(function)
        function_name_expected = "b1*(1-exp(-b2*x))"
        function_parameters_expected = "b1=500.0, b2=0.0001"

        self.assertEqual(function_name_expected, names[0])
        self.assertEqual(function_parameters_expected, params[0])

    def test_generateNamesAndParams_for_neutron_case(self):

        function = ("name=BackToBackExponential,I=597.076,A=1,B=0.05,"
                    "X0=24027.5,S=22.9096")

        names, params = generate_names_and_params(function)
        func_names_expected = "BackToBackExponential"
        func_parameters_expected = "I=597.076, A=1, B=0.05, X0=24027.5, S=22.9096"

        self.assertEqual(func_names_expected, names[0])
        self.assertEqual(func_parameters_expected, params[0])

    def test_generateNamesAndParams_raise_error(self):

        self.assertRaises(TypeError, generate_names_and_params, 'test12')

    def test_parseNistFunctionDef_return_proper_parsed_string(self):

        function = ("name=UserFunction,Formula=b1*(1-exp(-b2*x)),"
                    "b1=500.0,b2=0.0001")

        function_name, function_parameters = \
            parse_dat_mantid_function_def(function)
        function_name_expected = "b1*(1-exp(-b2*x))"
        function_parameters_expected = "b1=500.0, b2=0.0001"

        self.assertEqual(function_name_expected, function_name[0])
        self.assertEqual(function_parameters_expected, function_parameters[0])

    def test_parseNeutronFunctionDef_return_parsed_string_no_comma_found(self):

        function = "name=LinearBackground"
        func_names = []
        func_parameters = []

        function_names, function_parameters = \
            parse_txt_function_def(function, func_names, func_parameters)
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
            parse_txt_function_def(function, func_names, func_parameters)
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

    def test_generateFitDetHeader_return_correct_header(self):

        name_dim = 15
        params_dim = 15

        header = generate_fit_det_header(name_dim, params_dim)
        header_expected = '+-----------------+-----------------+\n' + \
                          '| Form            | Parameters      |\n' + \
                          '+=================+=================+\n'
        self.assertEqual(header_expected, header)

    def test_generateFitDetBody(self):

        func_names = ["LinearBackground", "BackToBackExponential"]
        func_params = ["None",
                       "I=597.076, A=1, B=0.05, X0=24027.5,S=22.9096"]
        name_dim = 21
        params_dim = 44

        body = \
            generate_fit_det_body(func_names, func_params, name_dim, params_dim)
        body_expected = '| LinearBackground      |' + \
                        ' None                                         |\n' + \
                        '+-----------------------+' + \
                        '----------------------------------------------+\n' + \
                        '| BackToBackExponential | I=597.076, A=1, B=0.05,' + \
                        ' X0=24027.5,S=22.9096 |\n' + \
                        '+-----------------------+' + \
                        '----------------------------------------------+\n'

        self.assertEqual(body_expected, body)


if __name__ == "__main__":
    unittest.main()
