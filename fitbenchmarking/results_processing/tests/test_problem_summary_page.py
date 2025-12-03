"""
Tests for the problem_summary_page python file.
"""

import inspect
import os
import shutil
from tempfile import TemporaryDirectory
from unittest import TestCase, main, mock

from parameterized import parameterized

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

    @mock.patch(
        "fitbenchmarking.results_processing.problem_summary_page._create_multistart_plots"
    )
    def test_create_calls_create_multistart_plots_once(self, mock):
        """
        Check that _create_multistart_plots is called. It should
        be called exactly once because the plots will be the
        same across all problem rows.
        """
        problem_summary_page.create(
            results=self.results,
            best_results=self.best_results,
            support_pages_dir=self.supp_dir,
            figures_dir=self.fig_dir,
            options=self.options,
        )
        assert mock.call_count == 1


class CreateMultistartPlotsTests(TestCase):
    """
    Tests for the _create_multistart_plots function.
    """

    def setUp(self):
        """
        Setup for the class tests
        """
        self.fig_dir = "temp_figures_dir"
        results, self.options = load_mock_results()
        _, self.results = preprocess_data(results)

    @parameterized.expand([True, False])
    def test_function_returns_empty_str(self, make_plots):
        """
        Check that a _create_multistart_plots returns an empty string
        when results are not multistart and when make_plots is false.
        """
        self.options.make_plots = make_plots
        multistart = problem_summary_page._create_multistart_plots(
            results=self.results,
            figures_dir=self.fig_dir,
            options=self.options,
        )
        assert multistart == ""

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot.plot_multistart"
    )
    def test_function_sorts_results_and_calls_plot_multistart(self, mock):
        """
        Check that a _create_multistart_plots sorts the results and
        calls the plotting method.
        """
        self.results["prob_0"]["cf1"][0].multistart = True
        results = {
            "prob_0": {
                "cf1": [
                    self.results["prob_0"]["cf1"][0],
                    self.results["prob_0"]["cf1"][1],
                ]
            },
            "prob_1": {
                "cf1": [
                    self.results["prob_1"]["cf1"][0],
                    self.results["prob_1"]["cf1"][1],
                ]
            },
        }
        problem_summary_page._create_multistart_plots(
            results=results,
            figures_dir=self.fig_dir,
            options=self.options,
        )
        results_arg = mock.call_args[1]["results"]
        cf_arg = next(iter(results_arg.keys()))
        s_arg = next(iter(results_arg[cf_arg].keys()))
        m_arg = next(iter(results_arg[cf_arg][s_arg].keys()))
        assert cf_arg == "cf1"
        assert s_arg == "s0"
        assert m_arg == "m00"
        assert mock.call_count == 1


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
            two_d_plot="2d_plots_path",
            summary_plot="plot_path",
            residuals_plot="residuals_plot_path",
            multistart_plot="multistart_plot_path",
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


if __name__ == "__main__":
    main()
