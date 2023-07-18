'''
Test plots
'''

import inspect
import os
import unittest
from tempfile import TemporaryDirectory
import pandas as pd

from fitbenchmarking import test_files
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
    options.checkpoint_filename = os.path.join(cp_dir, 'checkpoint.json')

    cp = Checkpoint(options)
    results, _, _ = cp.load()

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
        self.dir = TemporaryDirectory()
        # pylint: enable=consider-using-with
        self.plot = plots.Plot(best_result=self.fr['Fake_Test_Data'][0],
                               options=self.opts,
                               figures_dir=self.dir.name)
        self.df = {}
        # Create a dataframe for each result
        for cf, cat_results in self.fr.items():
            datatype = {'x': cat_results[0].data_x,
                        'y': cat_results[0].data_y,
                        'e': cat_results[0].data_e,
                        'minimizer': 'Data',
                        'cost_function': cf,
                        'best': False}
            self.df[cf] = pd.DataFrame(datatype)
            # next the initial data
            datatype = {'x': cat_results[0].data_x,
                        'y': cat_results[0].ini_y,
                        'e': cat_results[0].data_e,
                        'minimizer': 'Starting Guess',
                        'cost_function': cf,
                        'best': False}
            self.df[cf] = pd.concat([self.df[cf], pd.DataFrame(datatype)],
                                    axis=0,
                                    ignore_index=True)
            # then get data for each minimizer
            for result in cat_results:
                datatype = {'x': result.data_x,
                            'y': result.fin_y,
                            'e': result.data_e,
                            'minimizer': result.sanitised_min_name(True),
                            'cost_function': 'NLLS',
                            'best': result.is_best_fit}
                self.df[cf] = pd.concat([self.df[cf], pd.DataFrame(datatype)],
                                        axis=0,
                                        ignore_index=True)

    def test_plot_initial_guess_create_files(self):
        """
        Test that initial plot creates a file.
        """
        file_name = self.plot.plot_initial_guess(self.df['Fake_Test_Data'])

        self.assertEqual(file_name, 'start_for_prob_0.html')
        path = os.path.join(self.dir.name, file_name)
        self.assertTrue(os.path.exists(path))

    def test_best_filename_return(self):
        """
        Test that best_fileame returns the correct filename
        """
        file_name = self.plot.best_filename(self.fr['Fake_Test_Data'][0])
        self.assertEqual(file_name,
                         'm10_[s1]_jj0_fit_for_cf1_prob_0.html')

    def test_plotly_fit_create_files(self):
        """
        Test that plotly_fit creates a file.
        """
        file_names = self.plot.plotly_fit(self.df['Fake_Test_Data'])

        self.assertEqual(file_names['m10_[s1]_jj0'],
                         'm10_[s1]_jj0_fit_for_cf1_prob_0.html')
        path = os.path.join(self.dir.name, file_names['m10_[s1]_jj0'])
        self.assertTrue(os.path.exists(path))

    def test_multivariate_plot(self):
        """
        Test that the plotting fails gracefully for multivariate problems.
        """
        self.fr['Fake_Test_Data'][0].multivariate = True

        with self.assertRaises(PlottingError):
            self.plot = plots.Plot(best_result=self.fr['Fake_Test_Data'][0],
                                   options=self.opts,
                                   figures_dir=self.dir.name)


if __name__ == "__main__":
    unittest.main()
