"""
Tests for the performance profiler file.
"""

import inspect
import os
import re
import unittest
from inspect import getfile
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pandas import read_csv
from pandas.testing import assert_frame_equal

import fitbenchmarking
from fitbenchmarking import test_files
from fitbenchmarking.core.results_output import preprocess_data
from fitbenchmarking.results_processing import performance_profiler
from fitbenchmarking.results_processing.plots import Plot
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


def remove_ids_and_src(html_path):
    """
    Reads html file and removes ids and src.
    :param html_path: path to html file
    :type html_path: str

    :return: Processed lines from html file
    :rtype: list[str]
    """

    with open(html_path, 'r', encoding='utf-8') as f:
        read_lines = f.readlines()

    processed_lines = []
    pattern_for_ids = r'"(?:[a-f\d]+-)+[a-f\d]+"'

    for str_i in read_lines:
        line_without_ids = re.sub(pattern_for_ids, '', str_i)

        # Needed for the test to pass on Windows
        final_processed_line = line_without_ids.replace('\\', '/')
        processed_lines.append(final_processed_line)

    return processed_lines


def diff_between_htmls(expected_plot_path, output_plot_path):
    """
    Finds differences between two html files line by line.
    Returns an empty list if no difference is found.

    :param expected: path to html file with expected lines
    :type expected: str
    :param achieved: path to html file with achieved lines
    :type achieved: str

    :return: Lines in the two files that present differences
    :rtype: list[list]
    """
    act_lines = remove_ids_and_src(output_plot_path)
    exp_lines = remove_ids_and_src(expected_plot_path)

    diff = []
    for i, (act_line, exp_line) in enumerate(zip(act_lines, exp_lines)):
        exp_line = '' if exp_line is None else exp_line.strip('\n')
        act_line = '' if act_line is None else act_line.strip('\n')

        if act_line != exp_line:
            diff.append([i, exp_line, act_line])

    if diff:
        print(f"Comparing {output_plot_path} against {expected_plot_path}\n"
              + "\n".join([f'== Line {change[0]} ==\n'
                           f'Expected :{change[1]}\n'
                           f'Actual   :{change[2]}'
                           for change in diff]))

    return diff


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

        min_emissions = 1.0
        self.emissions_expected = {
            'm00 [s0]: j:j0': [np.inf, np.inf],
            'm00 [s0]: j:j1': [np.inf, np.inf],
            'm01 [s0]: j:j0': [1e4, 10.0],
            'm01 [s0]: j:j1': [1.0, 1e4],
            'm10 [s1]: j:j0': [1e4, 1.0],
            'm10 [s1]: j:j1': [1e2, 1e2],
            'm11 [s1]: j:j0': [1e3, 1.0],
            'm11 [s1]: j:j1': [1e2, 1e2],
        }
        for k in self.emissions_expected:
            self.emissions_expected[k] = [
                v/min_emissions for v in self.emissions_expected[k]]

        self.fig_dir = ''

        root = os.path.dirname(getfile(fitbenchmarking))
        self.expected_results_dir = os.path.join(
            root, 'results_processing',
            'tests', 'expected_results')

        self.options = Options()
        self.solvers = ['migrad [minuit]', 'simplex [minuit]',
                        'dfogn [dfo]']
        self.step_values = [
            np.array([0., 1., 1.2, 1.4, 2., 5., 10.4, 15.9, 500.]),
            np.array([0., 1., 1.5, 1.8, 5., 8., 15.4, 25.9, 600.]),
            np.array([0., 2., 3.5, 5.8, 7., 10., 25.4, 45.9, 800.])
        ]

        self.solver_values = [
            np.array([0.00e+00, 1.00e+00, 1.20e+00, 1.40e+00, 2.00e+00,
                      5.00e+00, 1.04e+01, 1.59e+01, 5.00e+02, 1.00e+20]),
            np.array([0.00e+00, 1.00e+00, 1.50e+00, 1.80e+00, 5.00e+00,
                      8.00e+00, 1.54e+01, 2.59e+01, 6.00e+02, 1.00e+20]),
            np.array([0.00e+00, 2.00e+00, 3.50e+00, 5.80e+00, 7.00e+00,
                      1.00e+01, 2.54e+01, 4.59e+01, 8.00e+02, 1.00e+20])
        ]

        self.plot_points = len(self.solvers) * [
            np.array([0., 0.125, 0.25, 0.375, 0.5,
                      0.625, 0.75, 0.875, 1., 1.])
        ]

        # pylint: disable=consider-using-with
        self._dir = TemporaryDirectory()
        self.temp_result = self._dir.name
        # pylint: enable=consider-using-with

    def tearDown(self):
        """
        Removes expected plots
        """
        for metric in ['acc', 'runtime', 'emissions']:
            if os.path.isfile(f"{metric}_profile.html"):
                os.remove(f"{metric}_profile.html")

    def test_correct_prepare_profile_data(self):
        """
        Test that prepare profile data gives the correct result.
        """
        bounds = performance_profiler.prepare_profile_data(self.results)

        for k, v in self.accuracy_expected.items():
            assert np.allclose(v, bounds['acc'][k])
        for k, v in self.runtime_expected.items():
            assert np.allclose(v, bounds['runtime'][k])
        for k, v in self.emissions_expected.items():
            assert np.allclose(v, bounds['emissions'][k])

    # pylint: disable=W0632
    def test_correct_profile_output_paths(self):
        """
        Test that the performance profiler returns the expected paths.
        """
        pp_locations, _ = performance_profiler.profile(self.results,
                                                       self.fig_dir,
                                                       self.options)
        assert pp_locations['acc'] == "acc_profile.html"
        assert pp_locations['runtime'] == "runtime_profile.html"
        assert pp_locations['emissions'] == "emissions_profile.html"

    def test_profile_returns_dict(self):
        """
        Test that the performance profiler returns a dictionary
        of dataframes for plotting the profiles.
        """
        _, pp_dfs = performance_profiler.profile(self.results,
                                                 self.fig_dir,
                                                 self.options)
        assert isinstance(pp_dfs, dict)
        for df in list(pp_dfs.values()):
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

    def test_create_plot_returns_correct_plot(self):
        """
        Test that create_plot_and_df returns the correct plot.
        """
        output_plot_path = self.temp_result + \
            '/pp_offline_plot.html'
        expected_plot_path = self.expected_results_dir + \
            '/pp_offline_plot.html'

        plot = performance_profiler.\
            create_plot(self.step_values, self.solvers)

        Plot.write_html_with_link_plotlyjs(fig=plot,
                                           figures_dir='',
                                           htmlfile=output_plot_path,
                                           options=self.options)

        diff = diff_between_htmls(expected_plot_path, output_plot_path)
        self.assertListEqual([], diff)

    def test_create_df_returns_correct_df(self):
        """
        Test that create_df creates the expected dataframe to be used
        to build the dash plots.
        """
        expected_df = read_csv(self.expected_results_dir +
                               "/offline_pp_plot_data.csv")
        output_df = performance_profiler.create_df(self.solvers,
                                                   self.solvers,
                                                   self.solver_values,
                                                   self.plot_points)
        assert_frame_equal(output_df, expected_df)

    def test_create_plots_and_get_paths(self):
        """
        Test that create_plots_and_get_paths returns the correct paths.
        """
        bounds = {'acc': {}, 'runtime': {}, 'emissions': {}}
        paths = performance_profiler.\
            create_plots_and_get_paths(bounds,
                                       self.fig_dir,
                                       self.options)

        expec_paths = {'acc': 'acc_profile.html',
                       'runtime': 'runtime_profile.html',
                       'emissions': 'emissions_profile.html'}

        assert paths == expec_paths

    def test_compute_step_values(self):
        """
        Test compute_step_values returns the correct step_values
        and max_value.
        """

        expec_step_vals = self.step_values
        expec_max = 800.

        profile_plot = {'migrad [minuit]': [1.2, 1.4, 1., 500.,
                                            2., 10.4, 15.9, 5.],
                        'simplex [minuit]': [15.4, 1., 1.5, 1.8,
                                             8., 5., 600., 25.9],
                        'dfogn [dfo]': [3.5, 5.8, 2., 10., 7.,
                                        45.9, 25.4, 800.]}

        step_vals, max_val = performance_profiler.\
            compute_step_values(profile_plot)

        assert max_val == expec_max
        for arr, exp_arr in zip(step_vals, expec_step_vals):
            assert np.array_equal(arr, exp_arr)

    def test_adjust_values_to_plot(self):
        """
        Test adjust_values_to_plot returns the correct output dict.
        """
        expected_dict = {
            'solvers': self.solvers,
            'labels': self.solvers,
            'solver_values': self.solver_values,
            'plot_points': self.plot_points
        }
        output_dict = performance_profiler.\
            adjust_values_to_plot(self.step_values, self.solvers)

        assert expected_dict.keys() == output_dict.keys()
        assert expected_dict['solvers'] == output_dict['solvers']
        assert expected_dict['labels'] == output_dict['labels']
        assert np.array_equal(expected_dict['solver_values'],
                              output_dict['solver_values'])
        assert np.array_equal(expected_dict['plot_points'],
                              output_dict['plot_points'])

    # pylint: disable=no-self-use
    def test_compute_linestyle_combinations(self):
        """
        Test compute_linestyle_combinations returns expected styles.
        """

        output = performance_profiler.compute_linestyle_combinations()
        assert isinstance(output, list)
        for combination in output:
            assert isinstance(combination, tuple)
            assert isinstance(combination[0], str)
            assert re.match(r"#[0-9a-fA-F]{6}", combination[1])
    # pylint: enable=no-self-use


class DashPerfProfileTests(unittest.TestCase):
    """
    Test the DashPerfProfile object is correct.
    """

    def setUp(self):
        """
        Sets up the data for the dash plot.
        """
        self.options = Options()
        root = os.path.dirname(getfile(fitbenchmarking))
        self.expected_results_dir = os.path.join(
            root, 'results_processing',
            'tests', 'expected_results')

        self.data = pd.DataFrame.from_dict({
            'migrad [minuit]': [1.2, 1.4, 1., 500.,
                                2., 10.4, 15.9, 5.],
            'simplex [minuit]': [15.4, 1., 1.5, 1.8,
                                 8., 5., 600., 25.9],
            'dfogn [dfo]': [3.5, 5.8, 2., 10., 7.,
                            45.9, 25.4, 800.]})

        self.perf_profile = performance_profiler.\
            DashPerfProfile('runtime', self.data,
                            'NIST_low_difficulty')

        # pylint: disable=consider-using-with
        self._dir = TemporaryDirectory()
        self.temp_result = self._dir.name
        # pylint: enable=consider-using-with

    def test_create_graph_returns_expected_plot(self):
        """
        Test create_graph returns the expected plot.
        """

        selected_solvers = self.data.columns
        output_fig = self.perf_profile.\
            create_graph(x_axis_scale="Log x-axis",
                         solvers=selected_solvers[:3])

        output_plot_path = self.temp_result + '/obtained_plot.html'

        Plot.write_html_with_link_plotlyjs(fig=output_fig,
                                           figures_dir='',
                                           htmlfile=output_plot_path,
                                           options=self.options)

        expected_plot_path = self.expected_results_dir + '/dash_plot.html'

        diff = diff_between_htmls(expected_plot_path, output_plot_path)
        self.assertListEqual([], diff)

    def test_prepare_data(self):
        """
        Test prepare_data returns correct output dataframe.
        """
        selected_solvers = self.data.columns
        output = self.perf_profile.prepare_data(selected_solvers)
        expected_output = read_csv(self.expected_results_dir +
                                   "/dash_pp_plot_data.csv")
        assert output.equals(expected_output)

    # pylint: enable=W0632


if __name__ == "__main__":
    unittest.main()
