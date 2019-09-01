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
fb_dir = os.path.dirname(os.path.normpath(main_dir))
sys.path.insert(0, main_dir)
sys.path.insert(1,fb_dir)

try:
    import sasmodels.data
except:
    print('******************************************\n'
          'sasmodels is not yet installed on your computer\n'
          'To install, type the following command:\n'
          'python -m pip install sasmodels\n'
          '******************************************')
    sys.exit()

from parsing.parse import parse_problem_file
from parsing.parse import check_problem_attributes
from parsing.parse import determine_problem_type
from parsing.parse_sasview_data import FittingProblem
from mock_problem_files.get_problem_files import get_file


class ParseSasViewTests(unittest.TestCase):

    def get_bench_prob_dir(self):

        prob_path = get_file('SV_cyl_400_20.txt')
        bench_prob_dir = os.path.dirname(prob_path)

        return bench_prob_dir

    def expected_SAS_modelling_1D_problem_entries(self):

        entries = {}
        entries['name'] = "Problem Def 1"

        entries['input_file'] = "SV_cyl_400_20.txt"

        entries['function'] = ("name=cylinder,radius=35.0,length=350.0,background=0.0,scale=1.0,sld=4.0,sld_solvent=1.0")
        entries['parameter_ranges'] = ("radius.range(1,50);length.range(1,500)")
        entries['description'] = ''

        return entries

    def expected_SAS_modelling_1D_problem(self):

        entries = self.expected_SAS_modelling_1D_problem_entries()
        fname = get_file('SV_prob_def_1.txt')
        problem = FittingProblem(fname)
        problem.name = entries['name']
        problem.equation = (entries['function'].split(',', 1))[0]
        problem.starting_values = (entries['function'].split(',', 1))[1]
        self._starting_value_ranges = entries['parameter_ranges']

        return problem

    def test_eval_f(self):

        fname = get_file('SV_prob_def_1.txt')

        problem = FittingProblem(fname)

        y_values = problem.eval_f(problem.data_x[:10], 'radius=35,length=350,background=0.0,scale=1.0,sld=4.0,sld_solvent=1.0')

        y_values_expected = np.array([3.34929172e+02, 9.61325700e+01, 1.92262557e+01, 1.21868330e+00, 7.96766671e-01, 1.27924690e+00, 4.70120551e-01, 1.96891429e-02, 1.54944490e-01, 1.69598579e-01])

        np.testing.assert_allclose(y_values_expected, y_values, rtol=1e-5, atol=0)

    def test_getFunction_returns_correct_function(self):

        fname = get_file('SV_prob_def_1.txt')

        problem = FittingProblem(fname)

        function = problem.get_function()

        function_obj_str = function[0][0]

        y_values = function_obj_str(problem.data_x[:10], 'radius=35,length=350,background=0.0,scale=1.0,sld=4.0,sld_solvent=1.0')

        y_values_expected = np.array(
            [3.34929172e+02, 9.61325700e+01, 1.92262557e+01, 1.21868330e+00, 7.96766671e-01, 1.27924690e+00,
             4.70120551e-01, 1.96891429e-02, 1.54944490e-01, 1.69598579e-01])

        param_array = function[0][1]

        param_array_expected = np.array([35., 350., 0., 1., 4., 1.])

        np.testing.assert_allclose(y_values_expected, y_values, rtol=1e-5, atol=0)
        np.testing.assert_array_equal(param_array_expected, param_array)

    def test_ParseProblemFileSasView_returns_correct_problem_object(self):

        fname = get_file('SV_prob_def_1.txt')

        problem = parse_problem_file(fname)
        problem_expected = self.expected_SAS_modelling_1D_problem()

        self.assertEqual(problem_expected.name, problem.name)
        self.assertEqual(problem_expected.equation, problem.equation)
        self.assertEqual(problem_expected.starting_values,
                         problem.starting_values)
        self.assertEqual(problem_expected.start_x, problem.start_x)
        self.assertEqual(problem_expected.end_x, problem.end_x)

    def test_getDataFilesDir_return_data_files_path(self):

        fname = get_file('SV_prob_def_1.txt')
        input_file = 'SV_cyl_400_20.txt'

        bench_prob_dir = self.get_bench_prob_dir()
        prob = FittingProblem(fname)
        data_file = prob.get_data_file(fname, input_file)
        data_file_expected = os.path.join(bench_prob_dir, input_file)

        self.assertEqual(data_file_expected, data_file)

    def test_getSasViewDataProblemEntries_return_problem_entries(self):

        fname = get_file('SV_prob_def_1.txt')
        prob = FittingProblem(fname)
        with open(fname) as probf:
            entries = prob.get_data_problem_entries(probf)
        entries_expected = self.expected_SAS_modelling_1D_problem_entries()

        self.assertEqual(entries_expected['name'], entries['name'])
        self.assertEqual(entries_expected['input_file'], entries['input_file'])
        self.assertEqual(entries_expected['function'], entries['function'])
        self.assertEqual(entries_expected['parameter_ranges'],
                         entries['parameter_ranges'])
        self.assertEqual(entries_expected['description'],
                         entries['description'])

    def test_storeMiscProbData(self):
        fname = get_file('SV_prob_def_1.txt')
        problem = FittingProblem(fname)
        entries = self.expected_SAS_modelling_1D_problem_entries()

        self.assertEqual(entries['name'], problem.name)
        self.assertEqual((entries['function'].split(',', 1))[0], problem.equation)
        self.assertEqual((entries['function'].split(',', 1))[1], problem.starting_values)
        self.assertEqual(entries['parameter_ranges'], problem.starting_value_ranges)
    #
    def test_checkingAttributesAssertion(self):
        fname = get_file('SV_prob_def_1.txt')
        prob = FittingProblem(fname)
    #     with self.assertRaises(ValueError):
        check_problem_attributes(prob)

    def test_checkingDetermineProblemType(self):
        f = open("RandomData.txt", "w+")
        for i in range(10):
            f.write("This is line %d\r\n" % (i + 1))
        f.close()
        with self.assertRaises(RuntimeError):
            determine_problem_type("RandomData.txt")
        os.remove("RandomData.txt")

    def test_get_start_x_and_end_x(self):

        fname = get_file('SV_prob_def_1.txt')
        prob = FittingProblem(fname)

        x_data = prob.data_x

        expected_start_x = 0.025
        expected_end_x = 0.5

        start_x, end_x = prob.get_start_x_and_end_x(x_data)

        self.assertEqual(expected_start_x, start_x)
        self.assertEqual(expected_end_x, end_x)


if __name__ == "__main__":
    unittest.main()
