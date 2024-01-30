"""
Results output tests
"""


import inspect
import os
import shutil
import unittest
from tempfile import TemporaryDirectory
from unittest import mock

import pandas as pd
from dash import dcc, html

from fitbenchmarking import test_files
from fitbenchmarking.core.results_output import (_extract_tags,
                                                 _find_matching_tags,
                                                 _process_best_results,
                                                 check_max_solvers,
                                                 create_directories,
                                                 create_plots,
                                                 create_problem_level_index,
                                                 display_page,
                                                 preprocess_data,
                                                 save_results,
                                                 update_warning)

from fitbenchmarking.results_processing.performance_profiler import \
    DashPerfProfile
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.options import Options


def load_mock_results(additional_options=None, filename='checkpoint.json'):
    """
    Load a predictable set of results.

    :return: Set of manually generated results
             The best results
    :rtype: list[FittingResult],
            Options
    """
    if additional_options is None:
        additional_options = {}
    cp_dir = os.path.dirname(inspect.getfile(test_files))
    additional_options.update({
        'checkpoint_filename': os.path.join(cp_dir, filename),
        'external_output': 'debug'})
    options = Options(additional_options=additional_options)
    cp = Checkpoint(options)
    results, _, _ = cp.load()

    return results['Fake_Test_Data'], options


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
        self.results, self.options = load_mock_results(
            {'results_dir': self.results_dir})
        os.mkdir(self.results_dir)

    def tearDown(self):
        """
        Clean up created folders.
        """
        shutil.rmtree(self.results_dir)

    def test_save_results_correct_output_path(self):
        """
        Tests to check the group_dir is correct
        """
        failed_problems = []
        unselected_minimizers = {}
        group_name = "group_name"
        group_dir, _ = save_results(self.options, self.results,
                                    group_name, failed_problems,
                                    unselected_minimizers)
        self.assertEqual(group_dir, os.path.join(self.results_dir, group_name))

    def test_save_results_correct_output_dict_format(self):
        """
        Test to check save_results returns a dict of pandas dataframes.
        """
        failed_problems = []
        unselected_minimizers = {}
        group_name = "group_name"
        _, pp_dfs = save_results(self.options, self.results,
                                 group_name, failed_problems,
                                 unselected_minimizers)

        assert isinstance(pp_dfs, dict)
        for df in list(pp_dfs.values()):
            assert isinstance(df, pd.DataFrame)
            assert not df.empty


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
        self.results, self.options = load_mock_results(
            {'results_dir': self.results_dir})
        self.min_accuracy = 0.2
        self.min_runtime = 1.0

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
                    self.assertEqual(r.min_accuracy, self.min_accuracy)
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

            results, self.options = load_mock_results(
                {'results_dir': self.results_dir})
            self.best_results, self.results = preprocess_data(results)

    @mock.patch('fitbenchmarking.results_processing.plots.Plot')
    def test_create_plots_with_params(self, plot_mock):
        """
        Tests for create_plots where the results object params are not None
        """
        expected_plot_initial_guess = "initial_guess"
        expected_plot_best = {'prob_0': "plotly_fit4",
                              'prob_1': "plotly_fit3"}
        expected_plotly_fit = {'m00_[s0]': "plotly_fit1",
                               'm01_[s0]_jj0': "plotly_fit2",
                               'm01_[s0]_jj1': "plotly_fit3",
                               'm10_[s1]_jj0': "plotly_fit4",
                               'm10_[s1]_jj1': "plotly_fit5",
                               'm11_[s1]_jj0': "plotly_fit6",
                               'm11_[s1]_jj1': "plotly_fit7",
                               'm00_[s0]_jj0': "plotly_fit8",
                               'm00_[s0]_jj1': "plotly_fit9"}
        plot_instance = mock.MagicMock()
        plot_instance.plot_initial_guess.return_value = \
            expected_plot_initial_guess
        plot_instance.plot_best.return_value = expected_plot_best
        plot_instance.plotly_fit.return_value = expected_plotly_fit

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
                                 expected_plot_best[problem_key])
                self.assertTrue(all(
                    r.figure_link == expected_plotly_fit[
                        r.sanitised_min_name(True)]
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
                                     f'{self.group_name}_index.html')
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
            results, self.options = load_mock_results(
                {'results_dir': self.results_dir})
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
            results, self.options = load_mock_results(
                {'results_dir': self.results_dir})
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


class UpdateWarningTests(unittest.TestCase):
    """
    Tests for the update_warning function.
    """

    def setUp(self):
        """
        Setup function for update_warning tests.
        """
        self.max_solvers = 15

    def test_warning_when_few_solvers(self):
        """
        Test that an empty string is returned when the number of
        solvers is less than the maximum allowed.
        """
        solvers = [f'Solver {i}' for i in range(3)]
        output = update_warning(solvers, self.max_solvers)
        expected_output = ''
        self.assertEqual(output, expected_output)

    def test_warning_when_too_many_solvers(self):
        """
        Test that the expected warning is returned when the number of
        solvers exceeds the maximum allowed.
        """
        solvers = [f'Solver {i}' for i in range(20)]
        output = update_warning(solvers, self.max_solvers)
        expected_output = 'The plot is showing the max number ' \
                          f'of minimizers allowed ({self.max_solvers}). '\
                          'Deselect some to select others.'
        self.assertEqual(output, expected_output)


class CheckMaxSolversTests(unittest.TestCase):
    """
    Tests for the check_max_solvers function.
    """

    def setUp(self):
        """
        Setup function for check_max_solvers tests.
        """
        self.max_solvers = 4

    def test_opts_disabled_when_many_solvers(self):
        """
        Test that options displayed in the dropdown are disabled when
        the number of solvers exceeds the maximum allowed.
        """
        solvers = [f'solver{i}' for i in range(5)]
        input_opts = [{"value": solver, "label": solver}
                      for solver in solvers]

        expec_output = [{'value': 'solver0', 'label': 'solver0',
                         'disabled': True},
                        {'value': 'solver1', 'label': 'solver1',
                         'disabled': True},
                        {'value': 'solver2', 'label': 'solver2',
                         'disabled': True},
                        {'value': 'solver3', 'label': 'solver3',
                         'disabled': True},
                        {'value': 'solver4', 'label': 'solver4',
                         'disabled': True}]

        output = check_max_solvers(input_opts, solvers, self.max_solvers)
        self.assertEqual(output, expec_output)

    def test_opts_enabled_when_low_solvers(self):
        """
        Test that options displayed in the dropdown are enabled when
        the number of solvers is less than the maximum allowed.
        """
        solvers = [f'solver{i}' for i in range(3)]
        input_opts = [{"value": solver, "label": solver}
                      for solver in solvers]

        expec_output = [{'value': 'solver0', 'label': 'solver0',
                         'disabled': False},
                        {'value': 'solver1', 'label': 'solver1',
                         'disabled': False},
                        {'value': 'solver2', 'label': 'solver2',
                         'disabled': False}]

        output = check_max_solvers(input_opts, solvers, self.max_solvers)
        self.assertEqual(output, expec_output)


class DisplayPageTests(unittest.TestCase):
    """
    Tests for the display_page function.
    """

    def setUp(self):
        """
        Setup function for display_page tests.
        """
        self.max_solvers = 4
        group = "NIST_low_difficulty"

        pp_df = pd.DataFrame.from_dict({
            'solver': ['solver1', 'solver1', 'solver1',
                       'solver2', 'solver2', 'solver2'],
            'x': [20.0, 30.5, 41.0, 10.0, 50.5, 70.0],
            'y': [0.0, 0.5, 1.0, 0.0, 0.5, 1.0]
        }, orient='columns')

        pp_dfs = {'acc': pp_df, 'runtime': pp_df}

        self.profile_instances_all_groups = {
            group: {
                'acc': DashPerfProfile(profile_name='Accuracy',
                                       pp_df=pp_dfs['acc'],
                                       group_label=group),
                'runtime': DashPerfProfile(profile_name='Runtime',
                                           pp_df=pp_dfs['runtime'],
                                           group_label=group)
            }
        }
        self.layout = [
            dcc.RadioItems(
                id="Log axis toggle",
                options=["Log x-axis", "Linear x-axis"],
                value="Log x-axis",
            ),
            dcc.Dropdown(
                id='dropdown',
                multi=True,
            ),
            html.Div(
                id='warning',
            ),
        ]

    def test_layout_returned_when_one_plot(self):
        """
        Test that the expected layout components are returned when the
        pathname refers to one plot only.
        """
        pathname = "127.0.0.1:5009/NIST_low_difficulty/pp/acc"
        output_div = display_page(pathname,
                                  self.profile_instances_all_groups,
                                  self.layout,
                                  self.max_solvers)
        output_ids = list(output_div)
        expected_ids = ['Log axis toggle', 'dropdown', 'warning',
                        'visual NIST_low_difficulty-Accuracy']
        self.assertEqual(output_ids, expected_ids)

    def test_layout_returned_when_two_plots(self):
        """
        Test that the expected layout components are returned when the
        pathname refers to two plots.
        """
        pathname = "127.0.0.1:5009/NIST_low_difficulty/pp/acc+runtime"
        output_div = display_page(pathname,
                                  self.profile_instances_all_groups,
                                  self.layout,
                                  self.max_solvers)
        output_ids = list(output_div)
        expected_ids = ['Log axis toggle', 'dropdown', 'warning',
                        'visual NIST_low_difficulty-Accuracy',
                        'visual NIST_low_difficulty-Runtime']
        self.assertEqual(output_ids, expected_ids)


if __name__ == "__main__":
    unittest.main()
