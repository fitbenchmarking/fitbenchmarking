from __future__ import (absolute_import, division, print_function)

import unittest
import os
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

    def NeutronProblemDirPath(self):
        ''' Helper function that returns the directory path ../Neutron_data/ '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        bench_prob_dir = os.path.join(base_dir, 'benchmark_problems')
        neutron_problems_path = os.path.join(bench_prob_dir, 'Neutron_data')

        return neutron_problems_path


    def ENGINX193749Peak19File(self):
        ''' Helper function that returns the path to the problem file
            'ENGINX193749_calibration_peak19.txt' '''

        neutron_problems_path = self.NeutronProblemDirPath()
        enginxPeak19_path = os.path.join(neutron_problems_path,
                                         'ENGINX193749_calibration_peak19.txt')

        return enginxPeak19_path


    def test_loadNeutronDataFittingProblemFile_return_ENGINXpeak19_problem_definition_object(self):

        enginxPeak19_path = self.ENGINX193749Peak19File()

        prob = load_neutron_data_fitting_problem_file(enginxPeak19_path)
        prob_expected = test_problem.FittingTestProblem()
        prob_expected.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
        prob_expected.equation = ("name=LinearBackground;"
                                  "name=BackToBackExponential,"
                                  "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        prob_expected.starting_values = None
        prob_expected.start_x = 23919.5789114
        prob_expected.end_x = 24189.3183142

        self.assertEqual(prob_expected.name, prob.name)
        self.assertEqual(prob_expected.equation, prob.equation)
        self.assertEqual(prob_expected.starting_values, prob.starting_values)
        self.assertEqual(prob_expected.start_x, prob.start_x)
        self.assertEqual(prob_expected.end_x, prob.end_x)


    def test_getNeutronDataProblemEntries_return_ENGINXpeak19_problem_entries(self):

        enginxPeak19_path = self.ENGINX193749Peak19File()

        with open(enginxPeak19_path) as probf:
            entries = get_neutron_data_problem_entries(probf)
        entries_expected = {'name' : ("ENGINX 193749 calibration, "
                                    "spectrum 651, peak 19"),
                            'input_file' : 'ENGINX193749_calibration_spec651.nxs',
                            'function' : ("name=LinearBackground;"
                                          "name=BackToBackExponential,"
                                          "I=597.076,A=1,B=0.05,X0=24027.5,"
                                          "S=22.9096"),
                            'fit_parameters' : {'StartX': 23919.5789114,
                                                'EndX': 24189.3183142},
                            'description' : ''}

        self.assertEqual(entries_expected['name'], entries['name'])
        self.assertEqual(entries_expected['input_file'], entries['input_file'])
        self.assertEqual(entries_expected['function'], entries['function'])
        self.assertEqual(entries_expected['fit_parameters'], entries['fit_parameters'])
        self.assertEqual(entries_expected['description'], entries['description'])


    def MockProblemData(self):
        ''' Helper function that provides the data in NeutronMockData.nxs
            stored in a test_problem object '''

        prob = test_problem.FittingTestProblem()

        prob.data_pattern_in = np.array([1, 2, 3, 4, 5, 6])
        prob.data_pattern_out = np.array([7, 8, 9, 10, 11, 12])
        prob.data_pattern_obs_errors = np.sqrt(prob.data_pattern_out)

        return prob


    def test_getFittingNeutronData_return_MockProblemData(self):

        current_dir = os.path.dirname(os.path.realpath(__file__))
        neutron_mock_data = os.path.join(current_dir, 'mock_problems', 'data_files',
                                         'NeutronMockData.nxs')

        prob = test_problem.FittingTestProblem()
        get_fitting_neutron_data(neutron_mock_data, prob)
        prob_expected = self.MockProblemData()

        np.testing.assert_array_equal(prob_expected.data_pattern_in, prob.data_pattern_in)
        np.testing.assert_array_equal(prob_expected.data_pattern_out, prob.data_pattern_out)
        np.testing.assert_array_equal(prob_expected.data_pattern_obs_errors, prob.data_pattern_obs_errors)


if __name__ == "__main__":
    unittest.main()
