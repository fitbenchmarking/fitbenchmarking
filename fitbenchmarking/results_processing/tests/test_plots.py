'''
Test plots
'''

import inspect
import os
import unittest
from tempfile import TemporaryDirectory

import pandas as pd
import plotly.graph_objects as go

from fitbenchmarking import test_files
from fitbenchmarking.results_processing import plots
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.options import Options
from fitbenchmarking.core.results_output import \
    create_directories, create_index_page


def load_mock_result():
    """
    Load a predictable result.

    :return: Manually generated results
    :rtype: FittingResult
    """
    options = Options()
    cp_dir = os.path.dirname(inspect.getfile(test_files))
    options.checkpoint_filename = os.path.join(cp_dir, 'checkpoint.json')

    cp = Checkpoint(options)
    results, _, _ = cp.load()
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


class PlotTests(unittest.TestCase):
    """
    Test the plot object is correct.
    """

    def setUp(self):
        self.fr = load_mock_result()

        self.opts = Options()
        self.opts.use_errors = True

        # pylint: disable=consider-using-with
        self._dir = TemporaryDirectory()
        self.opts.results_dir = self._dir.name
        # pylint: enable=consider-using-with

        _, _, self.figures_dir = create_directories(options=self.opts,
                                                    group_name='NIST_low')

        # This copies the js directory, and therefore plotly.js, into the
        # results directory. This is needed as plotly.js is used in a test.
        create_index_page(self.opts, ['NIST_low'], self.figures_dir)

        best = [r for r in self.fr['Fake_Test_Data']
                if r.is_best_fit and r.problem_tag == 'prob_1'][0]
        self.plot = plots.Plot(best_result=best,
                               options=self.opts,
                               figures_dir=self.figures_dir)

        self.df = {}
        # Create a dataframe for each row
        for label, dataset in self.fr.items():
            for result in dataset:
                key = (label, result.problem_tag)
                if key not in self.df:
                    self.df[key] = pd.concat([
                        pd.DataFrame({'x': result.data_x,
                                      'y': result.data_y,
                                      'e': result.data_e,
                                      'minimizer': 'Data',
                                      'cost_function': '',
                                      'best': False}),
                        pd.DataFrame({'x': result.data_x,
                                      'y': result.ini_y,
                                      'e': result.data_e,
                                      'minimizer': 'Starting Guess',
                                      'cost_function': label,
                                      'best': False})
                    ])

                result_dict = {'x': result.data_x,
                               'y': result.fin_y,
                               'e': result.data_e,
                               'minimizer': result.sanitised_min_name(True),
                               'cost_function': 'NLLS',
                               'best': result.is_best_fit}
                self.df[key] = pd.concat([self.df[key],
                                          pd.DataFrame(result_dict)],
                                         axis=0,
                                         ignore_index=True)

    def test_plot_initial_guess_create_files(self):
        """
        Test that initial plot creates a file.
        """
        file_name = self.plot.plot_initial_guess(
            self.df[('Fake_Test_Data', 'prob_1')])

        self.assertEqual(file_name, 'start_for_prob_1.html')
        path = os.path.join(self.figures_dir, file_name)
        self.assertTrue(os.path.exists(path))

    def test_best_filename_return(self):
        """
        Test that best_filename returns the correct filename
        """
        file_name = self.plot.best_filename(self.fr['Fake_Test_Data'][0])
        self.assertEqual(file_name,
                         'm10_[s1]_jj0_fit_for_cf1_prob_0.html')

    def test_plotly_fit_create_files(self):
        """
        Test that plotly_fit creates a file.
        """
        file_names = self.plot.plotly_fit(
            self.df[('Fake_Test_Data', 'prob_1')])

        self.assertEqual(file_names['m10_[s1]_jj0'],
                         'm10_[s1]_jj0_fit_for_cf1_prob_1.html')
        path = os.path.join(self.figures_dir, file_names['m10_[s1]_jj0'])
        self.assertTrue(os.path.exists(path))

    def test_multivariate_plot(self):
        """
        Test that the plotting fails gracefully for multivariate problems.
        """
        self.fr['Fake_Test_Data'][0].multivariate = True

        with self.assertRaises(PlottingError):
            self.plot = plots.Plot(best_result=self.fr['Fake_Test_Data'][0],
                                   options=self.opts,
                                   figures_dir=self.figures_dir)

    def test_write_html_with_link_plotlyjs(self):
        """
        Test that the function is producing output files smaller than 50KB.
        """
        fig = go.Figure()
        htmlfile_name = 'figure.html'
        self.plot.write_html_with_link_plotlyjs(fig=fig,
                                                figures_dir=self.figures_dir,
                                                htmlfile=htmlfile_name,
                                                options=self.opts)

        htmlfile_path = os.path.join(self.figures_dir, htmlfile_name)
        file_size_KB = os.path.getsize(htmlfile_path)/1000

        assert file_size_KB < 50


if __name__ == "__main__":
    unittest.main()
