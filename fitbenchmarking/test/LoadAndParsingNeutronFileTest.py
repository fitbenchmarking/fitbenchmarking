from __future__ import (absolute_import, division, print_function)

import unittest
import os
import mantid.simpleapi as msapi
import numpy as np

# DELETE RELATIVE PATH WHEN GIT TESTS ARE ENABLED
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from input_parsing import load_neutron_data_fitting_problem_file
from input_parsing import get_neutron_data_problem_entries
from input_parsing import get_fitting_neutron_data
import test_problem

class LoadAndParseNeutronFiles(unittest.TestCase):

    def MockProblemsDir(self):
        ''' Helper function that returns the path ../test/mock_problems/ '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        mock_problems_dir = os.path.join(current_dir, 'mock_problems')

        return mock_problems_dir


    def ENGINX193749Peak19DefinitionFile(self):
        ''' Helper function that returns the path ../test/mock_problems/ '''

        mock_problems_dir = self.MockProblemsDir()
        enginxPeak19_path = os.path.join(mock_problems_dir,
                                        'ENGINX193749_calibration_peak19.txt')

        return enginxPeak19_path


    def test_load_neutron_data_fitting_problem_file(self):

        enginxPeak19_path = self.ENGINX193749Peak19DefinitionFile()

        # These are true entries:
        prob_actual = test_problem.FittingTestProblem()
        prob_actual.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
        prob_actual.equation = ("name=LinearBackground;"
                                "name=BackToBackExponential,"
                                "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        prob_actual.starting_values = None
        prob_actual.start_x = 23919.5789114
        prob_actual.end_x = 24189.3183142

        # These are mock entries, to avoid using Load:
        prob_actual.data_pattern_in = np.arange(10)
        prob_actual.data_pattern_out = 100*np.arange(9)
        prob_actual.data_pattern_obs_errors = np.sqrt(prob_actual.data_pattern_out)
        prob_actual.ref_residual_sum_sq = 0

        prob = load_neutron_data_fitting_problem_file(enginxPeak19_path)

        self.assertEqual(prob_actual.name, prob.name,
                         msg="Test failed at comparing name")
        self.assertEqual(prob_actual.equation, prob.equation,
                         msg="Test failed at comparing equation")
        self.assertEqual(prob_actual.starting_values, prob.starting_values,
                         msg="Test failed at comparing starting_values")
        self.assertEqual(prob_actual.start_x, prob.start_x,
                         msg="Test failed at comparing start_x")
        self.assertEqual(prob_actual.end_x, prob.end_x,
                         msg="Test failed at comparing end_x")

        test_in = np.testing.assert_array_equal(prob_actual.data_pattern_in,
                                                prob.data_pattern_in)
        self.assertTrue(test_in is None, msg="Failed at comparing data_in")

        test_out = np.testing.assert_array_equal(prob_actual.data_pattern_out,
                                                 prob.data_pattern_out)
        self.assertTrue(test_out is None, msg="Failed at comparing data_out")

        test_obs_errors = np.testing.assert_array_equal(prob_actual.data_pattern_obs_errors,
                                                        prob.data_pattern_obs_errors)
        self.assertTrue(test_obs_errors is None, msg="Failed at comparing obs_errors")


    def test_get_neutron_data_problem_entries(self):

        enginxPeak19_path = self.ENGINX193749Peak19DefinitionFile()
        entries_actual = {'name' : ("ENGINX 193749 calibration, "
                                    "spectrum 651, peak 19"),
                          'input_file' : 'ENGINX193749_calibration_spec651.nxs',
                          'function' : ("name=LinearBackground;"
                                        "name=BackToBackExponential,"
                                        "I=597.076,A=1,B=0.05,X0=24027.5,"
                                        "S=22.9096"),
                          'fit_parameters' : {'StartX': 23919.5789114,
                                              'EndX': 24189.3183142},
                          'description' : ''}

        with open(enginxPeak19_path) as probf:
            entries = get_neutron_data_problem_entries(probf)

        self.assertEqual(entries_actual['name'], entries['name'],
                         msg="Test failed at comparing name")
        self.assertEqual(entries_actual['input_file'], entries['input_file'],
                         msg="Test failed at comparing input_file")
        self.assertEqual(entries_actual['function'], entries['function'],
                         msg="Test failed at comparing function")
        self.assertEqual(entries_actual['fit_parameters'], entries['fit_parameters'],
                         msg="Test failed at comparing fit_parameters")
        self.assertEqual(entries_actual['description'], entries['description'],
                         msg="Test failed at comparing description")


    def test_get_fitting_neutron_data(self):

        # The ENGINX data file loaded mentioned here is a mock file
        mock_problems_dir = self.MockProblemsDir()
        neutron_data_fit_file = os.path.join(mock_problems_dir, 'data_files',
                                             'ENGINX193749_calibration_spec651.nxs')

        prob_actual = test_problem.FittingTestProblem()
        prob_actual.data_pattern_in = np.arange(10)
        prob_actual.data_pattern_out = 100*np.arange(9)
        prob_actual.data_pattern_obs_errors = np.sqrt(prob_actual.data_pattern_out)
        prob_actual.ref_residual_sum_sq = 0

        prob = test_problem.FittingTestProblem()
        get_fitting_neutron_data(neutron_data_fit_file, prob)

        test_in = np.testing.assert_array_equal(prob_actual.data_pattern_in,
                                                prob.data_pattern_in)
        self.assertTrue(test_in is None, msg="Failed at comparing data_in")

        test_out = np.testing.assert_array_equal(prob_actual.data_pattern_out,
                                                 prob.data_pattern_out)
        self.assertTrue(test_out is None, msg="Failed at comparing data_out")

        test_obs_errors = np.testing.assert_array_equal(prob_actual.data_pattern_obs_errors,
                                                        prob.data_pattern_obs_errors)
        self.assertTrue(test_obs_errors is None, msg="Failed at comparing obs_errors")


if __name__ == "__main__":
    unittest.main()
