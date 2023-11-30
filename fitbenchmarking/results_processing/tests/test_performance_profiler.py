"""
Tests for the performance profiler file.
"""

import inspect
import os
import unittest
import re
from inspect import getfile
from tempfile import TemporaryDirectory

import numpy as np
from pandas.testing import assert_frame_equal
from pandas import read_csv
import pandas as pd
import plotly.graph_objects as go

import fitbenchmarking
from fitbenchmarking import test_files
from fitbenchmarking.core.results_output import preprocess_data
from fitbenchmarking.results_processing import performance_profiler
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.options import Options
from fitbenchmarking.results_processing.plots import Plot


def load_mock_results():
    """
    Load a predictable results set.

    :return: Manually generated results
    :rtype: list[FittingResult]
    """
    options = Options()
    cp_dir = os.path.dirname(inspect.getfile(test_files))
    options.checkpoint_filename = os.path.join(cp_dir, 'checkpoint.json')

    cp = Checkpoint(options)
    results, _, _ = cp.load()

    return [v
            for lst in results.values()
            for v in lst]


def remove_ids_and_src(html_path):
    """
    Remove ids within html file.
    :param html_path: path to html file
    :type html_path: str

    :return: Lines in html file, processed to remove ids
    :rtype: list[str]
    """

    with open(html_path, 'r', encoding='utf-8') as f:
        read_lines = f.readlines()

    processed_lines = []
    for str_i in read_lines:
        pattern_for_ids = r"\b((?:[a-z]+\S*\d+|\d\S*[a-z]+)[a-z\d_-]*)\b\w+"
        processed_line = re.sub(pattern_for_ids, '', str_i)
        pattern_for_src = r"\b(([A-Za-z._-]+[\\/]+){1,}([A-Za-z.\s_-]+))\b"
        final_processed_line = re.sub(pattern_for_src, '', processed_line)
        processed_lines.append(final_processed_line)

    return processed_lines


class PerformanceProfilerTests(unittest.TestCase):
    """
    General tests for the performance profiler code.
    """

    def setUp(self):
        """
        Sets up acc runtime profile names
        """
        results = load_mock_results()
        _, self.results = preprocess_data(results)

        min_acc = 0.2
        self.accuracy_expected = {
            'm00 [s0]: j:j0': [np.inf, np.inf],
            'm00 [s0]: j:j1': [np.inf, np.inf],
            'm01 [s0]: j:j0': [0.4, 2.0],
            'm01 [s0]: j:j1': [0.8, 0.2],
            'm10 [s1]: j:j0': [0.2, 1.0],
            'm10 [s1]: j:j1': [0.6, 3.0],
            'm11 [s1]: j:j0': [0.3, 1.0],
            'm11 [s1]: j:j1': [0.7, 3.0],
        }
        for k in self.accuracy_expected:
            self.accuracy_expected[k] = [
                v/min_acc for v in self.accuracy_expected[k]]

        min_runtime = 1.0
        self.runtime_expected = {
            'm00 [s0]: j:j0': [np.inf, np.inf],
            'm00 [s0]: j:j1': [np.inf, np.inf],
            'm01 [s0]: j:j0': [13.0, 2.0],
            'm01 [s0]: j:j1': [1.0, 15.0],
            'm10 [s1]: j:j0': [15.0, 1.0],
            'm10 [s1]: j:j1': [11.0, 3.0],
            'm11 [s1]: j:j0': [14.0, 1.0],
            'm11 [s1]: j:j1': [10.0, 2.0],
        }
        for k in self.runtime_expected:
            self.runtime_expected[k] = [
                v/min_runtime for v in self.runtime_expected[k]]

        self.supp_pag_dir = 'support_pages'
        self.fig_dir = ''
        self.acc_name = "acc_profile.html"
        self.runtime_name = "runtime_profile.html"

        root = os.path.dirname(getfile(fitbenchmarking))
        self.expected_results_dir = os.path.join(
            root, 'results_processing',
            'tests', 'expected_results')

        self.solvers = ['migrad [minuit]', 'simplex [minuit]',
                        'dfogn [dfo]']
        self.step_values = [
            np.array([0., 1., 1.2, 1.4, 2., 5.,
                      10.4, 15.9, 500.]),
            np.array([0., 1., 1.5, 1.8, 5., 8.,
                      15.4, 25.9, 600.]),
            np.array([0., 2., 3.5, 5.8, 7., 10.,
                      25.4, 45.9, 800.])
            ]
        self.solver_values = [
            np.array([0., 5.4, 11., 20., 59.1,
                      130.5, 300.1, 600.5, 1000]),
            np.array([0., 1.9, 11.1, 41.5, 101.3,
                      130.5, 200.8, 300, 5000]),
            np.array([0., 3.5, 7.2, 17.1, 29.6, 50.1,
                      78.6, 230.5, 770.1]),
            ]
        self.options = Options()

        # pylint: disable=consider-using-with
        self._dir = TemporaryDirectory()
        self.temp_result = self._dir.name
        # pylint: enable=consider-using-with

    def tearDown(self):
        """
        Removes expected acc and runtime plots
        """
        for name in [self.acc_name, self.runtime_name]:
            if os.path.isfile(name):
                os.remove(name)

    def test_correct_prepare_profile_data(self):
        """
        Test that prepare profile data gives the correct result
        """
        acc, runtime = performance_profiler.prepare_profile_data(self.results)

        for k, v in self.accuracy_expected.items():
            assert np.allclose(v, acc[k])
        for k, v in self.runtime_expected.items():
            assert np.allclose(v, runtime[k])

    # pylint: disable=W0632
    def test_correct_profile_output_paths(self):
        """
        Test that the performance profiler returns the expected paths.
        """
        (acc, runtime), _ = performance_profiler.profile(self.results,
                                                         self.fig_dir,
                                                         self.options)
        assert acc == "acc_profile.html"
        assert runtime == "runtime_profile.html"

    def test_profile_returns_dict(self):
        """
        Test that the performance profiler returns the expected dictionary
        of dataframes for plotting the profiles.
        """
        (_, _), data_dfs = performance_profiler.profile(self.results,
                                                        self.fig_dir,
                                                        self.options)
        assert isinstance(data_dfs, dict)
        for df in list(data_dfs.values()):
            assert isinstance(df, pd.DataFrame)
            assert not df.empty

    @staticmethod
    def test_update_fig_returns_plotly_go():
        """
        Test that update_fig returns a plotly graph object.
        """
        fig = go.Figure()
        profile_name = 'acc'
        use_log_plot = True
        log_upper_limit = 10000
        fig = performance_profiler.update_fig(fig, profile_name,
                                              use_log_plot,
                                              log_upper_limit)
        assert isinstance(fig, go.Figure)

    def test_create_plot_and_df_returns_correct_plot(self):
        """
        Test that create_plot_and_data_df returns a plotly graph object.
        """
        output_plot_path = self.temp_result + \
            'for_test_create_plot.html'
        expected_plot_path = self.expected_results_dir + \
            '/for_test_create_plot.html'

        plot, _ = performance_profiler.\
            create_plot_and_df(self.step_values, self.solvers)

        Plot.write_html_with_link_plotlyjs(fig=plot,
                                           figures_dir='',
                                           htmlfile=output_plot_path,
                                           options=self.options)

        processed_achieved_lines = remove_ids_and_src(output_plot_path)
        processed_exp_lines = remove_ids_and_src(expected_plot_path)

        assert set(processed_exp_lines) == set(processed_achieved_lines)
        assert isinstance(plot, go.Figure)

    def test_create_plot_and_df_returns_pandas_df(self):
        """
        Test that create_plot_and_data_df returns a pandas Dataframe.
        """
        _, data_df = performance_profiler.\
            create_plot_and_df(self.step_values, self.solvers)
        assert isinstance(data_df, pd.DataFrame)

    def test_create_df_returns_correct_df(self):
        """
        Test that the performance profiler creates the expected dataframes
        to be used to build the dash plots.
        """
        expected_df = read_csv(self.expected_results_dir + "/pp_data.csv")
        plot_points = len(self.solvers) * [
            np.array([
                0., 0.125, 0.25, 0.375,
                0.5, 0.625, 0.75, 0.875,
                1.])]
        output_df = performance_profiler.create_df(self.solvers,
                                                   self.solver_values,
                                                   plot_points)
        assert_frame_equal(output_df, expected_df)

    def test_get_plot_path_and_data_returns_dict_for_data(self):
        """
        Test that get_plot_path_and_data returns a dictionary
        of dataframes.
        """
        acc = {'migrad [minuit]': [1., 2.,  5., 6.,
                                   15., 150, 180.],
               'simplex [minuit]': [1., 20., 100., 110.,
                                    150., 1500, 1800.],
               'dfogn [dfo]': [1., 50., 500., 2000.,
                               2600., 2700, 2800.]}
        runtime = {'migrad [minuit]': [4.6, 6.4, 1.3, 8.5,
                                       51.6, 10.8, 15.2],
                   'simplex [minuit]': [6.9, 15.2, 6.5,
                                        5.6, 7., 8.5, 6.5],
                   'dfogn [dfo]': [8.6, 7.4, 51.6, 6.9,
                                   6.5,  28.3, 17.2]}

        _, data_dfs = performance_profiler.\
            get_plot_path_and_data(acc, runtime,
                                   self.fig_dir,
                                   self.options)

        assert isinstance(data_dfs, dict)
        for df in list(data_dfs.values()):
            assert isinstance(df, pd.DataFrame)
            assert not df.empty


class DashPerfProfileTests(unittest.TestCase):
    """
    Test the plot object is correct.
    """
    def setUp(self):

        self.options = Options()
        root = os.path.dirname(getfile(fitbenchmarking))
        self.expected_results_dir = os.path.join(
            root, 'results_processing',
            'tests', 'expected_results')

        data = read_csv(self.expected_results_dir + "/pp_data.csv")

        self.perf_profile = performance_profiler.\
            DashPerfProfile('runtime', data,
                            'NIST_low_difficulty')

        # pylint: disable=consider-using-with
        self._dir = TemporaryDirectory()
        self.temp_result = self._dir.name
        # pylint: enable=consider-using-with

    def test_create_graph_returns_expected_plot(self):
        """ Test create_graph returns the expected plot. """

        output = self.perf_profile.create_graph("Log x-axis")

        output_plot_path = self.temp_result + 'obtained_plot.html'

        Plot.write_html_with_link_plotlyjs(fig=output,
                                           figures_dir='',
                                           htmlfile=output_plot_path,
                                           options=self.options)

        expected_plot_path = self.expected_results_dir + '/dash_plot.html'

        processed_exp_lines = remove_ids_and_src(expected_plot_path)
        processed_achieved_lines = remove_ids_and_src(output_plot_path)

        assert isinstance(output, go.Figure)
        assert set(processed_exp_lines) == set(processed_achieved_lines)

    # pylint: enable=W0632


if __name__ == "__main__":
    unittest.main()
