from __future__ import (absolute_import, division, print_function)

import numpy as np
import os
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import unittest

from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.jacobian.SciPyFD_2point_jacobian import ScipyTwoPoint
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options
from fitbenchmarking.results_processing import plots


class PlotTests(unittest.TestCase):
    """
    Test the plot object is correct.
    """

    def setUp(self):
        self.opts = Options()
        self.opts.use_errors = True

        self.prob = FittingProblem(self.opts)
        self.prob.data_x = np.array([1, 2, 4, 3, 5])
        self.prob.sorted_index = np.array([0, 1, 3, 2, 4])
        self.prob.data_y = np.array([4, 3, 5, 2, 1])
        self.prob.data_e = np.array([0.5, 0.2, 0.3, 0.1, 0.4])
        self.prob.starting_values = [{'x': 1, 'y': 2}]
        self.prob.eval_f = lambda x, y: x[0] * y + x[1]
        self.prob.name = 'full name'
        jac = ScipyTwoPoint(self.prob)
        self.fr = FittingResult(options=self.opts,
                                problem=self.prob,
                                jac=jac,
                                chi_sq=1.0,
                                initial_params=[1.8],
                                params=[1.2],
                                runtime=2.0,
                                minimizer='fit',
                                error_flag=1)

        self.opts = Options()
        self.opts.use_errors = True

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

        self.assertEqual(file_name, 'start_for_full_name.png')
        path = os.path.join(self.dir.name, file_name)
        self.assertTrue(os.path.exists(path))

    def test_plot_best_create_files(self):
        """
        Test that best plot creates a file.
        """
        file_name = self.plot.plot_best('fit', [0.1, 3])

        self.assertEqual(file_name, 'fit_fit_for_full_name.png')
        path = os.path.join(self.dir.name, file_name)
        self.assertTrue(os.path.exists(path))

    def test_plot_fit_create_files(self):
        """
        Test that fit plot creates a file.
        """
        file_name = self.plot.plot_fit('fit', [8, 6.2])

        self.assertEqual(file_name, 'fit_fit_for_full_name.png')
        path = os.path.join(self.dir.name, file_name)
        self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
