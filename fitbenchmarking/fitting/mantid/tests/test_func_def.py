"""
Mantid function definition testing
"""
from __future__ import (absolute_import, division, print_function)

import unittest
import numpy as np
import mantid.simpleapi as msapi

from fitbenchmarking.fitting.mantid.func_def import (
    function_definitions
)
from fitbenchmarking.fitting.mantid.func_def import (
    parse_function_definitions
)
from fitbenchmarking.parsing.parse_fitbenchmark_data import FittingProblem
from fitbenchmarking.mock_problem_files.get_problem_files import get_file
from fitbenchmarking.fitting.mantid.tests.test_main import nist_problem


class MantidTests(unittest.TestCase):
    """
    Implements Mantid Function Definition Tests
    """
    def test_function_definitions_return_nist_functions(self):
        """
        Test the NIST function definitions return the correct functions
        """
        prob = nist_problem()

        function_defs = function_definitions(prob)
        function_defs_expected = \
            ["name=fitFunction,b1=500.0,b2=0.0001",
             "name=fitFunction,b1=250.0,b2=0.0005"]

        self.assertListEqual(function_defs_expected, function_defs)

    def test_function_definitions_return_neutron_function(self):
        """
        Test the NIST function definitions return the correct function
        """
        prob = neutron_problem()

        function_defs = function_definitions(prob)
        function_defs = [str(function_defs[0])]
        function_defs_expected = \
            [("name=LinearBackground,A0=0,A1=0;name=BackToBackExponential,"
              "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")]

        self.assertListEqual(function_defs_expected, function_defs)

    def test_parse_nist_function_definitions_get_true_function(self):
        """
        Test the NIST function definitions parsing
        """
        prob = nist_problem()
        nb_start_vals = 2

        function_defs = parse_function_definitions(prob, nb_start_vals)
        function_defs_expected = \
            ["name=fitFunction,b1=500.0,b2=0.0001",
             "name=fitFunction,b1=250.0,b2=0.0005"]

        self.assertListEqual(function_defs_expected, function_defs)


def neutron_problem():
    """
    Sets up the problem object for the neutron problem file:
    ENGINX193749_calibration_peak19.txt
    """

    fname = get_file('FB_ENGINX193749_calibration_peak19.txt')
    prob = FittingProblem(fname)
    prob.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
    prob.equation = ("name=LinearBackground,A0=0,A1=0;"
                     "name=BackToBackExponential,"
                     "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
    prob.starting_values = None
    prob.start_x = 23919.5789114
    prob.end_x = 24189.3183142

    return prob


def create_wks_nist_problem_with_errors():
    """
    Helper function.
    Creates a mantid workspace using the data provided by the
    NIST problem Misra1a.
    """
    prob = nist_problem()
    data_e = np.sqrt(abs(prob.data_y))
    wks_exp = msapi.CreateWorkspace(DataX=prob.data_x, DataY=prob.data_y,
                                    DataE=data_e)
    return wks_exp


def create_wks_nist_problem_without_errors():
    """
    Helper function.
    Creates a mantid workspace using the data provided by the
    NIST problem Misra1a.
    """
    prob = nist_problem()
    wks_exp = msapi.CreateWorkspace(DataX=prob.data_x, DataY=prob.data_y)
    return wks_exp


if __name__ == "__main__":
    unittest.main()
