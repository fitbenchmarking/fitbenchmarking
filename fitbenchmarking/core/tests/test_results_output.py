"""
Results output tests
"""


import inspect
import os
import shutil
import unittest
from tempfile import TemporaryDirectory
from unittest import mock

from fitbenchmarking import test_files
from fitbenchmarking.core.results_output import (_extract_tags,
                                                 _find_matching_tags,
                                                 _process_best_results,
                                                 _find_columns_with_fallback,
                                                 _process_tags,
                                                 _handle_fallback_tags,
                                                 create_directories,
                                                 create_plots,
                                                 create_problem_level_index,
                                                 preprocess_data, save_results)
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.options import Options


def load_mock_results(additional_options=None):
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
        'checkpoint_filename': os.path.join(cp_dir,
                                            'checkpoint.json'),
        'external_output': 'debug'})
    options = Options(additional_options=additional_options)
    cp = Checkpoint(options)
    results, _, _ = cp.load()

    return results["Fake_Test_Data"], options


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


class FallbackTagTests(unittest.TestCase):
    """
    Unit tests for finding fallback tags that
    occur when there is a fallback on jacobian
    and hessians.
    """
    def setUp(self):
        """
        Setting up paths and results folders
        """
        # Loading the results from checkpoint.json
        self.results, _ = load_mock_results()

        self.sort_order = (['problem'],
                           ['software',
                            'minimizer',
                            'jacobian',
                            'hessian'])
        self.col_sections = ['costfun']

        # Defining the expected values for results in checkpoint.json
        self.expected_tags = [{'row': 'prob_0', 'col': 's1:m10:j0:',
                               'cat': 'cf1', 'result_ix': 0},
                              {'row': 'prob_0', 'col': 's1:m11:j0:',
                               'cat': 'cf1', 'result_ix': 1},
                              {'row': 'prob_0', 'col': 's0:m01:j0:',
                               'cat': 'cf1', 'result_ix': 2},
                              {'row': 'prob_0', 'col': 's1:m10:j1:',
                               'cat': 'cf1', 'result_ix': 4},
                              {'row': 'prob_0', 'col': 's1:m11:j1:',
                               'cat': 'cf1', 'result_ix': 5},
                              {'row': 'prob_0', 'col': 's0:m01:j1:',
                               'cat': 'cf1', 'result_ix': 6},
                              {'row': 'prob_1', 'col': 's1:m10:j0:',
                               'cat': 'cf1', 'result_ix': 7},
                              {'row': 'prob_1', 'col': 's1:m11:j0:',
                               'cat': 'cf1', 'result_ix': 8},
                              {'row': 'prob_1', 'col': 's0:m01:j0:',
                               'cat': 'cf1', 'result_ix': 9},
                              {'row': 'prob_1', 'col': 's0:m00:j0:',
                               'cat': 'cf1', 'result_ix': 10},
                              {'row': 'prob_1', 'col': 's1:m10:j1:',
                               'cat': 'cf1', 'result_ix': 11},
                              {'row': 'prob_1', 'col': 's1:m11:j1:',
                               'cat': 'cf1', 'result_ix': 12},
                              {'row': 'prob_1', 'col': 's0:m01:j1:',
                               'cat': 'cf1', 'result_ix': 13},
                              {'row': 'prob_1', 'col': 's0:m00:j1:',
                               'cat': 'cf1', 'result_ix': 14}]
        self.expected_repeating_tags = []

    def test_find_fallback_tags(self):
        """
        Test the find fallback tags function
        """
        results = self.results
        expected_tags = self.expected_tags
        expected_repeating_tags = self.expected_repeating_tags

        # Test Case 1
        # Using the results in checkpoint.json
        # No column with fallback
        self.run_and_match_find_fallback_tags(results,
                                              expected_tags,
                                              expected_repeating_tags)

        # Test Case 2
        # Updating the results in checkpoint.json
        # One column with fallback
        results[8].jacobian_tag = 'j1'
        expected_tags[7]['col'] = 's1:m11:j1:'
        expected_repeating_tags = ['s1:m11:j0:', 's1:m11:j1:']

        self.run_and_match_find_fallback_tags(results,
                                              expected_tags,
                                              expected_repeating_tags)

        # Test Case 3
        # Updating the results in checkpoint.json
        # Two column with fallback
        results[6].hessian_tag = 'h0'
        results[13].hessian_tag = 'h1'
        expected_tags[5]['col'] = 's0:m01:j1:h0'
        expected_tags[12]['col'] = 's0:m01:j1:h1'
        expected_repeating_tags = ['s1:m11:j0:',
                                   's1:m11:j1:',
                                   's0:m01:j1:h0',
                                   's0:m01:j1:h1']

        self.run_and_match_find_fallback_tags(results,
                                              expected_tags,
                                              expected_repeating_tags)

    def run_and_match_find_fallback_tags(self,
                                         results,
                                         expected_tags,
                                         expected_repeating_tags):
        """
        Helper function to call _find_columns_with_fallback
        and match outputs
        """
        actual_tags, actual_repeating_tags = \
            _find_columns_with_fallback(results,
                                        self.sort_order,
                                        self.col_sections)

        self.assertEqual(actual_tags, expected_tags)
        self.assertEqual(actual_repeating_tags, expected_repeating_tags)

    def run_and_match_process_fallback_tags(self,
                                            columns,
                                            expected_count,
                                            columns_with_errors,
                                            expected_column_tags):
        """
        Helper function to call _process_tags
        and match outputs
        """
        actual_column_tags = _process_tags(columns,
                                           expected_count,
                                           columns_with_errors)
        self.assertEqual(actual_column_tags, expected_column_tags)

    def test_process_fallback_tags(self):
        """
        Test the process fallback tags function
        """
        columns = {'s1:m10:j0:': 2,
                   's1:m11:j0:': 2,
                   's0:m01:j0:': 2,
                   's1:m10:j1:': 2,
                   's1:m11:j1:': 2,
                   's0:m01:j1:': 2,
                   's0:m00:j0:': 1,
                   's0:m00:j1:': 1}
        expected_count = 2
        columns_with_errors = {'s0:m00': 1}

        # Test Case 1
        # Using the results in checkpoint.json
        # No column with fallback
        # 1 Error result
        expected_column_tags = []
        self.run_and_match_process_fallback_tags(columns,
                                                 expected_count,
                                                 columns_with_errors,
                                                 expected_column_tags)

        # Test Case 2
        # Using the results in checkpoint.json
        # 1 column with fallback
        # 0 Error result
        columns_with_errors = {}
        columns['s0:m00:j0:'] = columns['s0:m00:j1:'] = 2
        expected_column_tags = []
        self.run_and_match_process_fallback_tags(columns,
                                                 expected_count,
                                                 columns_with_errors,
                                                 expected_column_tags)

        # Test Case 3
        # Using the results in checkpoint.json
        # 2 column with fallback
        # 0 Error result
        columns['s1:m11:j0:'] = columns['s1:m11:j1:'] = 1
        expected_column_tags = ['s1:m11:j0:', 's1:m11:j1:']
        self.run_and_match_process_fallback_tags(columns,
                                                 expected_count,
                                                 columns_with_errors,
                                                 expected_column_tags)

        # Test Case 4
        # Using the results in checkpoint.json
        # 2 column with fallback
        # 0 Error result
        columns['s1:m11:j0:h0'] = columns['s1:m11:j1:h1'] = 1
        expected_column_tags = ['s1:m11:j0:',
                                's1:m11:j1:',
                                's1:m11:j0:h0',
                                's1:m11:j1:h1']
        self.run_and_match_process_fallback_tags(columns,
                                                 expected_count,
                                                 columns_with_errors,
                                                 expected_column_tags)

    def test_handle_fallback_tags(self):
        """
        Test the handle fallback tags function
        """

        # Test Case 1
        # Using the results in checkpoint.json
        results = self.results
        expected_tags = self.expected_tags
        repeating_tags = []

        actual_results, actual_result_tags = \
            _handle_fallback_tags(results,
                                  expected_tags,
                                  repeating_tags)

        self.assertEqual(actual_results, results)
        self.assertEqual(actual_result_tags, expected_tags)

        # Test Case 2
        # Updating the results in checkpoint.json
        del results[14], results[10], results[3]
        del expected_tags[13], expected_tags[9]
        for ix in range(3, 12):
            expected_tags[ix]['result_ix'] = ix
        expected_tags[6]['col'] = 's1:m10:j1:'
        results[6].jacobian_tag = 'j1'

        repeating_tags = ['s1:m10:j0:', 's1:m10:j1:']

        actual_results, actual_result_tags = \
            _handle_fallback_tags(results,
                                  expected_tags,
                                  repeating_tags)

        for ix in [0, 3, 6, 9]:
            self.assertEqual(actual_result_tags[ix]['col'],
                             's1:m10:best_avaliable:')


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
            for r, accuracy, mean_runtime in zip(self.results,
                                                 [2, 1, 5, 3, 4],
                                                 [5, 4, 1, 2, 3]):
                r.accuracy = accuracy
                r.mean_runtime = mean_runtime
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
        self.assertEqual(self.results[0].min_runtime, fastest.mean_runtime)
        self.assertEqual(self.results[1].min_runtime, fastest.mean_runtime)
        self.assertEqual(self.results[2].min_runtime, fastest.mean_runtime)
        self.assertEqual(self.results[3].min_runtime, fastest.mean_runtime)
        self.assertEqual(self.results[4].min_runtime, fastest.mean_runtime)


if __name__ == "__main__":
    unittest.main()
