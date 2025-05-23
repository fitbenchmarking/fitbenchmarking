"""
Tests for the problem_summary_page python file.
"""

import inspect
import os
import shutil
from tempfile import TemporaryDirectory
from unittest import TestCase, main

from fitbenchmarking import test_files
from fitbenchmarking.core.results_output import preprocess_data
from fitbenchmarking.results_processing import problem_summary_page
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.options import Options


def load_mock_results(additional_options=None):
    """
    Load a predictable results set.

    :param additional_options: Extra options to pass to options init
    :type additional_options: dict
    :return: Manually generated results
    :rtype: list[FittingResult]
    """
    options = Options(additional_options=additional_options)
    cp_dir = os.path.dirname(inspect.getfile(test_files))
    options.checkpoint_filename = os.path.join(cp_dir, "checkpoint.json")

    cp = Checkpoint(options)
    results, _, _, _ = cp.load()

    return results["Fake_Test_Data"], options


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
            self.supp_dir = os.path.join(self.temp_dir, "support_pages")
            self.fig_dir = os.path.join(self.supp_dir, "figures")
        os.makedirs(self.fig_dir)
        results, self.options = load_mock_results(
            {"results_dir": self.temp_dir}
        )
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
        problem_summary_page.create(
            results=self.results,
            best_results=self.best_results,
            support_pages_dir=self.supp_dir,
            figures_dir=self.fig_dir,
            options=self.options,
        )
        for k in self.results:
            expected_path = os.path.join(
                self.fig_dir, f"summary_plot_for_{k}.html"
            )
            self.assertTrue(os.path.exists(expected_path))

    def test_create_no_plots(self):
        """
        Check that no plots are created if the option is off.
        """
        self.options.make_plots = False
        problem_summary_page.create(
            results=self.results,
            best_results=self.best_results,
            support_pages_dir=self.supp_dir,
            figures_dir=self.fig_dir,
            options=self.options,
        )
        for k in self.results:
            expected_path = os.path.join(
                self.fig_dir, f"summary_plot_for_{k}.png"
            )
            self.assertFalse(os.path.exists(expected_path))

    def test_create_all_summary_pages(self):
        """
        Check that a summary page is created for each result set.
        """
        self.options.make_plots = False
        problem_summary_page.create(
            results=self.results,
            best_results=self.best_results,
            support_pages_dir=self.supp_dir,
            figures_dir=self.fig_dir,
            options=self.options,
        )
        for v in self.best_results.values():
            example_result = list(v.values())[0]
            self.assertTrue(
                os.path.exists(example_result.problem_summary_page_link)
            )


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
            self.supp_dir = os.path.join(self.temp_dir, "support_pages")

        os.makedirs(self.supp_dir)
        results, self.options = load_mock_results(
            {"results_dir": self.temp_dir}
        )

        best_results, results = preprocess_data(results)
        self.prob_name = list(results.keys())[0]
        self.results = results[self.prob_name]
        self.best_results = best_results[self.prob_name]
        cat_results = [
            (cf, r, "Some text") for cf, r in self.best_results.items()
        ]
        problem_summary_page._create_summary_page(
            categorised_best_results=cat_results,
            plot_2d_data_path="2d_plots_path",
            summary_plot_path="plot_path",
            residuals_plot_path="residuals_plot_path",
            support_pages_dir=self.supp_dir,
            options=self.options,
        )

    def tearDown(self) -> None:
        """
        Tear down the test suite.
        """
        shutil.rmtree(self.temp_dir)

    def test_create_summary_pages(self):
        """
        Check that a summary page is created for a problem set.
        """
        expected_path = os.path.join(
            self.supp_dir, f"{self.prob_name}_summary.html"
        )
        self.assertTrue(os.path.exists(expected_path))

    def test_set_link_attribute(self):
        """
        Check that all results have a summary page added to the
        'problem_summary_page_link' attribute.
        """
        for result in self.best_results.values():
            self.assertNotEqual(result.problem_summary_page_link, "")


class GetFigurePathsTests(TestCase):
    """
    Tests the very simple get_figure_paths function
    """

    def setUp(self):
        results, self.options = load_mock_results()
        self.result = results[0]

    def test_with_links(self):
        """
        Tests that the returned links are correct when links are passed in.
        """
        self.result.figure_link = "some_link"
        self.result.start_figure_link = "other_link"
        figure_link, start_link = problem_summary_page._get_figure_paths(
            self.result
        )
        self.assertEqual(figure_link, os.path.join("figures", "some_link"))
        self.assertEqual(start_link, os.path.join("figures", "other_link"))

    def test_no_links(self):
        """
        Tests that links are not changed if an empty string is given.
        """
        self.result.figure_link = ""
        self.result.start_figure_link = ""
        figure_link, start_link = problem_summary_page._get_figure_paths(
            self.result
        )
        self.assertEqual(figure_link, "")
        self.assertEqual(start_link, "")


if __name__ == "__main__":
    main()
