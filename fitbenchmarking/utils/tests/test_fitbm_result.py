"""
Tests for FitBenchmarking object
"""
from __future__ import (absolute_import, division, print_function)
import inspect
import os
import unittest
import numpy as np

from fitbenchmarking import mock_problems
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.jacobian.numerical_2point_jacobian import ScipyTwoPoint
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


class FitbmResultTests(unittest.TestCase):
    """
    Tests for FitBenchmarking results object
    """

    def setUp(self):
        """
        Setting up FitBenchmarking results object
        """
        self.options = Options()
        mock_problems_dir = os.path.dirname(inspect.getfile(mock_problems))
        problem_dir = os.path.join(mock_problems_dir, "cubic.dat")
        self.problem = parse_problem_file(problem_dir, self.options)
        self.problem.correct_data()

        self.chi_sq = 10
        self.minimizer = "test_minimizer"
        self.runtime = 0.01
        self.params = np.array([1, 3, 4, 4])
        self.initial_params = np.array([0, 0, 0, 0])
        self.jac = ScipyTwoPoint(self.problem)
        self.result = FittingResult(
            options=self.options, problem=self.problem, jac=self.jac,
            chi_sq=self.chi_sq, runtime=self.runtime, minimizer=self.minimizer,
            initial_params=self.initial_params, params=self.params,
            error_flag=0)

        self.min_chi_sq = 0.1
        self.result.min_chi_sq = self.min_chi_sq
        self.min_runtime = 1
        self.result.min_runtime = self.min_runtime

        self.support_page_link = 'random_path_to_nothing'
        self.relative_dir = 'relative_random_path_to_nothing'

        self.result.support_page_link = self.support_page_link
        self.result.relative_dir = self.relative_dir
        self.comparison_mode = ['abs', 'rel', 'both']
        self.result.set_colour_scale()

        r = self.problem.eval_r(self.params)
        min_test = np.matmul(self.jac.eval(self.params).T, r)
        self.norm_rel = np.linalg.norm(min_test) / np.linalg.norm(r)

    def test_init_with_dataset_id(self):
        chi_sq = [10, 5, 1]
        minimizer = "test_minimizer"
        runtime = 0.01
        params = [np.array([1, 3, 4, 4]),
                  np.array([2, 3, 57, 8]),
                  np.array([4, 2, 5, 1])]
        initial_params = np.array([0, 0, 0, 0])

        self.problem.data_x = [np.array([3, 2, 1, 4]),
                               np.array([5, 1, 2, 3]),
                               np.array([6, 7, 8, 1])]
        self.problem.data_y = [np.array([2, 1, 7, 40]),
                               np.array([8, 9, 4, 2]),
                               np.array([7, 4, 4, 2])]
        self.problem.data_e = [np.array([1, 1, 1, 1]),
                               np.array([2, 2, 2, 1]),
                               np.array([2, 3, 4, 4])]
        self.problem.sorted_index = [np.array([2, 1, 0, 3]),
                                     np.array([1, 2, 3, 0]),
                                     np.array([3, 0, 1, 2])]
        jac = ScipyTwoPoint(self.problem)
        self.result = FittingResult(
            options=self.options, problem=self.problem, jac=jac,
            chi_sq=chi_sq, runtime=runtime, minimizer=minimizer,
            initial_params=initial_params, params=params,
            error_flag=0, dataset_id=1)

        self.assertTrue(
            np.isclose(self.result.data_x, self.problem.data_x[1]).all())
        self.assertTrue(
            np.isclose(self.result.data_y, self.problem.data_y[1]).all())
        self.assertTrue(
            np.isclose(self.result.data_e, self.problem.data_e[1]).all())
        self.assertTrue(
            np.isclose(self.result.sorted_index,
                       self.problem.sorted_index[1]).all())

        self.assertTrue(np.isclose(params[1], self.result.params).all())
        self.assertEqual(chi_sq[1], self.result.chi_sq)

    def test_default_print(self):
        """
        Testing defaults printing
        """
        name = "Fitting problem class: minimizer = {}".format(self.minimizer)
        self.assertEqual(self.result.__str__(), name)

    def test_acc_print(self):
        """
        Testing accuracy table printing
        """
        abs_val = self.chi_sq
        rel_val = self.chi_sq / self.min_chi_sq
        text_table, html_table = self.generate_expected_str_output([abs_val],
                                                                   [rel_val])
        self.shared_compare('acc', text_table, html_table)

    def test_runtime_print(self):
        """
        Testing runtime table printing
        """
        abs_val = self.runtime
        rel_val = self.runtime / self.min_runtime
        text_table, html_table = self.generate_expected_str_output([abs_val],
                                                                   [rel_val])
        self.shared_compare('runtime', text_table, html_table)

    def test_compare_print(self):
        """
        Testing compare table printing
        """
        runtime_abs_val = self.runtime
        runtime_rel_val = self.runtime / self.min_runtime
        acc_abs_val = self.chi_sq
        acc_rel_val = self.chi_sq / self.min_chi_sq

        abs_val = [acc_abs_val, runtime_abs_val]
        rel_val = [acc_rel_val, runtime_rel_val]

        text_table, html_table = self.generate_expected_str_output(abs_val,
                                                                   rel_val)
        self.shared_compare('compare', text_table, html_table)

    def test_local_min_print_false(self):
        """
        Testing local min table printing when params are not given
        """
        self.result.params = None
        self.assertEqual(self.result.local_min, "False")
        self.assertEqual(self.result.norm_rel, np.inf)

    def test_local_min_print_true(self):
        """
        Testing local min table printing when params are given
        """

        self.result.params = self.params
        self.assertEqual(self.result.local_min, "False")
        self.assertEqual(self.result.norm_rel, self.norm_rel)

    def test_local_min_print_colour(self):
        """
        Testing local min table colour
        """
        self.result.table_type = "local_min"
        self.assertEqual(self.result.colour, "#b30000")

    def test_local_min_print_table_output(self):
        """
        Testing local min table_output
        """
        self.result.table_type = "local_min"
        self.assertEqual(self.result.table_output,
                         "False ({:.4g})".format(self.norm_rel))

    def test_sanitised_name(self):
        """
        Test that sanitised names are correct.
        """
        self.result.name = 'test, name with commas'
        self.assertEqual(self.result.sanitised_name, 'test_name_with_commas')

    def generate_expected_str_output(self, abs_val, rel_val):
        """
        Shared function which computes expected string output

        :param abs_val: list of absolute values (e.g. [acc] and [acc, runtime])
        :type abs_val: list
        :param rel_val: list of relative values (e.g. [acc] and [acc, runtime])
        :type rel_val: list

        :return: list of expected string outputs for text and html tables
        :rtype: list
        """
        text_table = ['<br>'.join(["{:.4g}".format(v) for v in abs_val]),
                      '<br>'.join(["{:.4g}".format(v) for v in rel_val]),
                      '<br>'.join("{0:.4g} ({1:.4g})".format(v1, v2)
                                  for v1, v2 in zip(abs_val, rel_val))]
        link = self.result.support_page_link
        html_table = ['<a href="../{0}">{1}</a>'.format(link, value)
                      for value in text_table]
        return text_table, html_table

    def shared_compare(self, table_type, text_table, html_table):
        """
        Shared function which compares text and html outputs

        :param table_type: table type ("abs", "rel" or "both")
        :type table_type: str
        :param text_table: expected text output
        :type text_table: list
        :param html_table: expected html output
        :type html_table: list

        """
        for mode, text, html in zip(self.comparison_mode,
                                    text_table, html_table):
            self.options.comparison_mode = mode
            # Note: need to reset table_type to enable different comparison
            # modes to be set
            self.result.table_type = table_type
            self.result.html_print = False
            self.assertEqual(self.result.__str__(), text)
            self.result.html_print = True
            self.assertEqual(self.result.__str__(), html)


if __name__ == "__main__":
    unittest.main()
