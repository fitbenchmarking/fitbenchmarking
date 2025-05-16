"""
Test plots
"""

import inspect
import os
import unittest
from tempfile import TemporaryDirectory
from unittest import mock

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from fitbenchmarking import test_files
from fitbenchmarking.core.results_output import (
    create_directories,
    create_index_page,
)
from fitbenchmarking.results_processing import plots
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.options import Options


def load_mock_result():
    """
    Load a predictable result.

    :return: Manually generated results
    :rtype: FittingResult
    """
    options = Options()
    cp_dir = os.path.dirname(inspect.getfile(test_files))
    options.checkpoint_filename = os.path.join(cp_dir, "checkpoint.json")

    cp = Checkpoint(options)
    results, _, _, _ = cp.load()
    best = {}
    for label, dataset in results.items():
        for i, r in enumerate(dataset):
            r.is_best_fit = False
            key = (label, r.problem_tag)
            if key not in best or best[key][1] < r.accuracy:
                best[key] = (i, r.accuracy)
        for b in best.values():
            dataset[b[0]].is_best_fit = True

    return results


def find_error_bar_count(path):
    """
    Reads an html file and counts the error_y count
    """
    with open(path, encoding="utf-8") as file:
        html_content = file.read()
    return html_content.count("error_y")


class PlotTests(unittest.TestCase):
    """
    Test the plot object is correct.
    """

    def setUp(self):
        self.fr = load_mock_result()

        self.opts = Options()
        self.opts.use_errors = True

        self._dir = TemporaryDirectory()
        self.opts.results_dir = self._dir.name

        _, _, self.figures_dir = create_directories(
            options=self.opts, group_name="NIST_low"
        )

        # This copies the js directory, and therefore plotly.js, into the
        # results directory. This is needed as plotly.js is used in a test.
        create_index_page(self.opts, ["NIST_low"], self.figures_dir)

        best = [
            r
            for r in self.fr["Fake_Test_Data"]
            if r.is_best_fit and r.problem_tag == "prob_1"
        ][0]
        self.plot = plots.Plot(
            best_result=best, options=self.opts, figures_dir=self.figures_dir
        )

        self.df = {}
        # Create a dataframe for each row
        for label, dataset in self.fr.items():
            for result in dataset:
                key = (label, result.problem_tag)
                if key not in self.df:
                    self.df[key] = pd.concat(
                        [
                            pd.DataFrame(
                                {
                                    "x": result.data_x,
                                    "y": result.data_y,
                                    "e": result.data_e,
                                    "minimizer": "Data",
                                    "cost_function": "",
                                    "best": False,
                                }
                            ),
                            pd.DataFrame(
                                {
                                    "x": result.data_x,
                                    "y": result.ini_y,
                                    "e": result.data_e,
                                    "minimizer": "Starting Guess",
                                    "cost_function": label,
                                    "best": False,
                                }
                            ),
                        ]
                    )

                result_dict = {
                    "x": result.data_x,
                    "y": result.fin_y,
                    "e": result.data_e,
                    "minimizer": result.sanitised_min_name(True),
                    "cost_function": "NLLS",
                    "best": result.is_best_fit,
                }
                self.df[key] = pd.concat(
                    [self.df[key], pd.DataFrame(result_dict)],
                    axis=0,
                    ignore_index=True,
                )

    def test_plot_initial_guess_create_files(self):
        """
        Test that initial plot creates a file and errorbars are
        added to the plot.
        """
        file_name = self.plot.plot_initial_guess(
            self.df[("Fake_Test_Data", "prob_1")]
        )

        self.assertEqual(file_name, "start_for_prob_1.html")
        path = os.path.join(self.figures_dir, file_name)
        self.assertTrue(os.path.exists(path))
        self.assertEqual(find_error_bar_count(path), 2)

    def test_best_filename_return(self):
        """
        Test that best_filename returns the correct filename
        """
        file_name = self.plot.best_filename(self.fr["Fake_Test_Data"][0])
        self.assertEqual(file_name, "m10_[s1]_jj0_fit_for_cf1_prob_0.html")

    def test_plotly_fit_create_files(self):
        """
        Test that plotly_fit creates a file and errorbars are
        added to the plot.
        """
        file_names = self.plot.plotly_fit(
            self.df[("Fake_Test_Data", "prob_1")]
        )

        for m, s, j in zip(
            ["m10", "m11", "m01", "m00", "m10", "m11", "m01", "m00"],
            ["s1", "s1", "s0", "s0", "s1", "s1", "s0", "s0"],
            ["jj0", "jj0", "jj0", "jj0", "jj1", "jj1", "jj1", "jj1"],
        ):
            file_name_prefix = f"{m}_[{s}]_{j}"
            self.assertEqual(
                file_names[file_name_prefix],
                file_name_prefix + "_fit_for_cf1_prob_1.html",
            )
            path = os.path.join(self.figures_dir, file_names[file_name_prefix])
            self.assertTrue(os.path.exists(path))
            self.assertEqual(find_error_bar_count(path), 2)

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._check_data_len"
    )
    def test__check_data_len_called_by_plotly_fit(self, check_data_len):
        """
        Test that plotly_fit calls _check_data_len
        when plot_info is set.
        """
        self.plot.result.plot_info = {
            "plot_type": "1d_cuts",
            "n_plots": 3,
            "subplot_titles": [
                "0.5 Å<sup>-1</sup>",
                "1 Å<sup>-1</sup>",
                "1.5 Å<sup>-1</sup>",
            ],
            "ebin_cens": [0.9],
            "ax_titles": {"x": "x", "y": "y"},
        }

        self.plot.plotly_fit(self.df[("Fake_Test_Data", "prob_1")])
        check_data_len.assert_called()

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._check_data_len"
    )
    def test__check_data_len_not_called(self, check_data_len):
        """
        Test that plotly_fit and plots_residuals don't call
        _check_data_len when plot_info is not set.
        """
        self.plot.plotly_fit(self.df[("Fake_Test_Data", "prob_1")])
        check_data_len.assert_not_called()

        self.plot.plot_residuals(
            categories=self.fr,
            title="",
            options=self.opts,
            figures_dir=self.figures_dir,
        )
        check_data_len.assert_not_called()

    def test__check_data_len_raises_error(self):
        """
        Test _check_data_len raises error if data lengths are
        unexpected
        """
        data = self.df[("Fake_Test_Data", "prob_1")]
        y_best = data["y"][data["best"]]
        x_best = 10 * data["x"][data["best"]].to_list()

        with self.assertRaises(PlottingError):
            self.plot._check_data_len(y_best, x_best)

    def test_plot_posteriors_create_files(self):
        """
        Test that plot_posteriors creates a file
        """

        self.plot.result.param_names = ["a", "b"]

        result = mock.Mock()
        result.params_pdfs = {
            "scipy_pfit": [1.0, 1.0],
            "scipy_perr": [0.1, 0.2],
            "a": [1.5, 1.0, 1.2],
            "b": [0.9, 1.6, 1.1],
        }
        result.sanitised_min_name.return_value = "m10_[s1]_jj0"
        result.sanitised_name = "cf1_prob_1"

        file_name = self.plot.plot_posteriors(result)

        self.assertEqual(
            file_name, "m10_[s1]_jj0_posterior_pdf_plot_for_cf1_prob_1.html"
        )
        path = os.path.join(self.figures_dir, file_name)
        self.assertTrue(os.path.exists(path))

    def test_multivariate_plot(self):
        """
        Test that the plotting fails gracefully for multivariate problems.
        """
        self.fr["Fake_Test_Data"][0].multivariate = True

        with self.assertRaises(PlottingError):
            self.plot = plots.Plot(
                best_result=self.fr["Fake_Test_Data"][0],
                options=self.opts,
                figures_dir=self.figures_dir,
            )

    def test_write_html_with_link_plotlyjs(self):
        """
        Test that the function is producing output files smaller than 50KB.
        """
        fig = go.Figure()
        htmlfile_name = "figure.html"
        self.plot.write_html_with_link_plotlyjs(
            fig=fig,
            figures_dir=self.figures_dir,
            htmlfile=htmlfile_name,
            options=self.opts,
        )

        htmlfile_path = os.path.join(self.figures_dir, htmlfile_name)
        file_size_KB = os.path.getsize(htmlfile_path) / 1000

        assert file_size_KB < 50

    def test_plot_residuals_create_files(self):
        """
        Test that plot_residuals creates a file
        """
        file_name = self.plot.plot_residuals(
            categories=self.fr,
            title="",
            options=self.opts,
            figures_dir=self.figures_dir,
        )

        self.assertEqual(file_name, "residuals_plot_for_prob_0.html")
        path = os.path.join(self.figures_dir, file_name)
        self.assertTrue(os.path.exists(path))

    def test__create_empty_residuals_plots(self):
        """
        Test that create_empty_residuals_plot_spinw creates correct
        number of subplots
        """
        result = next(iter(self.fr.values()))[0]
        result.plot_info = {
            "plot_type": "1d_cuts",
            "n_plots": 3,
            "subplot_titles": [
                "0.5 Å<sup>-1</sup>",
                "1 Å<sup>-1</sup>",
                "1.5 Å<sup>-1</sup>",
            ],
            "ebin_cens": [0.9],
        }
        titles = 3 * ["Q_value"]

        fig = self.plot._create_empty_residuals_plots(
            categories=self.fr,
            subplot_titles=titles,
        )
        rows, cols = fig._get_subplot_rows_columns()

        assert len(rows) == len(self.fr.keys())
        assert len(cols) == result.plot_info["n_plots"]

        result.plot_info["ebin_cens"] = [2, 4]

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._create_empty_residuals_plots"
    )
    def test__create_empty_residuals_plots_not_called_when_no_subplots(
        self, create_empty_residuals
    ):
        """
        Test that _create_empty_residuals is not called when there is only
        one plot (no subplots).
        """
        self.plot.plot_residuals(
            categories=self.fr,
            title="",
            options=self.opts,
            figures_dir=self.figures_dir,
        )
        create_empty_residuals.assert_not_called()

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._add_residual_traces"
    )
    def test__add_residual_traces_called_by_plot_residuals(
        self, add_residual_traces
    ):
        """
        Test that _add_residual_traces gets called by plot_residuals
        the right number of times (based on number of categories and results).
        """
        self.plot.plot_residuals(
            categories=self.fr,
            title="",
            options=self.opts,
            figures_dir=self.figures_dir,
        )
        expected = len(self.fr["Fake_Test_Data"])
        self.assertEqual(add_residual_traces.call_count, expected)

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._plot_minimizer_results"
    )
    def test__plot_minimizer_results_called_by_plot_summary(
        self, plot_minimizer_results
    ):
        """
        Test that _plot_minimizer_results gets called by plot_summary.
        """
        self.plot.plot_summary(
            categories=self.fr,
            title="",
            options=self.opts,
            figures_dir=self.figures_dir,
        )
        expected = len(self.fr["Fake_Test_Data"])
        self.assertEqual(plot_minimizer_results.call_count, expected)

    def test__plot_summary_when_data_x_cuts(self):
        """
        Test that plot_summary raises no exception
        when data_x_cuts is set.
        """
        categs = self.fr
        categ1_key, categ1_results = next(iter(categs.items()))
        new_results = []

        for result in categ1_results:
            result.data_x_cuts = np.arange(10)
            result.data_y_cuts = np.arange(10)
            new_results.append(result)

        modif_categs = {categ1_key: new_results}

        self.plot.plot_summary(
            categories=modif_categs,
            title="",
            options=self.opts,
            figures_dir=self.figures_dir,
        )

    def test__plot_minimizer_results_when_data_x_cuts(self):
        """
        Test _plot_minimizer_results raises no exception
        when data_x_cuts is set.
        """
        fig = make_subplots(rows=1, cols=2)

        categs = self.fr
        categ1_name, categ1_results = next(iter(categs.items()))
        result = categ1_results[0]

        result.data_x_cuts = np.arange(10)
        result.data_y_cuts = np.arange(10)
        result.fin_y_cuts = np.arange(10)

        self.plot._plot_minimizer_results(
            fig=fig,
            result=result,
            categ=categ1_name,
            n_plots=2,
            ax_titles={"x": "x", "y": "y"},
            colour="rgb(255,0,0)",
        )

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._create_empty_residuals_plots"
    )
    def test_plot_residuals_calls__create_empty_residuals_plots(
        self, create_empty_residuals_plots
    ):
        categs = self.fr
        categ1_name, categ1_results = next(iter(categs.items()))
        result = categ1_results[0]
        result.plot_info = {"n_plots": 2, "subplot_titles": ["plot1", "plot2"]}
        modif_categs = {categ1_name: [result]}

        self.plot.plot_residuals(
            categories=modif_categs,
            title="",
            options=self.opts,
            figures_dir=self.figures_dir,
        )

        self.assertEqual(create_empty_residuals_plots.call_count, 1)

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._add_data_points"
    )
    def test__add_data_points_called_by_plot_summary(self, add_data_points):
        """
        Test that _add_data_points gets called once by plot_summary.
        """
        self.plot.plot_summary(
            categories=self.fr,
            title="",
            options=self.opts,
            figures_dir=self.figures_dir,
        )
        add_data_points.assert_called_once()

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._add_data_points"
    )
    def test__add_data_points_called_by_plot_initial_guess(
        self, add_data_points
    ):
        """
        Test that _add_data_points gets called once by
        plot_initial_guess.
        """
        self.plot.plot_initial_guess(self.df[("Fake_Test_Data", "prob_1")])
        add_data_points.assert_called_once()

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._add_data_points"
    )
    def test__add_data_points_called_by_plotly_fit(self, add_data_points):
        """
        Test that _add_data_points gets called the right number of times
        by plotly_fit.
        """
        input_df = self.df[("Fake_Test_Data", "prob_1")]
        self.plot.plotly_fit(input_df)
        minimizers = input_df["minimizer"][
            ~input_df.minimizer.isin(["Data", "Starting Guess"])
        ].unique()
        self.assertEqual(add_data_points.call_count, len(minimizers))

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._add_starting_guess"
    )
    def test__add_starting_guess_called_by_plot_initial_guess(
        self, add_starting_guess
    ):
        """
        Test that _add_starting_guess gets called by plot_initial_guess.
        """
        self.plot.plot_initial_guess(self.df[("Fake_Test_Data", "prob_1")])
        add_starting_guess.assert_called_once()

    @mock.patch(
        "fitbenchmarking.results_processing.plots.Plot._add_starting_guess"
    )
    def test__add_starting_guess_called_by_plotly_fit(
        self, add_starting_guess
    ):
        """
        Test that _add_starting_guess gets called by plotly_fit, the
        correct number of times.
        """
        input_df = self.df[("Fake_Test_Data", "prob_1")]
        self.plot.plotly_fit(input_df)
        minimizers = input_df["minimizer"][
            ~input_df.minimizer.isin(["Data", "Starting Guess"])
        ].unique()
        self.assertEqual(add_starting_guess.call_count, len(minimizers))

    def test_plot_2d_data_creates_files(self):
        """
        Test that plot_2d_data creates a file
        """
        categs = self.fr
        modif_categs = {}

        categ1_key, categ1_results = next(iter(categs.items()))
        new_results = []

        for k, result in enumerate(categ1_results):
            result.plot_info = {}
            result.plot_info["plot_type"] = "2d"
            result.fin_y_complete = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
            result.plot_info["ebin_cens"] = np.arange(3)
            result.plot_info["modQ_cens"] = np.arange(40)
            new_results.append(result)

        modif_categs[categ1_key] = new_results

        file_name = self.plot.plot_2d_data(
            categories=modif_categs,
            title="",
            options=self.opts,
            figures_dir=self.figures_dir,
        )

        self.assertEqual(file_name, "2d_plots_for_best_minims_prob_1.html")
        path = os.path.join(self.figures_dir, file_name)
        self.assertTrue(os.path.exists(path))

    def test__sample_colours(self):
        """
        Test that _sample_colours produces the expected output.
        """
        exp_colours = ["rgb(9, 173, 234)", "rgb(213, 242, 0)"]
        colours = self.plot._sample_colours([0.4, 0.7])
        self.assertEqual(exp_colours, colours)


if __name__ == "__main__":
    unittest.main()
