from __future__ import (absolute_import, division, print_function)

import unittest
import os

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from parsing.parse_neutron import get_data_file
from parsing.parse_neutron import get_neutron_data_problem_entries

from utils import test_problem


class ParseNeutronTests(unittest.TestCase):

    def neutron_peak_19_file(self):
        """
        Helper function that returns the path to
        /fitbenchmarking/benchmark_problems
        """

        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(os.path.normpath(test_dir))
        main_dir = os.path.dirname(os.path.normpath(parent_dir))
        root_dir = os.path.dirname(os.path.normpath(main_dir))
        bench_prob_dir = os.path.join(root_dir, 'benchmark_problems')
        fname = os.path.join(bench_prob_dir, 'Neutron_data',
                             'ENGINX193749_calibration_peak19.txt')

        return fname

    def get_bench_prob_dir(self):

        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(os.path.normpath(test_dir))
        main_dir = os.path.dirname(os.path.normpath(parent_dir))
        root_dir = os.path.dirname(os.path.normpath(main_dir))
        bench_prob_dir = os.path.join(root_dir, 'benchmark_problems')

        return bench_prob_dir


    def expected_neutron_problem_entries(self):

        entries = {}
        entries['name'] = "ENGINX 193749 calibration, spectrum 651, peak 19"
        entries['input_file'] = "ENGINX193749_calibration_spec651.nxs"
        entries['function'] = ("name=LinearBackground,A0=0,A1=0;"
                               "name=BackToBackExponential,"
                               "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        entries['fit_parameters'] = {'StartX': 23919.5789114,
                                     'EndX': 24189.3183142}
        entries['description'] = ''

        return entries


    def test_getDataFilesDir_return_data_files_path(self):

        fname = self.neutron_peak_19_file()
        input_file = 'ENGINX193749_calibration_spec651'
        bench_prob_dir = self.get_bench_prob_dir()

        data_file = get_data_file(fname, input_file)
        data_file_expected = os.path.join(bench_prob_dir, 'Neutron_data',
                                          'data_files', input_file)

        self.assertEqual(data_file_expected, data_file)


    def test_getNeutronDataProblemEntries_return_problem_entries(self):

        fname = self.neutron_peak_19_file()

        with open(fname) as probf:
            entries = get_neutron_data_problem_entries(probf)
        entries_expected = self.expected_neutron_problem_entries()

        self.assertEqual(entries_expected['name'], entries['name'])
        self.assertEqual(entries_expected['input_file'], entries['input_file'])
        self.assertEqual(entries_expected['function'], entries['function'])
        self.assertEqual(entries_expected['fit_parameters'],
                         entries['fit_parameters'])
        self.assertEqual(entries_expected['description'],
                         entries['description'])


if __name__ == "__main__":
    unittest.main()
