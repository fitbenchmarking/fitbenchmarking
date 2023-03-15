"""
Tests for functions in the base tables file.
"""

import os
from unittest import TestCase, mock

import numpy as np

from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.jacobian.default_jacobian import \
    Default as DefaultJacobian
from fitbenchmarking.jacobian.scipy_jacobian import Scipy as ScipyJacobian
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.results_processing.base_table import Table
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options
from fitbenchmarking.results_processing.base_table import (calculate_luminance,
                                                           calculate_contrast,
                                                           background_to_text)


def generate_results():
    """
    Create a predictable set of results.

    :return: Set of manually generated results
             The best results
    :rtype: dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]
            dict[str, dict[str, utils.fitbm_result.FittingResult]]
    """
    options = Options()
    results = {}

    data_x = np.array([[1, 4, 5], [2, 1, 5]])
    data_y = np.array([[1, 2, 1], [2, 2, 2]])
    data_e = np.array([[1, 1, 1], [1, 2, 1]])
    func = [lambda d, x1, x2: x1 * np.sin(x2), lambda d, x1, x2: x1 * x2]
    name = ['prob_0', 'prob_1']
    problems = [FittingProblem(options), FittingProblem(options)]
    starting_values = [{"a": .3, "b": .11}, {"a": 0, "b": 0}]
    for p, x, y, e, f, n, s in zip(problems, data_x, data_y, data_e,
                                   func, name, starting_values):
        p.data_x = x
        p.data_y = y
        p.data_e = e
        p.function = f
        p.name = n
        p.starting_values = [s]

    cost_func = WeightedNLLSCostFunc(problems[0])
    jac = [DefaultJacobian(cost_func), ScipyJacobian(cost_func)]
    jac[1].method = '2-point'
    hess = [None for j in jac]
    results['prob_0'] = {'cf1': [
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[0], hess=hess[0],
            initial_params=list(problems[0].starting_values[0].values()),
            params=[1, 1], name=problems[0].name, chi_sq=0.2, runtime=15,
            software='s1', minimizer='m10', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[0], hess=hess[0],
            initial_params=list(problems[0].starting_values[0].values()),
            params=[1, 1], name=problems[0].name, chi_sq=0.3, runtime=14,
            software='s1', minimizer='m11', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[0], hess=hess[0],
            initial_params=list(problems[0].starting_values[0].values()),
            params=[1, 1], name=problems[0].name, chi_sq=0.4, runtime=13,
            software='s0', minimizer='m01', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=None, hess=None,
            initial_params=list(problems[0].starting_values[0].values()),
            params=[1, 1], name=problems[0].name, chi_sq=np.inf,
            runtime=np.inf, software='s0', minimizer='m00', error_flag=4),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[1], hess=hess[1],
            initial_params=list(problems[0].starting_values[0].values()),
            params=[1, 1], name=problems[0].name, chi_sq=0.6, runtime=11,
            software='s1', minimizer='m10', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[1], hess=hess[1],
            initial_params=list(problems[0].starting_values[0].values()),
            params=[1, 1], name=problems[0].name, chi_sq=0.7, runtime=10,
            software='s1', minimizer='m11', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[1], hess=hess[1],
            initial_params=list(problems[0].starting_values[0].values()),
            params=[1, 1], name=problems[0].name, chi_sq=0.8, runtime=9,
            software='s0', minimizer='m01', error_flag=0),
    ]}
    results['prob_1'] = {'cf1': [
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[0], hess=hess[0],
            initial_params=list(problems[1].starting_values[0].values()),
            params=[1, 1], name=problems[1].name, chi_sq=1, runtime=1,
            software='s1', minimizer='m10', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[0], hess=hess[0],
            initial_params=list(problems[1].starting_values[0].values()),
            params=[1, 1], name=problems[1].name, chi_sq=1, runtime=1,
            software='s1', minimizer='m11', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[0], hess=hess[0],
            initial_params=list(problems[1].starting_values[0].values()),
            params=[1, 1], name=problems[1].name, chi_sq=2, runtime=2,
            software='s0', minimizer='m01', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[0], hess=hess[0],
            initial_params=list(problems[1].starting_values[0].values()),
            params=[1, 1], name=problems[1].name, chi_sq=np.inf,
            runtime=np.inf, software='s0', minimizer='m00', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[1], hess=hess[1],
            initial_params=list(problems[1].starting_values[0].values()),
            params=[1, 1], name=problems[1].name, chi_sq=3, runtime=3,
            software='s1', minimizer='m10', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[1], hess=hess[1],
            initial_params=list(problems[1].starting_values[0].values()),
            params=[1, 1], name=problems[1].name, chi_sq=3, runtime=3,
            software='s1', minimizer='m11', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[1], hess=hess[1],
            initial_params=list(problems[1].starting_values[0].values()),
            params=[1, 1], name=problems[1].name, chi_sq=4, runtime=4,
            software='s0', minimizer='m01', error_flag=0),
        FittingResult(
            options=options, cost_func=cost_func, jac=jac[1], hess=hess[1],
            initial_params=list(problems[1].starting_values[0].values()),
            params=[1, 1], name=problems[1].name, chi_sq=np.inf,
            runtime=np.inf, software='s0', minimizer='m00', error_flag=0),
    ]}

    best_results = {'prob_0': {'cf1': results['prob_0']['cf1'][0]},
                    'prob_1': {'cf1': results['prob_1']['cf1'][0]}}
    return results, best_results


class DummyTable(Table):
    """
    Create an instantiatable subclass of the abstract Table
    """

    def get_value(self, result):
        """
        Just use the chi_sq value

        :param result: The result to get the value for
        :type result: FittingResult
        :return: The value for the table
        :rtype: tuple[float]
        """
        return [result.chi_sq]


class CreateResultsDictTests(TestCase):
    """
    Tests for the create_results_dict function.
    """

    def test_create_results_dict_correct_dict(self):
        """
        Test that create_results_dict produces the correct format
        """
        results_list, best_results = generate_results()
        table = DummyTable(results=results_list,
                           best_results=best_results,
                           options=Options(),
                           group_dir='fake',
                           pp_locations=('no', 'pp'),
                           table_name='A table!')

        results_dict = table.sorted_results

        def check_result(r1, r2):
            """
            Utility function to give a useful error message if it fails.
            """
            self.assertIs(r1, r2,
                          f'Error: First result is {r1.problem_tag}-'
                          f'{r1.software_tag}-{r1.minimizer_tag}-'
                          f'{r1.jacobian_tag}.'
                          f' Second result is {r2.problem_tag}-'
                          f'{r2.software_tag}-{r2.minimizer_tag}-'
                          f'{r2.jacobian_tag}')
        for i in range(7):
            check_result(results_dict['prob_0'][i],
                         results_list['prob_0']['cf1'][i])
            check_result(results_dict['prob_1'][i],
                         results_list['prob_1']['cf1'][i])


class DisplayStrTests(TestCase):
    """
    Tests for the default display_str implementation.
    """

    def setUp(self):
        results, best_results = generate_results()
        self.table = DummyTable(results=results,
                                best_results=best_results,
                                options=Options(),
                                group_dir='fake',
                                pp_locations=('no', 'pp'),
                                table_name='A table!')

    def test_display_str_abs(self):
        """
        Test the abs string is as expected
        """
        self.table.options.comparison_mode = 'abs'
        s = self.table.display_str([7, 9])
        self.assertEqual(s, '9')

    def test_display_str_rel(self):
        """
        Test the rel string is as expected
        """
        self.table.options.comparison_mode = 'rel'
        s = self.table.display_str([7, 9])
        self.assertEqual(s, '7')

    def test_display_str_both(self):
        """
        Test the both string is as expected
        """
        self.table.options.comparison_mode = 'both'
        s = self.table.display_str([7, 9])
        self.assertEqual(s, '9 (7)')


class SaveColourbarTests(TestCase):
    """
    Tests for the save_colourbar implementation.
    """

    def setUp(self):
        results, best_results = generate_results()
        self.root_directory = os.path.join(os.path.dirname(__file__),
                                           os.pardir, os.pardir, os.pardir)
        self.table = DummyTable(results=results,
                                best_results=best_results,
                                options=Options(),
                                group_dir=self.root_directory,
                                pp_locations=('no', 'pp'),
                                table_name='A table!')

    @mock.patch("fitbenchmarking.results_processing.base_table.plt.savefig")
    def test_save_colourbar_returns_a_relative_path(self, savefig_mock):
        """
        Test the relative path to the colourbar figure is returned after saving
        """
        self.table.name = "fake_name"
        colourbar_file = f"{self.table.name}_cbar.png"

        figure_sub_directory = "fitbenchmarking_results"
        figure_directory = os.path.join(self.root_directory,
                                        figure_sub_directory)

        relative_path = os.path.join(figure_sub_directory, colourbar_file)
        self.assertEqual(self.table.save_colourbar(figure_directory),
                         relative_path)

        savefig_mock.assert_called_once()


class TestContrastRatio(TestCase):
    """
    Tests the three functions used for calculating the contrast ratio
    """
    def test_calculate_luminance(self):
        """
        Tests the luminance calculation using 6 subtests
        """
        luminance_test = (
             {'case': 'black', 'rgb': [0, 0, 0], 'output': 0},
             {'case': 'white', 'rgb': [1, 1, 1], 'output': 1},
             {'case': 'red', 'rgb': [1, 0, 0], 'output': 0.2126},
             {'case': 'green', 'rgb': [0, 1, 0], 'output': 0.7152},
             {'case': 'blue', 'rgb': [0, 0, 1], 'output': 0.0722},
             {'case': 'purple', 'rgb': [1, 0, 1], 'output': 0.2848}
        )
        for test in luminance_test:
            with self.subTest(test['case']):
                self.assertAlmostEqual(calculate_luminance(test['rgb']),
                                       test['output'])

    def test_calculate_contrast(self):
        """
        Tests the contrast ratio calculation using 6 subtests
        """
        contrast_test = (
             {'case': '1', 'background': [0, 0, 0],
              'foreground': [1, 1, 1], 'output': 21.00},
             {'case': '2', 'background': [1, 0, 0],
              'foreground': [0, 0, 0], 'output': 5.25},
             {'case': '3', 'background': [0, 1, 0],
              'foreground': [0, 0, 0], 'output': 15.30},
             {'case': '4', 'background': [0, 1, 0],
              'foreground': [1, 1, 1], 'output': 1.37},
             {'case': '5', 'background': [0, 0, 1],
              'foreground': [1, 1, 1], 'output': 8.59},
             {'case': '6', 'background': [0, 0, 1],
              'foreground': [0, 0, 0], 'output': 2.44}
        )
        for test in contrast_test:
            with self.subTest(test['case']):
                self.assertAlmostEqual(calculate_contrast(test['background'],
                                                          test['foreground']),
                                       test['output'], places=2)

    def test_background_to_text(self):
        """
        Tests the function that determines the text colour
        """
        test_cases = (
             {'case': '1',
              'background': [[0, 0, 0]],
              'output': ['rgb(255,255,255)']},
             {'case': '2',
              'background': [[1, 1, 1]],
              'output': ['rgb(0,0,0)']},
             {'case': '3',
              'background': [[1, 0, 0]],
              'output': ['rgb(0,0,0)']},
             {'case': '4',
              'background': [[0, 1, 0]],
              'output': ['rgb(0,0,0)']},
             {'case': '4',
              'background': [[0, 0, 1]],
              'output': ['rgb(255,255,255)']},
             {'case': '5',
              'background': [[0, 0, 1],
                             [0, 1, 0],
                             [0, 0, 0]],
              'output': ['rgb(255,255,255)',
                         'rgb(0,0,0)',
                         'rgb(255,255,255)']}
        )
        for test in test_cases:
            with self.subTest(test['case']):
                self.assertCountEqual(background_to_text(test['background'],
                                                         7),
                                      test['output'])
