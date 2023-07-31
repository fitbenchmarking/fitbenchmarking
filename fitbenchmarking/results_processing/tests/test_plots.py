'''
Test plots
'''

import os
import unittest
from tempfile import TemporaryDirectory
import numpy as np

from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.results_processing import plots
from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


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
        self.prob.starting_values = [{'p': 1.8}]
        self.prob.name = 'full name'

        def tmp(p, x=None, y=None):
            if x is None:
                x = self.prob.data_x
            if y is None:
                y = self.prob.data_y
            return p + y * x + y
        self.prob.eval_model = tmp
        cost_func = NLLSCostFunc(self.prob)
        jac = 'j1'
        self.fr = FittingResult(options=self.opts,
                                cost_func=cost_func,
                                jac=jac,
                                hess=None,
                                acc=1.0,
                                initial_params=[1.8],
                                params=[1.2],
                                runtime=2.0,
                                software='s1',
                                minimizer='fit',
                                error_flag=1)

        self.opts = Options()
        self.opts.use_errors = True
        # pylint: disable=consider-using-with
        self.dir = TemporaryDirectory()
        # pylint: enable=consider-using-with
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
        file_name = self.plot.plot_best(self.fr)

        self.assertEqual(file_name,
                         'fit_[s1]_jj1_fit_for_NLLSCostFunc_full_name.png')
        path = os.path.join(self.dir.name, file_name)
        self.assertTrue(os.path.exists(path))

    def test_plot_fit_create_files(self):
        """
        Test that fit plot creates a file.
        """
        file_name = self.plot.plot_fit(self.fr)

        self.assertEqual(file_name,
                         'fit_[s1]_jj1_fit_for_NLLSCostFunc_full_name.png')
        path = os.path.join(self.dir.name, file_name)
        self.assertTrue(os.path.exists(path))

    def test_multivariate_plot(self):
        """
        Test that the plotting fails gracefully for multivariate problems.
        """
        self.fr.cost_func.problem.multivariate = True

        with self.assertRaises(PlottingError):
            self.plot = plots.Plot(best_result=self.fr,
                                   options=self.opts,
                                   figures_dir=self.dir.name)


if __name__ == "__main__":
    unittest.main()
