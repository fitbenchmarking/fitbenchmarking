from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from fitting.mantid.externals import store_main_problem_data
from parsing.parse_data import load_file
from parsing.parse_data import get_data_file
from parsing.parse_data import get_txt_data_problem_entries
from parsing.parse_data import store_misc_problem_data

from parsing.parse_data import store_prob_details
from parsing.parse_data import parse_line_by_line
from parsing.parse_data import get_dat_model
from parsing.parse_data import get_dat_starting_values
from parsing.parse_data import get_data_pattern_txt
from parsing.parse_data import parse_data_pattern
from parsing.parse_data import parse_equation

from utils import fitbm_problem


class ParseTxtTests(unittest.TestCase):

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

    def expected_neutron_problem(self):

        bench_prob_dir = self.get_bench_prob_dir()
        entries = self.expected_neutron_problem_entries()
        problem = fitbm_problem.FittingProblem()
        problem.name = entries['name']
        problem.equation = entries['function']
        problem.starting_values = None
        if 'fit_parameters' in entries:
            problem.start_x = entries['fit_parameters']['StartX']
            problem.end_x = entries['fit_parameters']['EndX']
        problem.ref_residual_sum_sq = 0
        data_file = os.path.join(bench_prob_dir, 'Neutron_data',
                                 'data_files', entries['input_file'])
        store_main_problem_data(data_file, problem)

        return problem

    def test_loadFile_returns_correct_problem_object(self):

        fname = self.neutron_peak_19_file()

        problem = load_file(fname)
        problem_expected = self.expected_neutron_problem()

        self.assertEqual(problem_expected.name, problem.name)
        self.assertEqual(problem_expected.equation, problem.equation)
        self.assertEqual(problem_expected.starting_values,
                         problem.starting_values)
        self.assertEqual(problem_expected.start_x, problem.start_x)
        self.assertEqual(problem_expected.end_x, problem.end_x)
        self.assertEqual(problem_expected.ref_residual_sum_sq,
                         problem.ref_residual_sum_sq)

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
            entries = get_txt_data_problem_entries(probf)
        entries_expected = self.expected_neutron_problem_entries()

        self.assertEqual(entries_expected['name'], entries['name'])
        self.assertEqual(entries_expected['input_file'], entries['input_file'])
        self.assertEqual(entries_expected['function'], entries['function'])
        self.assertEqual(entries_expected['fit_parameters'],
                         entries['fit_parameters'])
        self.assertEqual(entries_expected['description'],
                         entries['description'])

    def test_storeMiscProbData(self):

        problem = fitbm_problem.FittingProblem()
        entries = self.expected_neutron_problem_entries()

        store_misc_problem_data(problem, entries)

        self.assertEqual(entries['name'], problem.name)
        self.assertEqual(entries['function'], problem.equation)
        self.assertEqual(entries['fit_parameters']['StartX'], problem.start_x)
        self.assertEqual(entries['fit_parameters']['EndX'], problem.end_x)
        self.assertEqual(None, problem.starting_values)


class ParseNistTests(unittest.TestCase):

    def misra1a_file(self):
        """
        Helper function that returns the path to
        /fitbenchmarking/benchmark_problems
        """

        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(os.path.normpath(test_dir))
        main_dir = os.path.dirname(os.path.normpath(parent_dir))
        root_dir = os.path.dirname(os.path.normpath(main_dir))
        bench_prob_dir = os.path.join(root_dir, 'benchmark_problems')
        fname = os.path.join(bench_prob_dir, 'NIST_low_diff', 'Misra1a.dat')

        return fname

    def setup_misra1a_data_pattern_lines(self):

        lines = ['Data:   y               x',
                 '10.07E0      77.6E0',
                 '14.73E0     114.9E0',
                 '17.94E0     141.1E0',
                 '23.93E0     190.8E0',
                 '29.61E0     239.9E0',
                 '35.18E0     289.0E0',
                 '40.02E0     332.8E0',
                 '44.82E0     378.4E0',
                 '50.76E0     434.8E0',
                 '55.05E0     477.3E0',
                 '61.01E0     536.8E0',
                 '66.40E0     593.1E0',
                 '75.47E0     689.1E0',
                 '81.78E0     760.0E0'
                 ]

        return lines

    def setup_misra1a_model_lines(self):

        lines = ["Model:         Exponential Class\n",
                 "               2 Parameters (b1 and b2)\n",
                 "\n",
                 "               y = b1*(1-exp[-b2*x])  +  e\n",
                 "\n"]

        return lines

    def setup_misra1a_startvals_lines(self):

        lines = ["\n",
                 "\n",
                 "  b1 =   500         250"
                 "           2.3894212918E+02  2.7070075241E+00",
                 "  b2 =     0.0001      0.0005"
                 "      5.5015643181E-04  7.2668688436E-06"]

        return lines

    def setup_misra1a_data_pattern_text(self):

        data_pattern_text_expected = ['      10.07E0      77.6E0\n',
                                      '      14.73E0     114.9E0\n',
                                      '      17.94E0     141.1E0\n',
                                      '      23.93E0     190.8E0\n',
                                      '      29.61E0     239.9E0\n',
                                      '      35.18E0     289.0E0\n',
                                      '      40.02E0     332.8E0\n',
                                      '      44.82E0     378.4E0\n',
                                      '      50.76E0     434.8E0\n',
                                      '      55.05E0     477.3E0\n',
                                      '      61.01E0     536.8E0\n',
                                      '      66.40E0     593.1E0\n',
                                      '      75.47E0     689.1E0\n',
                                      '      81.78E0     760.0E0\n']

        return data_pattern_text_expected

    def setup_misra1a_expected_data_points(self):

        data_pattern = np.array([[10.07, 77.6],
                                 [14.73, 114.9],
                                 [17.94, 141.1],
                                 [23.93, 190.8],
                                 [29.61, 239.9],
                                 [35.18, 289.0],
                                 [40.02, 332.8],
                                 [44.82, 378.4],
                                 [50.76, 434.8],
                                 [55.05, 477.3],
                                 [61.01, 536.8],
                                 [66.40, 593.1],
                                 [75.47, 689.1],
                                 [81.78, 760.0]])

        return data_pattern

    def setup_nist_expected_problem(self):

        prob = fitbm_problem.FittingProblem()
        prob.name = 'Misra1a'
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0, 250.0]], ['b2', [0.0001, 0.0005]]]
        data_pattern = self.setup_misra1a_expected_data_points()
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]
        prob.ref_residual_sum_sq = 1.2455138894e-01

        return prob

    def test_loadFile_correct_problem_object(self):

        fname = self.misra1a_file()

        problem = load_file(fname)
        problem_expected = self.setup_nist_expected_problem()

        self.assertEqual(problem_expected.name, problem.name)
        self.assertEqual(problem_expected.equation, problem.equation)
        self.assertEqual(problem_expected.starting_values,
                         problem.starting_values)
        np.testing.assert_allclose(problem_expected.data_x, problem.data_x)
        np.testing.assert_allclose(problem_expected.data_y, problem.data_y)
        self.assertEqual(problem_expected.ref_residual_sum_sq,
                         problem.ref_residual_sum_sq)

    def test_storeProbDetails_correct_storing(self):

        fname = self.misra1a_file()
        parsed_eq = 'b1*(1-exp(-b2*x))'
        starting_values = [['b1', [500.0, 250.0]], ['b2', [0.0001, 0.0005]]]
        data_pattern = self.setup_misra1a_expected_data_points()
        residual_sum_sq = 1.2455138894e-01

        with open(fname) as spec_file:
            prob = store_prob_details(spec_file, parsed_eq, starting_values,
                                      data_pattern, residual_sum_sq)

        prob_expected = self.setup_nist_expected_problem()

        self.assertEqual(prob_expected.name, prob.name)
        self.assertEqual(prob_expected.equation, prob.equation)
        self.assertEqual(prob_expected.starting_values,
                         prob.starting_values)
        np.testing.assert_allclose(prob_expected.data_x, prob.data_x)
        np.testing.assert_allclose(prob_expected.data_y, prob.data_y)
        self.assertEqual(prob_expected.ref_residual_sum_sq,
                         prob.ref_residual_sum_sq)

    def test_parseLineByLine_correct_lines(self):

        fname = self.misra1a_file()

        with open(fname) as spec_file:
            lines = spec_file.readlines()
            equation_text, data_pattern_text, \
                starting_values, residual_sum_sq = parse_line_by_line(lines)

        equation_text_expected = 'y = b1*(1-exp[-b2*x])  +  e'
        data_pattern_text_expected = self.setup_misra1a_data_pattern_text()
        starting_values_expected = [['b1', [500.0, 250.0]],
                                    ['b2', [0.0001, 0.0005]]]
        residual_sum_sq_expected = 1.2455138894e-01

        self.assertEqual(equation_text_expected, equation_text)
        self.assertListEqual(data_pattern_text_expected, data_pattern_text)
        self.assertListEqual(starting_values_expected, starting_values)
        self.assertEqual(residual_sum_sq_expected, residual_sum_sq)

    def test_getNistModel_return_proper_eqtxt(self):

        lines = self.setup_misra1a_model_lines()
        idx = 0

        equation_text, idx = get_dat_model(lines, idx)
        equation_text_expected = 'y = b1*(1-exp[-b2*x])  +  e'
        idx_expected = 4

        self.assertEqual(equation_text_expected, equation_text)
        self.assertEqual(idx_expected, idx)

    def test_getNistModel_fail_runtimeError(self):

        lines = ["\n", "\n"]
        idx = 33

        self.assertRaises(RuntimeError, get_dat_model, lines, idx)

    def test_getNistStartingValues_return_proper_startvaltxt(self):

        lines = self.setup_misra1a_startvals_lines()
        idx = 0

        starting_vals, idx = get_dat_starting_values(lines, idx)
        starting_vals_expected = [['b1', [500.0, 250.0]],
                                  ['b2', [0.0001, 0.0005]]]
        idx = 3

        for idx in range(0, len(starting_vals_expected)):
            self.assertEqual(starting_vals_expected[idx][0],
                             starting_vals[idx][0])
            self.assertListEqual(starting_vals_expected[idx][1],
                                 starting_vals[idx][1])

    def test_getNistStartingValues_fail_startvals_invalid(self):

        lines = ["\n",
                 "\n",
                 "  b1 =   500         250   ",
                 "  b2 =     0.0001      0.0005"
                 "      5.5015643181E-04  7.2668688436E-06"]
        idx = 0

        self.assertRaises(RuntimeError, get_dat_starting_values, lines, idx)

    def test_getDataPatternTxt_correct_data(self):

        lines = self.setup_misra1a_data_pattern_lines()
        idx = 0

        data_pattern_text, idx = get_data_pattern_txt(lines, idx)
        data_pattern_text_expected = self.setup_misra1a_data_pattern_lines()
        idx_expected = 15

        self.assertEqual(idx_expected, idx)
        self.assertListEqual(data_pattern_text_expected, data_pattern_text)

    def test_getDataPatternTxt_raises_error(self):

        lines = []
        idx = 0

        self.assertRaises(RuntimeError, get_data_pattern_txt, lines, idx)

    def test_parseDataPattern_return_parsed_data_pattern_array(self):

        data_pattern_text = self.setup_misra1a_data_pattern_text()

        data_points = parse_data_pattern(data_pattern_text)
        data_points_expected = self.setup_misra1a_expected_data_points()

        np.testing.assert_array_equal(data_points_expected, data_points)

    def test_parseEquation_return_proper_equation_form(self):

        equation_text = 'y = b1*(1-exp[-b2*x])  +  e'

        equation = parse_equation(equation_text)
        equation_expected = 'b1*(1-exp(-b2*x))'

        self.assertEqual(equation_expected, equation)

    def test_parseEquation_fail_runtimeError(self):

        equation_text = 'LULy = bf1*(1-exdsp[-b2as*x])  +  e'

        self.assertRaises(RuntimeError, parse_equation, equation_text)


if __name__ == "__main__":
    unittest.main()
