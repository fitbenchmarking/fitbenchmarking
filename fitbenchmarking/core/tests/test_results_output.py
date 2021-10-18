"""
Results output tests
"""

from __future__ import absolute_import, division, print_function

import os
import shutil
import unittest
from tempfile import TemporaryDirectory
from unittest import mock

import numpy as np

from fitbenchmarking.core.results_output import (create_directories,
                                                 create_plots,
                                                 create_problem_level_index,
                                                 preprocess_data, save_results)
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


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


def generate_mock_results(results_directory: str):
    """
    Generates results to test against

    :return: best results calculated using the chi_sq value, list of results
             and the options
    :rtype: tuple(list of best results,
                  list of list fitting results,
                  Options object)
    """
    software = 'scipy_ls'
    options = Options(results_directory=results_directory)
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
    min_chi_sq = [1, 3]
    acc_in = [[1, 5, 2, 1.54],
              [7, 3, 5, 1]]
    min_runtime = [4.2e-5, 5.0e-14]
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
            cost_func = NLLSCostFunc(p)
            jac = Scipy(cost_func)
            jac.method = '2-point'
            r = FittingResult(options=options,
                              cost_func=cost_func,
                              jac=jac,
                              hess=None,
                              initial_params=starting_values,
                              params=params_in[i][j],
                              name=p.name,
                              chi_sq=acc_in[i][j],
                              runtime=runtime_in[i][j],
                              software=software,
                              minimizer=options.minimizers[software][j],
                              error_flag=error_in[i][j],)
            r.support_page_link = link_in[i][j]
            results.append(r)
            options.minimizer_alg_type[options.minimizers[software]
                                       [j]] = 'all, ls'
        results_out.extend(results)
    return results_out, options, min_chi_sq, min_runtime


class SaveResultsTests(unittest.TestCase):
    """
    Unit tests for save_results function
    """

    def setUp(self):
        """
        Setting up paths and results folders
        """
        self.results_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'fitbenchmarking_results')
        self.results, self.options, self.min_chi_sq, self.min_runtime = \
            generate_mock_results(self.results_dir)
        os.mkdir(self.results_dir)

    def tearDown(self):
        """
        Clean up created folders.
        """
        shutil.rmtree(self.results_dir)

    def test_save_results_correct(self):
        """
        Tests to check the group_dir is correct
        """
        failed_problems = []
        unselected_minimizers = {}
        group_name = "group_name"
        group_dir = save_results(self.options, self.results, group_name,
                                 failed_problems, unselected_minimizers)
        assert group_dir == os.path.join(self.results_dir, group_name)


class CreateDirectoriesTests(unittest.TestCase):
    """
    Unit tests for create_directories function
    """

    def setUp(self):
        """
        Setting up paths and results folders
        """
        test_path = os.path.dirname(os.path.realpath(__file__))
        self.results_dir = os.path.join(test_path, 'fitbenchmarking_results')
        self.options = Options(results_directory=self.results_dir)
        os.mkdir(self.results_dir)

    def tearDown(self):
        """
        Clean up created folders.
        """
        shutil.rmtree(self.results_dir)

    def test_create_dirs_correct(self):
        """
        Test to check that the directories are correctly made.
        """
        group_name = 'test_group'
        expected_results_dir = self.results_dir
        expected_group_dir = os.path.join(expected_results_dir, group_name)
        expected_support_dir = os.path.join(expected_group_dir,
                                            'support_pages')
        expected_figures_dir = os.path.join(expected_support_dir, 'figures')
        expected_css_dir = os.path.join(expected_results_dir, 'css')

        group_dir, support_dir, figures_dir, css_dir = \
            create_directories(self.options, group_name)

        assert group_dir == expected_group_dir
        assert support_dir == expected_support_dir
        assert figures_dir == expected_figures_dir
        assert css_dir == expected_css_dir

        assert os.path.isdir(group_dir)
        assert os.path.isdir(support_dir)
        assert os.path.isdir(figures_dir)
        assert os.path.isdir(css_dir)


class PreprocessDataTests(unittest.TestCase):
    """
    Unit tests for preproccess_data function
    """

    def setUp(self):
        """
        Setting up paths and results folders
        """
        self.results_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'fitbenchmarking_results')
        self.results, self.options, self.min_chi_sq, self.min_runtime = \
            generate_mock_results(self.results_dir)

    def test_preprocess_data(self):
        """
        Test for preprocess_data function
        """
        best_result, results = preprocess_data(self.results)

        for category in best_result.values():
            for result in category.values():
                assert result.is_best_fit

        for problem, chi_sq, runtime in zip(results.values(),
                                            self.min_chi_sq,
                                            self.min_runtime):
            for category in problem.values():
                for r in category:
                    print("chi_sq  = {} | {}".format(r.min_chi_sq, chi_sq))
                    print("runtime = {} | {}".format(r.runtime, runtime))
                    assert r.min_chi_sq == chi_sq
                    assert r.min_runtime == runtime


class CreatePlotsTests(unittest.TestCase):
    """
    Unit tests for create_plots function
    """

    def setUp(self):
        """
        Setting up paths and results folders
        """
        self.tempdir = TemporaryDirectory()
        self.results_dir = os.path.join(self.tempdir.name, 'figures_dir')
        results, self.options, self.min_chi_sq, self.min_runtime = \
            generate_mock_results(self.results_dir)
        self.best_results, self.results = preprocess_data(results)

    @mock.patch('fitbenchmarking.results_processing.plots.Plot')
    def test_create_plots_with_params(self, plot_mock):
        """
        Tests for create_plots where the results object params are not None
        """
        expected_plot_initial_guess = "initial_guess"
        expected_plot_best = "plot_best"
        expected_plot_fit = "plot_fit"
        plot_instance = mock.MagicMock()
        plot_instance.plot_initial_guess.return_value = \
            expected_plot_initial_guess
        plot_instance.plot_best.return_value = expected_plot_best
        plot_instance.plot_fit.return_value = expected_plot_fit

        # Return the above created `plot_instance`
        plot_mock.return_value = plot_instance
        create_plots(self.options, self.results,
                     self.best_results, self.results_dir)
        for problem_key in self.results.keys():
            best_in_prob = self.best_results[problem_key]
            results_in_prob = self.results[problem_key]
            for category_key in results_in_prob.keys():
                best_in_cat = best_in_prob[category_key]
                results = results_in_prob[category_key]

                # Check initial guess is correctly set in results
                self.assertEqual(best_in_cat.start_figure_link,
                                 expected_plot_initial_guess)
                self.assertTrue(all(
                    r.start_figure_link == expected_plot_initial_guess
                    for r in results))

                # Check plot is correctly set in results
                self.assertEqual(best_in_cat.figure_link,
                                 expected_plot_best)
                self.assertTrue(all(
                    r.figure_link == expected_plot_fit
                    for r in results if not r.is_best_fit))

    @mock.patch('fitbenchmarking.results_processing.plots.Plot')
    def test_create_plots_without_params(self, plot_mock):
        """
        Tests for create_plots where the results object params are None
        """
        for problem_key in self.results.keys():
            best_in_prob = self.best_results[problem_key]
            results_in_prob = self.results[problem_key]
            for category_key in results_in_prob.keys():
                best_in_cat = best_in_prob[category_key]
                results = results_in_prob[category_key]
                best_in_cat.params = None
                for r in results:
                    r.params = None

        expected_plot_initial_guess = "initial_guess"
        plot_instance = mock.MagicMock()
        plot_instance.plot_initial_guess.return_value = \
            expected_plot_initial_guess
        # Return the above created `plot_instance`
        plot_mock.return_value = plot_instance
        create_plots(self.options, self.results,
                     self.best_results, self.results_dir)

        for problem_key in self.results.keys():
            best_in_prob = self.best_results[problem_key]
            results_in_prob = self.results[problem_key]
            for category_key in results_in_prob.keys():
                best_in_cat = best_in_prob[category_key]
                results = results_in_prob[category_key]

                # Check initial guess is correctly set in results
                self.assertEqual(best_in_cat.start_figure_link,
                                 expected_plot_initial_guess)
                self.assertTrue(all(
                    r.start_figure_link == expected_plot_initial_guess
                    for r in results))

                # Check plot is correctly set in results
                self.assertEqual(best_in_cat.figure_link, '')
                self.assertTrue(all(r.figure_link == ''
                                    for r in results if not r.is_best_fit))

                # Checks that when no params are given the correct error
                # message is produced
                expected_message = "Minimizer failed to produce any parameters"
                self.assertEqual(best_in_cat.figure_error, expected_message)
                self.assertTrue(all(r.figure_error == expected_message
                                    for r in results if not r.is_best_fit))

    def test_plot_error(self):
        """
        Test that errors are passed correctly when the plotting fails.
        """
        with mock.patch(
                'fitbenchmarking.results_processing.plots.Plot',
                side_effect=PlottingError('Faked plot')):

            create_plots(self.options, self.results,
                         self.best_results, self.results_dir)

        expected = 'An error occurred during plotting.\nDetails: Faked plot'

        for problem_key in self.results.keys():
            best_in_prob = self.best_results[problem_key]
            results_in_prob = self.results[problem_key]
            for category_key in results_in_prob.keys():
                best_in_cat = best_in_prob[category_key]
                results = results_in_prob[category_key]
                self.assertEqual(best_in_cat.figure_error, expected)
                for r in results:
                    self.assertEqual(r.figure_error, expected)


class CreateProblemLevelIndex(unittest.TestCase):
    """
   Unit tests for create_problem_level_index function
   """

    def setUp(self):
        """
        Setting up paths and results folders
        """
        self.options = Options()
        test_path = os.path.dirname(os.path.realpath(__file__))
        self.group_dir = os.path.join(test_path, 'fitbenchmarking_results')
        os.mkdir(self.group_dir)
        self.table_names = {"compare": "compare_table_name.",
                            "runtime": "runtime_table_name."}
        self.table_descriptions = {"compare": "compare table descriptions",
                                   "runtime": "runtime table descriptions",
                                   "both": "both table descriptions"}
        self.group_name = "random_name"

    def tearDown(self):
        """
        Clean up created folders.
        """
        shutil.rmtree(self.group_dir)

    def test_creation_index_page(self):
        """
        Tests to see that the index page are correctly created
        """
        create_problem_level_index(self.options, self.table_names,
                                   self.group_name, self.group_dir,
                                   self.table_descriptions)
        expected_file = os.path.join(self.group_dir,
                                     '{}_index.html'.format(self.group_name))
        assert os.path.isfile(expected_file)


if __name__ == "__main__":
    unittest.main()
