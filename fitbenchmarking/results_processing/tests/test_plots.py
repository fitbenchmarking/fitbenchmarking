'''
Test plots
'''
from __future__ import absolute_import, division, print_function

import inspect
import os
import unittest

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

from fitbenchmarking import test_files
from fitbenchmarking.results_processing import plots
from fitbenchmarking.utils.checkpoint import get_checkpoint
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
    options.checkpoint_filename = os.path.join(cp_dir, 'checkpoint.json')

    cp = get_checkpoint(options)
    results, _, _ = cp.load()

    return results['prob_0'][0]


class PlotTests(unittest.TestCase):
    """
    Test the plot object is correct.
    """

    def setUp(self):
        self.opts = Options()

        self.fr = load_mock_result()

        self.dir = TemporaryDirectory()
        self.plot = plots.Plot(best_result=self.fr,
                               options=self.opts,
                               figures_dir=self.dir.name)

    def test_init_creates_line(self):
        """
        Tests that init puts a single line in the plot.
        """
        lines = self.plot.ax.get_lines()
        self.assertEqual(len(lines), 1)

    def test_plot_data_creates_line(self):
        """
        Test that plotting a line when line_plot is None creates a new line.
        """
        self.plot.line_plot = None
        lines = self.plot.ax.get_lines()
        lines_before = len(lines)
        self.plot.plot_data(False, self.plot.ini_guess_plot_options)
        lines = self.plot.ax.get_lines()
        self.assertEqual(lines_before + 1, len(lines))

    def test_plot_data_updates_line(self):
        """
        Tests that plotting when line_plot is not None updates the line.
        """
        self.plot.plot_data(False,
                            self.plot.ini_guess_plot_options,
                            [1, 2, 3],
                            [2, 3, 1])
        lines = self.plot.ax.get_lines()
        lines_before = len(lines)
        self.plot.plot_data(False, self.plot.ini_guess_plot_options)
        lines = self.plot.ax.get_lines()
        self.assertEqual(lines_before, len(lines))

    def test_plot_initial_guess_create_files(self):
        """
        Test that initial plot creates a file.
        """
        file_name = self.plot.plot_initial_guess()

        self.assertEqual(file_name, 'start_for_prob_0.png')
        path = os.path.join(self.dir.name, file_name)
        self.assertTrue(os.path.exists(path))

    def test_plot_best_create_files(self):
        """
        Test that best plot creates a file.
        """
        file_name = self.plot.plot_best(self.fr)

        self.assertEqual(file_name,
                         'm10_[s1]_jj0_fit_for_cf1_prob_0.png')
        path = os.path.join(self.dir.name, file_name)
        self.assertTrue(os.path.exists(path))

    def test_plot_fit_create_files(self):
        """
        Test that fit plot creates a file.
        """
        file_name = self.plot.plot_fit(self.fr)

        self.assertEqual(file_name,
                         'm10_[s1]_jj0_fit_for_cf1_prob_0.png')
        path = os.path.join(self.dir.name, file_name)
        self.assertTrue(os.path.exists(path))

    def test_multivariate_plot(self):
        """
        Test that the plotting fails gracefully for multivariate problems.
        """
        self.fr.multivariate = True

        with self.assertRaises(PlottingError):
            self.plot = plots.Plot(best_result=self.fr,
                                   options=self.opts,
                                   figures_dir=self.dir.name)


if __name__ == "__main__":
    unittest.main()
