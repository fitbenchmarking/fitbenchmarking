"""
Tests for functions in the base tables file.
"""

import inspect
import os
from unittest import TestCase, mock

from fitbenchmarking import test_files
from fitbenchmarking.results_processing.base_table import Table
from fitbenchmarking.utils.checkpoint import get_checkpoint
from fitbenchmarking.utils.options import Options


def load_mock_results():
    """
    Load a predictable set of results.

    :return: Set of manually generated results
             The best results
    :rtype: dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]
            dict[str, dict[str, utils.fitbm_result.FittingResult]]
    """
    options = Options()
    cp_dir = os.path.dirname(inspect.getfile(test_files))
    options.checkpoint_filename = os.path.join(cp_dir, 'checkpoint.json')

    cp = get_checkpoint(options)
    results, _, _ = cp.load()

    grouped_results = {k: {'cf1': v} for k, v in results.items()}
    best_results = {'prob_0': {'cf1': results['prob_0'][0]},
                    'prob_1': {'cf1': results['prob_1'][0]}}
    return grouped_results, best_results


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
        results_list, best_results = load_mock_results()
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
        results, best_results = load_mock_results()
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
        results, best_results = load_mock_results()
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
