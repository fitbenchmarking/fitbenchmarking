"""
Tests for the performance profiler file.
"""

import inspect
import os
import unittest
from inspect import getfile
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
        options = Options()
        (acc, runtime), _ = performance_profiler.profile(self.results,
                                                         self.fig_dir,
                                                         options)

        assert acc == "acc_profile.html"
        assert runtime == "runtime_profile.html"

    def test_profile_returns_dict(self):
        """
        Test that the performance profiler returns the expected dictionary
        of dataframes for plotting the profiles.
        """
        options = Options()
        (_, _), data_dfs = performance_profiler.profile(self.results,
                                                        self.fig_dir,
                                                        options)

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

    @staticmethod
    def test_create_plot_and_df_returns_plotly_go():
        """
        Test that create_plot_and_data_df returns a plotly graph object.
        """
        step_values = [
            np.array([0., 1., 1., 1., 1.2, 1.4, 1.6, 1.7,
                      2., 5., 6.5, 8., 10.4, 15.9, 200., 500., 1000.]),
            np.array([0., 1., 1., 1.6, 2., 6., 8., 15.,
                      20., 30., 50., 80., 100., 300., 500., 600., 1200.]),
            np.array([0., 1., 1., 1., 1., 1., 1., 1., 1., 1.,
                      1., 1., 1., 1., 1., 1., 1.])
            ]
        solvers = ['migrad [minuit]', 'simplex [minuit]', 'dfogn [dfo]']
        plot, _ = performance_profiler.\
            create_plot_and_df(step_values, solvers)
        assert isinstance(plot, go.Figure)

    @staticmethod
    def test_create_plot_and_df_returns_pandas_df():
        """
        Test that create_plot_and_data_df returns a pandas Dataframe.
        """
        step_values = [
            np.array([0., 1., 1., 1., 1.2, 1.4, 1.6, 1.7,
                      2., 5., 6.5, 8., 10.4, 15.9, 200., 500., 1000.]),
            np.array([0., 1., 1., 1.6, 2., 6., 8., 15.,
                      20., 30., 50., 80., 100., 300., 500., 600., 1200.]),
            np.array([0., 1., 1., 1., 1., 1., 1., 1., 1., 1.,
                      1., 1., 1., 1., 1., 1., 1.])
            ]
        solvers = ['migrad [minuit]', 'simplex [minuit]', 'dfogn [dfo]']
        _, data_df = performance_profiler.\
            create_plot_and_df(step_values, solvers)
        assert isinstance(data_df, pd.DataFrame)

    def test_create_correct_data_df(self):
        """
        Test that the performance profiler creates the expected dataframes
        to be used to build the dash plots.
        """
        expected_df = read_csv(self.expected_results_dir + "/pp_data.csv")
        solvers = ['lm-bumps [bumps]', 'scipy-leastsq [bumps]',
                   'dfogn [dfo] (4 failures)']
        solver_values = [
            np.array([0., 5.4, 11., 20., 59.1, 130.5, 300.1, 600.5, 1000]),
            np.array([0., 1.9, 11.1, 41.5, 101.3, 130.5, 200.8, 300, 5000]),
            np.array([0., 3.5, 7.2, 17.1, 29.6, 50.1, 78.6, 230.5, 770.1]),
        ]

        plot_points = len(solvers) * [
            np.array([
                0., 0.125, 0.25, 0.375,
                0.5, 0.625, 0.75, 0.875,
                1.])]
        output_df = performance_profiler.create_df(solvers,
                                                   solver_values,
                                                   plot_points)
        assert_frame_equal(output_df, expected_df)

    # pylint: enable=W0632


if __name__ == "__main__":
    unittest.main()
