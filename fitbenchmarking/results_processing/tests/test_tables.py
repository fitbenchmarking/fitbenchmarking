"""
Table tests
"""

import os
import shutil
import unittest
from inspect import getfile

import numpy as np

import fitbenchmarking
from fitbenchmarking.core.results_output import preprocess_data
from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.jacobian.default_jacobian import Default as DefaultJac
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.results_processing.tables import (SORTED_TABLE_NAMES,
                                                       create_results_tables,
                                                       generate_table)
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
            cost_func = WeightedNLLSCostFunc(p)
            jac = DefaultJac(p)
            cost_func.jacobian = jac
            hess = None
            r = FittingResult(options=options,
                              cost_func=cost_func,
                              jac=jac.name(),
                              hess=hess,
                              initial_params=starting_values,
                              params=params_in[i][j],
                              name=p.name,
                              chi_sq=acc_in[i][j],
                              runtime=runtime_in[i][j],
                              software=software,
                              minimizer=options.minimizers[software][j],
                              error_flag=error_in[i][j],
                              algorithm_type='all, ls',
                              )
            r.fitting_report_link = link_in[i][j]
            r.problem_summary_page_link = 'link0'
            results.append(r)
        results_out.extend(results)
    best_results, results_out = preprocess_data(results_out)
    return best_results, results_out, options


class GenerateTableTests(unittest.TestCase):
    """
    Class that tests the generate_table function within
    fitbenchmarking.results_processing.tables
    """

    def setUp(self):
        """
        Setup up method for test
        """
        self.best_results, self.results, self.options = generate_mock_results()
        root = os.path.dirname(getfile(fitbenchmarking))

        self.expected_results_dir = os.path.join(root, 'results_processing',
                                                 'tests', 'expected_results')

        self.fig_dir = os.path.join(root, 'results_processing',
                                    'tests', 'figures')
        os.mkdir(self.fig_dir)

    def tearDown(self):
        """
        Deletes temporary folder and results produced
        """
        if os.path.exists(self.fig_dir):
            shutil.rmtree(self.fig_dir)

    def test_tables_correct(self):
        """
        Test that the tables are equal to the expected output stored in
        fitbenchmarking/results_processing/tests/expected_results
        """
        for suffix in SORTED_TABLE_NAMES:
            _, html, txt_table, _ = generate_table(
                results=self.results,
                best_results=self.best_results,
                options=self.options,
                group_dir="group_dir",
                fig_dir=self.fig_dir,
                pp_locations=["pp_1", "pp_2"],
                table_name="table_name",
                suffix=suffix)
            html_table_name = os.path.join(self.expected_results_dir,
                                           f"{suffix}.html")
            txt_table_name = os.path.join(self.expected_results_dir,
                                          f"{suffix}.txt")
            for f, t in zip([html_table_name, txt_table_name],
                            [html["table"], txt_table]):
                self.compare_files(f, t)

    def test_dropdown_html_correct(self):
        """
        Test that the HTML for dropdown menus used for hiding/showing
        table rows and columns is generated as expected.
        """
        _, html, _, _ = generate_table(
            results=self.results,
            best_results=self.best_results,
            options=self.options,
            group_dir="group_dir",
            fig_dir=self.fig_dir,
            pp_locations=["pp_1", "pp_2"],
            table_name="table_name",
            suffix="compare")

        expected_problem_dropdown = os.path.join(self.expected_results_dir,
                                                 "problem_dropdown.html")
        expected_minimizer_dropdown = os.path.join(self.expected_results_dir,
                                                   "minimizer_dropdown.html")

        for expected_file, dropdown_name in zip(
                [expected_problem_dropdown, expected_minimizer_dropdown],
                ["problem_dropdown", "minim_dropdown"]):
            self.compare_files(expected_file, html[dropdown_name])

    def compare_files(self, expected, achieved):
        """
        Compares two files line by line

        :param expected: imported HTML output from expected results in
                         fitbenchmarking/results_processing/tests/
                         expected_results
        :type expected: str
        :param achieved: HTML generated using generate_table in
                         fitbenchmarking.results_processing.tables
        :type achieved: str
        """
        with open(expected, 'r') as f:
            exp_lines = f.readlines()

        diff = []
        for i, (act_line, exp_line) in enumerate(
                zip(achieved.splitlines(), exp_lines)):
            exp_line = '' if exp_line is None else exp_line.strip('\n')
            act_line = '' if act_line is None else act_line.strip('\n')
            # to pass on windows need to first do this before comparing
            act_line = act_line.replace('href=\"..\\', 'href=\"../')
            if act_line != exp_line:
                diff.append([i, exp_line, act_line])
        if diff != []:
            print(f"Comparing against {expected}\n"
                  + "\n".join([f'== Line {change[0]} ==\n'
                               f'Expected :{change[1]}\n'
                               f'Actual   :{change[2]}'
                               for change in diff]))
            print("\n==\n")
            print("Output generated (also saved as actual.out):")
            print(achieved)
            with open("actual.out", "w") as outfile:
                outfile.write(achieved)
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
        self.best_results, self.results, self.options = generate_mock_results()
        root = os.path.dirname(getfile(fitbenchmarking))

        self.group_dir = os.path.join(root, 'results_processing',
                                      'tests', 'results')
        os.mkdir(self.group_dir)

        self.fig_dir = os.path.join(root, 'results_processing',
                                    'tests', 'figures')
        os.mkdir(self.fig_dir)

        self.group_name = 'test_name'

    def tearDown(self):
        """
        Deletes temporary folder and results produced
        """
        if os.path.exists(self.group_dir):
            shutil.rmtree(self.group_dir)

        if os.path.exists(self.fig_dir):
            shutil.rmtree(self.fig_dir)

    def test_generate_table_page(self):
        """
        Checks to see whether files with the correct name are produced.
        """
        create_results_tables(options=self.options,
                              results=self.results,
                              best_results=self.best_results,
                              group_dir=self.group_dir,
                              fig_dir=self.fig_dir,
                              pp_locations=["pp_1", "pp_2"],
                              failed_problems=[],
                              unselected_minimzers={'min1': []})
        for suffix in SORTED_TABLE_NAMES:

            for table_type in ['html', 'txt']:
                table_name = f'{suffix}_table.{table_type}'
                file_name = os.path.join(self.group_dir, table_name)
                self.assertTrue(os.path.isfile(file_name),
                                f"Could not find {file_name}")


if __name__ == "__main__":
    unittest.main()
