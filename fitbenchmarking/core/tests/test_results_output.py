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

from fitbenchmarking.core.results_output import (_extract_tags,
                                                 _find_matching_tags,
                                                 _process_best_results,
                                                 create_directories,
                                                 create_plots,
                                                 create_problem_level_index,
                                                 preprocess_data, save_results)
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options
from fitbenchmarking.controllers.scipy_controller import ScipyController


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
    return x1 * np.sin(x2) * data


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
    return x1 * x2 * data


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
            controller = ScipyController(cf)
            for k, software in enumerate(softwares):
                controller.software = software
                for m, minim in enumerate(minimizers[k]):
                    controller.minimizer = minim
                    jacs = jacobians[i] if minim != 's1m2' else [None]
                    for n, jac in enumerate(jacs):
                        controller.flag = None if jac is not None else 4
                        cf.jacobian = jac
                        minim_name = f'{minim}, Jac: {n}'
                        options.minimizer_alg_type[minim_name] = 'test'
                        controller.final_params = params[i][j][k][m][n],
                        results.append(FittingResult(
                            options=options,
                            controller=controller,
                            accuracy=acc[i][j][k][m][n],
                            runtime=runtime[i][j][k][m][n]))

    return results, options


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
        self.results, self.options = generate_mock_results(
            {'results_dir': self.results_dir})
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
        self.assertEqual(group_dir, os.path.join(self.results_dir, group_name))


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
        self.options = Options(additional_options={
                               'results_dir': self.results_dir})
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

        group_dir, support_dir, figures_dir = \
            create_directories(self.options, group_name)

        self.assertEqual(group_dir, expected_group_dir)
        self.assertEqual(support_dir, expected_support_dir)
        self.assertEqual(figures_dir, expected_figures_dir)

        self.assertTrue(os.path.isdir(group_dir))
        self.assertTrue(os.path.isdir(support_dir))
        self.assertTrue(os.path.isdir(figures_dir))


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
        self.results, self.options = generate_mock_results(
            {'results_dir': self.results_dir})
        self.min_chi_sq = 0.1
        self.min_runtime = 0.1

    def test_preprocess_data(self):
        """
        Test for preprocess_data function
        """
        best_result, results = preprocess_data(self.results)

        for category in best_result.values():
            for result in category.values():
                self.assertTrue(result.is_best_fit)

        for problem in results.values():
            for category in problem.values():
                for r in category:
                    self.assertEqual(r.min_chi_sq, self.min_chi_sq)
                    self.assertEqual(r.min_runtime, self.min_runtime)


class CreatePlotsTests(unittest.TestCase):
    """
    Unit tests for create_plots function
    """

    def setUp(self):
        """
        Setting up paths and results folders
        """
        with TemporaryDirectory() as directory:
            self.results_dir = os.path.join(directory, 'figures_dir')

            results, self.options = generate_mock_results(self.results_dir)
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
        self.assertTrue(os.path.isfile(expected_file))


class ExtractTagsTests(unittest.TestCase):
    """
    Tests for the _extract_tags function
    """

    def setUp(self):
        """
        Setup function for extract tags tests.
        """
        with TemporaryDirectory() as directory:
            self.results_dir = os.path.join(directory, 'figures_dir')
            results, self.options = generate_mock_results(self.results_dir)
            self.result = results[0]
            self.result.costfun_tag = 'cf0'
            self.result.problem_tag = 'p0'
            self.result.software_tag = 's0'
            self.result.minimizer_tag = 'm0'
            self.result.jacobian_tag = 'j0'
            self.result.hessian_tag = 'h0'
            self.result.error_flag = 0

    def test_correct_tags(self):
        """
        Test that for a general result, the tags are correctly populated.
        """
        tags = _extract_tags(self.result,
                             row_sorting=['costfun', 'problem'],
                             col_sorting=['jacobian', 'hessian'],
                             cat_sorting=['software', 'minimizer'])

        self.assertDictEqual(tags, {'row': 'cf0:p0',
                                    'col': 'j0:h0',
                                    'cat': 's0:m0'})

    def test_correct_tags_error_flag_4(self):
        """
        Test that the tags are correct for a fitting function which
        is missing jacobian and hessian information.
        """
        self.result.error_flag = 4
        tags = _extract_tags(self.result,
                             row_sorting=['jacobian', 'problem'],
                             col_sorting=['hessian'],
                             cat_sorting=['costfun', 'software', 'minimizer'])

        self.assertDictEqual(tags, {'row': '[^:]*:p0',
                                    'col': '[^:]*',
                                    'cat': 'cf0:s0:m0'})


class FindMatchingTagsTests(unittest.TestCase):
    """
    Tests for the _find_matching_tags function.
    """

    def test_matching_tags_included(self):
        """
        Test that the matching tags include all correct tags.
        """
        matching = _find_matching_tags('cf0:[^:]*:p0', ['cf0:j0:p0',
                                                        'cf0:j0:p1',
                                                        'cf0:j1:p0',
                                                        'cf0:j1:p1',
                                                        'cf1:j0:p0',
                                                        'cf1:j0:p1',
                                                        'cf1:j1:p0',
                                                        'cf1:j1:p1'])
        self.assertIn('cf0:j0:p0', matching)
        self.assertIn('cf0:j1:p0', matching)

    def test_non_matching_tags_excluded(self):
        """
        Test that all tags that don't match are excluded.
        """
        matching = _find_matching_tags('cf0:[^:]*:p0', ['cf0:j0:p0',
                                                        'cf0:j1:p0',
                                                        'cf1:j0:p0',
                                                        'cf1:j1:p0'])
        self.assertNotIn('cf1:j0:p0', matching)
        self.assertNotIn('cf1:j1:p0', matching)


class ProcessBestResultsTests(unittest.TestCase):
    """
    Tests for the _process_best_results function.
    """

    def setUp(self):
        """
        Setup function for _process_best_results tests.
        """
        with TemporaryDirectory() as directory:
            self.results_dir = os.path.join(directory, 'figures_dir')
            results, self.options = generate_mock_results(self.results_dir)
            self.results = results[:5]
            for r, accuracy, runtime in zip(self.results,
                                         [2, 1, 5, 3, 4],
                                         [5, 4, 1, 2, 3]):
                r.accuracy = accuracy
                r.runtime = runtime
            self.best = _process_best_results(self.results)

    def test_returns_best_result(self):
        """
        Test that the best result is returned.
        """
        self.assertIs(self.best, self.results[1])

    def test_is_best_fit_True(self):
        """
        Test that the is_best_fit flag is set on the correct result.
        """
        self.assertTrue(self.best.is_best_fit)

    def test_is_best_fit_False(self):
        """
        Test that is_best_fit is not set on other results.
        """
        self.assertFalse(self.results[0].is_best_fit)
        self.assertFalse(self.results[2].is_best_fit)
        self.assertFalse(self.results[3].is_best_fit)
        self.assertFalse(self.results[4].is_best_fit)

    def test_minimum_accuracy_set(self):
        """
        Test that min_accuracy is set correctly.
        """
        self.assertEqual(self.results[0].min_accuracy, self.best.accuracy)
        self.assertEqual(self.results[1].min_accuracy, self.best.accuracy)
        self.assertEqual(self.results[2].min_accuracy, self.best.accuracy)
        self.assertEqual(self.results[3].min_accuracy, self.best.accuracy)
        self.assertEqual(self.results[4].min_accuracy, self.best.accuracy)

    def test_minimum_runtime_set(self):
        """
        Test that min_runtime is set correctly.
        """
        fastest = self.results[2]
        self.assertEqual(self.results[0].min_runtime, fastest.runtime)
        self.assertEqual(self.results[1].min_runtime, fastest.runtime)
        self.assertEqual(self.results[2].min_runtime, fastest.runtime)
        self.assertEqual(self.results[3].min_runtime, fastest.runtime)
        self.assertEqual(self.results[4].min_runtime, fastest.runtime)


if __name__ == "__main__":
    unittest.main()
