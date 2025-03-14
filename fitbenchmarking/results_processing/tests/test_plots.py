"""
Test plots
"""

import inspect
import os
import unittest
from tempfile import TemporaryDirectory
from unittest import mock

import pandas as pd
import plotly.graph_objects as go

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

    @mock.patch("fitbenchmarking.results_processing.plots.Plot.plotly_spinw")
    def test_plotly_spinw_called(self, spinw_plot):
        """
        Test that plotly_fit calls plotly_spinw
        when spinw_plot_info is set.
        """
        self.plot.result.spinw_plot_info = {
            "plot_type": "1d_cuts",
            "n_cuts": 2,
            "q_cens": [0.5, 1],
            "ebin_cens": [0.9, 1.6, 1.1],
        }

        self.plot.plot_initial_guess(self.df[("Fake_Test_Data", "prob_1")])
        spinw_plot.assert_called()

        self.plot.plotly_fit(self.df[("Fake_Test_Data", "prob_1")])
        spinw_plot.assert_called()

    @mock.patch("fitbenchmarking.results_processing.plots.Plot.plotly_spinw")
    def test_plotly_spinw_fit_not_called(self, spinw_plot):
        """
        Test that plotly_fit doesn't call plotly_spinw
        when spinw_plot_info is not set.
        """
        self.plot.plot_initial_guess(self.df[("Fake_Test_Data", "prob_1")])
        spinw_plot.assert_not_called()

        self.plot.plotly_fit(self.df[("Fake_Test_Data", "prob_1")])
        spinw_plot.assert_not_called()

    def test_plotly_spinw(self):
        """
        Test that plotly_spinw creates correct number of subplots
        and raises error if data lengths are unexpected
        """
        self.plot.result.spinw_plot_info = {
            "plot_type": "1d_cuts",
            "n_cuts": 3,
            "q_cens": [0.5, 1, 1.5],
            "ebin_cens": [0.9],
        }
        data = self.df[("Fake_Test_Data", "prob_1")]
        y_best = data["y"][data["best"]]

        fig = self.plot.plotly_spinw(data, "m10_[s1]_jj0", y_best)
        _, cols = fig._get_subplot_rows_columns()

        assert len(cols) == self.plot.result.spinw_plot_info["n_cuts"]

        self.plot.result.spinw_plot_info["ebin_cens"] = [2, 4]

        with self.assertRaises(PlottingError):
            self.plot.plotly_spinw(data, "m10_[s1]_jj0", y_best)

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

    def test_create_empty_residuals_plot_spinw(self):
        """
        Test that create_empty_residuals_plot_spinw creates correct
        number of subplots and raises error if data lengths are unexpected
        """
        result = next(iter(self.fr.values()))[0]
        result.spinw_plot_info = {
            "plot_type": "1d_cuts",
            "n_cuts": 3,
            "q_cens": [0.5, 1, 1.5],
            "ebin_cens": [0.9],
        }

        fig = self.plot._create_empty_residuals_plot_spinw(
            categories=self.fr,
            n_plots_per_row=result.spinw_plot_info["n_cuts"],
        )
        rows, cols = fig._get_subplot_rows_columns()

        assert len(rows) == len(self.fr.keys())
        assert len(cols) == result.spinw_plot_info["n_cuts"]

        result.spinw_plot_info["ebin_cens"] = [2, 4]

        with self.assertRaises(PlottingError):
            self.plot._create_empty_residuals_plot_spinw(
                categories=self.fr,
                n_plots_per_row=result.spinw_plot_info["n_cuts"],
            )


if __name__ == "__main__":
    unittest.main()
