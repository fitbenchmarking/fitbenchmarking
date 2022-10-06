"""
Tests for the problem_summary_page python file.
"""

import os
from tempfile import TemporaryDirectory
from unittest import TestCase, main

import shutil
import numpy as np

from fitbenchmarking.core.results_output import preprocess_data
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.results_processing import problem_summary_page
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options

# pylint: disable=protected-access


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
    return x1 * np.sin(x2) * np.ones_like(data)


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
    return x1 * x2 * np.ones_like(data)


def generate_mock_results(additional_options):
    """
    Generates results to test against

    :return: list of results
             and the options
    :rtype: tuple(list of best results,
                  list of list fitting results,
                  Options object)
    """
    options = Options(additional_options=additional_options)
    options.table_type = ['acc']
    problems = [FittingProblem(options), FittingProblem(options)]
    starting_values = [{"a": .3, "b": .11}, {"a": 0, "b": 0}]
    data_x = np.array([[1, 4, 5], [2, 1, 5]])
    data_y = np.array([[1, 2, 1], [2, 2, 2]])
    data_e = np.array([[1, 1, 1], [1, 2, 1]])
    func = [fitting_function_1, fitting_function_2]
    for i, p in enumerate(problems):
        p.data_x = data_x[i]
        p.data_y = data_y[i]
        p.data_e = data_e[i]
        p.function = func[i]
        p.name = "prob_{}".format(i)
        p.starting_values = [starting_values[i]]

    softwares = ['s1', 's2']
    minimizers = [['s1m1', 's1m2'], ['s2m1', 's2m2']]
    jacobians = [['j1', 'j2'] for _ in problems]
    cost_funcs = [[NLLSCostFunc(p), WeightedNLLSCostFunc(p)]
                  for p in problems]

    # problem, cost fun, software, minimizer, jacobian
    acc = [[[[[0.5, 0.3], [10]], [[0.6, 0.2], [0.7, 0.1]]],  # p1, cf1
            [[[0.1, 0.9], [10]], [[0.2, 0.6], [0.8, 0.4]]]],  # p1, cf2
           [[[[0.9, 0.5], [10]], [[0.1, 0.3], [0.2, 0.6]]],  # p2, cf1
            [[[0.2, 0.1], [10]], [[0.5, 0.9], [0.4, 0.8]]]]]  # p2, cf2
    runtime = [[[[[0.7, 0.1], [10]], [[0.7, 0.2], [0.3, 0.8]]],  # p1, cf1
                [[[0.6, 0.9], [10]], [[0.2, 0.1], [0.8, 0.4]]]],  # p1, cf2
               [[[[0.9, 0.5], [10]], [[0.1, 0.3], [0.2, 0.6]]],  # p2, cf1
                [[[0.1, 0.8], [10]], [[0.5, 0.9], [0.4, 0.8]]]]]  # p2, cf2
    params = [[[[[[0.1, 0.5], [0.1, 0.3]],  # p1, cf1, s1, m1
                 [[10, 10]]],  # p1, cf1, s1, m2
                [[[0.1, 0.6], [0.1, 0.2]],  # p1, cf1, s2, m1
                 [[0.1, 0.7], [0.1, 0.1]]]],  # p1, cf1, s2, m2
               [[[[0.1, 0.1], [0.1, 0.9]],  # p1, cf2, s1, m1
                 [[10, 10]]],  # p1, cf2, s1, m2
                [[[0.1, 0.2], [0.1, 0.6]],  # p1, cf2, s2, m1
                 [[0.1, 0.8], [0.1, 0.4]]]]],  # p1, cf2, s2, m2
              [[[[[0.1, 0.9], [0.1, 0.5]],  # p2, cf1, s1, m1
                 [[10, 10]]],  # p2, cf1, s1, m2
                [[[0.1, 0.1], [0.1, 0.3]],  # p2, cf1, s2, m1
                 [[0.1, 0.2], [0.1, 0.6]]]],  # p2, cf1, s2, m2
               [[[[0.1, 0.2], [0.1, 0.1]],  # p2, cf2, s1, m1
                 [[10, 10]]],  # p2, cf2, s1, m2
                [[[0.1, 0.5], [0.1, 0.9]],  # p2, cf2, s2, m1
                 [[0.1, 0.4], [0.1, 0.8]]]]]]  # p2, cf2, s2, m2

    results = []
    for i, _ in enumerate(problems):
        for j, cf in enumerate(cost_funcs[i]):
            for k, software in enumerate(softwares):
                for m, minim in enumerate(minimizers[k]):
                    jacs = jacobians[i] if minim != 's1m2' else [None]
                    for n, jac in enumerate(jacs):
                        results.append(FittingResult(
                            options=options,
                            cost_func=cf,
                            jac=jac,
                            hess=None,
                            initial_params=list(
                                cf.problem.starting_values[0].values()),
                            params=params[i][j][k][m][n],
                            chi_sq=acc[i][j][k][m][n],
                            runtime=runtime[i][j][k][m][n],
                            software=software,
                            minimizer=minim,
                            error_flag=None if jac is not None else 4
                        ))

    return results, options


class CreateTests(TestCase):
    """
    Tests for the create function.
    """

    def setUp(self):
        """
        Setup for create function tests
        """
        with TemporaryDirectory() as directory:
            self.temp_dir = directory
            self.supp_dir = os.path.join(self.temp_dir, 'support_pages')
            self.fig_dir = os.path.join(self.supp_dir, 'figures')
        os.makedirs(self.fig_dir)
        results, self.options = generate_mock_results(
            {'results_dir': self.temp_dir})
        self.best_results, self.results = preprocess_data(results)

    def tearDown(self) -> None:
        """
        Tear down the test suite.
        """
        shutil.rmtree(self.temp_dir)

    def test_create_all_plots(self):
        """
        Check that a plot is created for each result set.
        """
        self.options.make_plots = True
        problem_summary_page.create(results=self.results,
                                    best_results=self.best_results,
                                    support_pages_dir=self.supp_dir,
                                    figures_dir=self.fig_dir,
                                    options=self.options)
        for k in self.results:
            expected_path = os.path.join(self.fig_dir,
                                         f'summary_plot_for_{k}.png')
            self.assertTrue(os.path.exists(expected_path))

    def test_create_no_plots(self):
        """
        Check that no plots are created if the option is off.
        """
        self.options.make_plots = False
        problem_summary_page.create(results=self.results,
                                    best_results=self.best_results,
                                    support_pages_dir=self.supp_dir,
                                    figures_dir=self.fig_dir,
                                    options=self.options)
        for k in self.results.keys():
            expected_path = os.path.join(self.fig_dir,
                                         f'summary_plot_for_{k}.png')
            self.assertFalse(os.path.exists(expected_path))

    def test_create_all_summary_pages(self):
        """
        Check that a summary page is created for each result set.
        """
        self.options.make_plots = False
        problem_summary_page.create(results=self.results,
                                    best_results=self.best_results,
                                    support_pages_dir=self.supp_dir,
                                    figures_dir=self.fig_dir,
                                    options=self.options)
        for v in self.best_results.values():
            example_result = list(v.values())[0]
            self.assertTrue(os.path.exists(
                example_result.problem_summary_page_link))


class CreateSummaryPageTests(TestCase):
    """
    Tests for the _create_summary_page function.
    """

    def setUp(self):
        """
        Setup tests for _create_summary_page
        """
        with TemporaryDirectory() as directory:
            self.temp_dir = directory
            self.supp_dir = os.path.join(self.temp_dir, 'support_pages')

        os.makedirs(self.supp_dir)
        results, self.options = generate_mock_results(
            {'results_dir': self.temp_dir})

        best_results, results = preprocess_data(results)
        self.prob_name = list(results.keys())[0]
        self.results = results[self.prob_name]
        self.best_results = best_results[self.prob_name]
        cat_results = [(cf, r, 'Some text')
                       for cf, r in self.best_results.items()]
        problem_summary_page._create_summary_page(
            categorised_best_results=cat_results,
            summary_plot_path='plot_path',
            support_pages_dir=self.supp_dir,
            options=self.options)

    def tearDown(self) -> None:
        """
        Tear down the test suite.
        """
        shutil.rmtree(self.temp_dir)

    def test_create_summary_pages(self):
        """
        Check that a summary page is created for a problem set.
        """
        expected_path = os.path.join(self.supp_dir,
                                     f'{self.prob_name}_summary.html')
        self.assertTrue(os.path.exists(expected_path))

    def test_set_link_attribute(self):
        """
        Check that all results have a summary page added to the
        'problem_summary_page_link' attribute.
        """
        for result in self.best_results.values():
            self.assertNotEqual(result.problem_summary_page_link, '')


class GetFigurePathsTests(TestCase):
    """
    Tests the very simple get_figure_paths function
    """

    def setUp(self):
        self.options = Options()
        problem = FittingProblem(self.options)
        problem.name = 'prob a'
        problem.equation = 'equation!'
        problem.starting_values = [{'x': 1}]
        cost_func = NLLSCostFunc(problem)
        jac = 'j1'
        self.result = FittingResult(options=self.options,
                                    cost_func=cost_func,
                                    jac=jac,
                                    hess=None,
                                    initial_params=[],
                                    params=[],
                                    minimizer='test')

    def test_with_links(self):
        """
        Tests that the returned links are correct when links are passed in.
        """
        self.result.figure_link = 'some_link'
        self.result.start_figure_link = 'other_link'
        # pylint: disable=protected-access
        figure_link, start_link = problem_summary_page._get_figure_paths(
            self.result)
        self.assertEqual(figure_link, os.path.join('figures', 'some_link'))
        self.assertEqual(start_link, os.path.join('figures', 'other_link'))

    def test_no_links(self):
        """
        Tests that links are not changed if an empty string is given.
        """
        self.result.figure_link = ''
        self.result.start_figure_link = ''
        # pylint: disable=protected-access
        figure_link, start_link = problem_summary_page._get_figure_paths(
            self.result)
        self.assertEqual(figure_link, '')
        self.assertEqual(start_link, '')


if __name__ == "__main__":
    main()
