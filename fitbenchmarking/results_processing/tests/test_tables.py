"""
Table tests
"""

from __future__ import (absolute_import, division, print_function)
import unittest
from inspect import getfile
import os
import shutil
import numpy as np

import fitbenchmarking
from fitbenchmarking.results_processing.tables import SORTED_TABLE_NAMES
from fitbenchmarking.results_processing.tables import generate_table
from fitbenchmarking.results_processing.tables import create_results_tables
from fitbenchmarking.jacobian.SciPyFD_2point_jacobian import ScipyTwoPoint
from fitbenchmarking.core.results_output import preproccess_data
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


# By design both fitting_function_1 and fitting_function_2 need data as an
# argument
# pylint: disable=unused-argument
def fitting_function_1(data, x1, x2):
    """
    Fitting function evaluator

    :param data: x data
    :type data: numpy array
    :param x1: fitting parameter
    :type x1: float
    :param x2: fitting parameter
    :type x2: float

    :return: y data values evaluated from the function of the problem
    :rtype: numpy array
    """
    return x1 * np.sin(x2)


def fitting_function_2(data, x1, x2):
    """
    Fitting function evaluator

    :param data: x data
    :type data: numpy array
    :param x1: fitting parameter
    :type x1: float
    :param x2: fitting parameter
    :type x2: float

    :return: y data values evaluated from the function of the problem
    :rtype: numpy array
    """
    return x1 * x2

# pylint: enable=unused-argument


def generate_mock_results():
    """
    Generates results to test against

    :return: best results calculated using the chi_sq value, list of results
             and the options
    :rtype: tuple(list of best results,
                  list of list fitting results,
                  Options object)
    """
    software = 'scipy_ls'
    options = Options()
    options.software = [software]
    num_min = len(options.minimizers[options.software[0]])
    data_x = np.array([[1, 4, 5], [2, 1, 5]])
    data_y = np.array([[1, 2, 1], [2, 2, 2]])
    data_e = np.array([[1, 1, 1], [1, 2, 1]])
    func = [fitting_function_1, fitting_function_2]
    problems = [FittingProblem(options), FittingProblem(options)]

    params_in = [[[.3, .11], [.04, 2], [3, 1], [5, 0]],
                 [[4, 2], [3, .006], [.3, 10], [9, 0]]]

    starting_values = [{"a": .3, "b": .11}, {"a": 0, "b": 0}]
    error_in = [[1, 0, 2, 0],
                [0, 1, 3, 1]]
    link_in = [['link1', 'link2', 'link3', 'link4'],
               ['link5', 'link6', 'link7', 'link8']]
    acc_in = [[1, 5, 2, 1.54],
              [7, 3, 5, 1]]
    runtime_in = [[1e-2, 2.2e-3, 4.2e-5, 9.8e-1],
                  [3.0e-10, 5.0e-14, 1e-7, 4.3e-12]]

    results_out = []
    for i, p in enumerate(problems):
        p.data_x = data_x[i]
        p.data_y = data_y[i]
        p.data_e = data_e[i]
        p.function = func[i]
        p.name = "prob_{}".format(i)
        results = []
        for j in range(num_min):
            p.starting_values = starting_values
            jac = ScipyTwoPoint(p)
            r = FittingResult(options=options, problem=p, jac=jac,
                              initial_params=starting_values,
                              params=params_in[i][j])
            r.chi_sq = acc_in[i][j]
            r.runtime = runtime_in[i][j]
            r.error_flag = error_in[i][j]
            r.support_page_link = link_in[i][j]
            r.minimizer = options.minimizers[software][j]
            results.append(r)
        results_out.append(results)
    best = preproccess_data(results_out)
    return best, results_out, options


class GenerateTableTests(unittest.TestCase):
    """
    Class that tests the generate_table function within
    fitbenchmarking.results_processing.tables
    """

    def setUp(self):
        """
        Setup up method for test
        """
        self.best, self.results, self.options = generate_mock_results()
        root = os.path.dirname(getfile(fitbenchmarking))

        self.expected_results_dir = os.path.join(root, 'results_processing',
                                                 'tests', 'expected_results')

    def test_tables_correct(self):
        """
        Test that the tables are equal to the expected output stored in
        fitbenchmarking/results_processing/tests/expected_results
        """
        for suffix in SORTED_TABLE_NAMES:
            _, html_table, txt_table = generate_table(
                self.results, self.best, self.options, "group_dir",
                ["pp_1", "pp_2"], "table_name", suffix)
            html_table_name = os.path.join(self.expected_results_dir,
                                           "{}.html".format(suffix))
            txt_table_name = os.path.join(self.expected_results_dir,
                                          "{}.txt".format(suffix))

            for f, t in zip([html_table_name, txt_table_name],
                            [html_table, txt_table]):
                self.compare_files(f, t)

    def compare_files(self, expected_table, table):
        """
        Compares two tables line by line

        :param expected_table: imported html output from expected results in
                               fitbenchmarking/results_processing/tests/
                               expected_results
        :type expected_table: str
        :param table: table generated using generate_table in
                      fitbenchmarking.results_processing.tables
        :type table: str
        """
        with open(expected_table, 'r') as f:
            expected = f.readlines()

        file_extension = expected_table.split('.')[1]
        if file_extension == 'txt':
            html_id_expected = ''
            html_id = ''
        elif file_extension == 'html':
            html_id_expected = expected[1].strip(' ').split('row')[0][1:]
            html_id = table.splitlines()[1].strip(' ').split('row')[0][1:]
        diff = []
        for act_line, exp_line in zip(table.splitlines(), expected):
            exp_line = '' if exp_line is None else exp_line.strip('\n')
            act_line = '' if act_line is None else act_line.strip('\n')
            exp_line = exp_line.replace(html_id_expected, html_id)
            # to pass on windows need to first do this before comparing
            act_line = act_line.replace('href=\"..\\', 'href=\"../')
            if act_line != exp_line:
                diff.append([exp_line, act_line])
        self.assertListEqual([], diff)


class CreateResultsTableTests(unittest.TestCase):
    """
    Class that tests the generate_table function within
    fitbenchmarking.results_processing.create_results_tables
    """

    def setUp(self):
        """
        Setup up method for test
        """
        self.best, self.results, self.options = generate_mock_results()
        root = os.path.dirname(getfile(fitbenchmarking))

        self.group_dir = os.path.join(root, 'results_processing',
                                      'tests', 'results')
        os.mkdir(self.group_dir)
        self.group_name = 'test_name'

    def tearDown(self):
        """
        Deletes temporary folder and results produced
        """
        if os.path.exists(self.group_dir):
            shutil.rmtree(self.group_dir)

    def test_generate_table_page(self):
        """
        Checks to see whether files with the correct name are produced.
        """
        create_results_tables(self.options, self.results, self.best,
                              self.group_name, self.group_dir,
                              ["pp_1", "pp_2"], [], {'min1': []})
        for suffix in SORTED_TABLE_NAMES:

            for table_type in ['html', 'txt']:
                table_name = '{}_{}_weighted_table.{}'.format(self.group_name,
                                                              suffix,
                                                              table_type)
                file_name = os.path.join(self.group_dir, table_name)
                self.assertTrue(os.path.isfile(file_name))


if __name__ == "__main__":
    unittest.main()
