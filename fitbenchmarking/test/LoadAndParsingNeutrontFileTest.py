from __future__ import (absolute_import, division, print_function)

import unittest
import os

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
        ''' Helper function that returns the directory path ../Neutron_/ '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        bench_prob_dir = os.path.join(base_dir, 'benchmark_problems')
        neutron_problems_path = os.path.join(bench_prob_dir, 'Neutron_data')

        return neutron_problems_path

    def ENGINX193749Peak19File(self):
        neutron_problems_path = self.NeutronProblemDirPath()
        enginxPeak19_path = os.path.join(neutron_problems_path,
                                        'ENGINX193749_calibration_peak19.txt')

        return enginxPeak19_path


    def test_load_neutron_data_fitting_problem_file(self):

        enginxPeak19_path = self.ENGINX193749Peak19File()
        prob_actual = test_problem.FittingTestProblem()
        prob_actual.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
        prob_actual.equation = ("name=LinearBackground;"
                                "name=BackToBackExponential,"
                                "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        prob_actual.starting_values = None
        prob_actual.start_x = 23919.5789114
        prob_actual.end_x = 24189.3183142


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


    def test_get_neutron_data_problem_entries(self):
        enginxPeak19_path = self.ENGINX193749Peak19File()
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
        # QUESTION: HOW DO I TEST THIS?

        neutron_problems_path = self.NeutronProblemDirPath()
        neutron_fit_file = os.path.join(neutron_problems_path, 'data_files',
                                        'ENGINX193749_calibration_spec651.nxs')
        prob = test_problem.FittingTestProblem()

        get_fitting_neutron_data(neutron_fit_file, prob)


if __name__ == "__main__":
    unittest.main()
