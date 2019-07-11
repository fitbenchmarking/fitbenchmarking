from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np
import json

# Delete four lines below when automated tests are enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from fitting.mantid.externals import store_main_problem_data
from parsing.parse import parse_problem_file
from parsing.parse import check_problem_attributes
from parsing.parse import determine_problem_type
from parsing.parse_fitbenchmark_data import FittingProblem
from parsing.base_fitting_problem import BaseFittingProblem


class ParseFitbenchmarkTests(unittest.TestCase):

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

    def expected_fitbenchmark_problem_entries(self):

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

    def expected_neutron_problem(self):

        bench_prob_dir = self.get_bench_prob_dir()
        entries = self.expected_fitbenchmark_problem_entries()
        fname = self.neutron_peak_19_file()
        problem = BaseFittingProblem(fname)
        problem.name = entries['name']
        problem.equation = entries['function']
        problem.starting_values = None
        if 'fit_parameters' in entries:
            problem.start_x = entries['fit_parameters']['StartX']
            problem.end_x = entries['fit_parameters']['EndX']
        data_file = os.path.join(bench_prob_dir, 'Neutron_data',
                                 'data_files', entries['input_file'])
        store_main_problem_data(data_file, problem)

        return problem

    def test_ParseProblemFileFitbenchmark_returns_correct_problem_object(self):

        fname = self.neutron_peak_19_file()

        problem = parse_problem_file(fname)
        problem_expected = self.expected_neutron_problem()

        self.assertEqual(problem_expected.name, problem.name)
        self.assertEqual(problem_expected.equation, problem.equation)
        self.assertEqual(problem_expected.starting_values,
                         problem.starting_values)
        self.assertEqual(problem_expected.start_x, problem.start_x)
        self.assertEqual(problem_expected.end_x, problem.end_x)

    def test_getDataFilesDir_return_data_files_path(self):

        fname = self.neutron_peak_19_file()
        input_file = 'ENGINX193749_calibration_spec651.nxs'
        bench_prob_dir = self.get_bench_prob_dir()
        prob = FittingProblem(fname)
        data_file = prob.get_data_file(fname, input_file)
        data_file_expected = os.path.join(bench_prob_dir, 'Neutron_data',
                                          'data_files', input_file)

        self.assertEqual(data_file_expected, data_file)

    def test_getFitbenchmarkDataProblemEntries_return_problem_entries(self):

        fname = self.neutron_peak_19_file()
        prob = FittingProblem(fname)
        with open(fname) as probf:
            entries = prob.get_fitbenchmark_data_problem_entries(probf)
        entries_expected = self.expected_fitbenchmark_problem_entries()

        self.assertEqual(entries_expected['name'], entries['name'])
        self.assertEqual(entries_expected['input_file'], entries['input_file'])
        self.assertEqual(entries_expected['function'], entries['function'])
        self.assertEqual(entries_expected['fit_parameters'],
                         entries['fit_parameters'])
        self.assertEqual(entries_expected['description'],
                         entries['description'])

    def test_storeMiscProbData(self):
        fname = self.neutron_peak_19_file()
        problem = FittingProblem(fname)
        entries = self.expected_fitbenchmark_problem_entries()

        self.assertEqual(entries['name'], problem.name)
        self.assertEqual(entries['function'], problem.equation)
        self.assertEqual(entries['fit_parameters']['StartX'], problem.start_x)
        self.assertEqual(entries['fit_parameters']['EndX'], problem.end_x)
        self.assertEqual(None, problem.starting_values)

    def test_checkingAttributesAssertion(self):
        fname = self.neutron_peak_19_file()
        prob = BaseFittingProblem(fname)
        with self.assertRaises(ValueError):
            check_problem_attributes(prob)

    def test_checkingDetermineProblemType(self):
        f = open("RandomData.txt", "w+")
        for i in range(10):
            f.write("This is line %d\r\n" % (i + 1))
        f.close()
        with self.assertRaises(RuntimeError):
            determine_problem_type("RandomData.txt")
        os.remove("RandomData.txt")


if __name__ == "__main__":
    unittest.main()
