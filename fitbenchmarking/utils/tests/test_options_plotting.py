'''
Test the PLOTTING section for the options file
'''
import inspect
import shutil
import os
import numpy as np
import unittest

from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


class PlottingOptionTests(unittest.TestCase):
    """
    Checks that the defaults in the PLOTTING section are set correctly
    """

    def setUp(self):
        """
        Initializes options class with defaults
        """
        self.options = Options()

    def test_make_plots_default(self):
        """
        Checks make_plots default
        """
        expected = True
        actual = self.options.make_plots
        self.assertEqual(expected, actual)

    def test_colour_scale_default(self):
        """
        Checks colour_scale default
        """
        expected = [(1.1, "#fef0d9"),
                    (1.33, "#fdcc8a"),
                    (1.75, "#fc8d59"),
                    (3, "#e34a33"),
                    (np.inf, "#b30000")]
        actual = self.options.colour_scale
        self.assertEqual(expected, actual)

    def test_comparison_mode_default(self):
        """
        Checks comparison_mode default
        """
        expected = 'both'
        actual = self.options.comparison_mode
        self.assertEqual(expected, actual)

    def test_table_type_default(self):
        """
        Checks table_type default
        """
        expected = ['acc', 'runtime', 'compare', 'local_min']
        actual = self.options.table_type
        self.assertEqual(expected, actual)

    def test_results_dir_default(self):
        """
        Checks results_dir default
        """
        expected = os.path.abspath('fitbenchmarking_results')
        actual = self.options.results_dir
        self.assertEqual(expected, actual)


class UserPlottingOptionTests(unittest.TestCase):
    """
    Checks the plotting in the options file are set correctly or raise errors
    """

    def setUp(self):
        """
        Sets the directory to save the temporary ini files in
        """
        options_dir = os.path.dirname(inspect.getfile(Options))
        self.test_files_dir = os.path.join(options_dir, 'tests', 'files')
        os.mkdir(self.test_files_dir)

    def tearDown(self):
        """
        Deletes temporary folder and results produced
        """
        if os.path.exists(self.test_files_dir):
            shutil.rmtree(self.test_files_dir)

    def generate_user_ini_file(self, opt_name, config_str):
        """
        Generates user defined ini file

        :param opt_name: name of option to be set
        :type opt_name: str
        :param config_str: section of an ini file which sets the option
        :type config_str: str

        :return: location of temporary ini file
        :rtype: str
        """
        opts_file = os.path.join(self.test_files_dir,
                                 'test_{}_valid.ini'.format(opt_name))
        with open(opts_file, 'w') as f:
            f.write(config_str)
        return opts_file

    def shared_valid(self, opt_name, options_set, config_str):
        """
        Shared test to check that the plotting option set is valid

        :param opt_name: name of option to be set
        :type opt_name: str
        :param options_set: option set to be tested
        :type options_set: list
        :param config_str: section of an ini file which sets the option
        :type config_str: str
        """
        opts_file = self.generate_user_ini_file(opt_name, config_str)
        options = Options(opts_file)
        actual = getattr(options, opt_name)
        self.assertEqual(options_set, actual)

    def shared_invalid(self, opt_name, config_str):
        """
        Shared test to check that the plotting option set is invalid

        :param opt_name: name of option to be set
        :type opt_name: str
        :param config_str: option set to be tested
        :type config_str: list
        """
        opts_file = self.generate_user_ini_file(opt_name, config_str)
        with self.assertRaises(exceptions.OptionsError):
            Options(opts_file)

    def test_invalid_option_key(self):
        """
        Tests that the user defined option key is invalid.
        """
        config_str = \
            "[PLOTTING]\nmake_figures: True"
        self.shared_invalid('make_figures', config_str)

    def test_minimizer_make_plots_valid(self):
        """
        Checks user set make_plots is valid
        """
        set_option = False
        config_str = \
            "[PLOTTING]\nmake_plots: no"
        self.shared_valid('make_plots', set_option, config_str)

    def test_minimizer_make_plots_invalid(self):
        """
        Checks user set make_plots is invalid
        """
        config_str = \
            "[PLOTTING]\nmake_plots: a selection of plots"
        self.shared_invalid('make_plots', config_str)

    def test_minimizer_colour_scale_valid(self):
        """
        Checks user set colour_scale is valid
        """
        set_option = [(1.1, "#fef0d9"),
                      (1.33, "#fdcc8a")]
        config_str = \
            "[PLOTTING]\ncolour_scale: 1.1, #fef0d9\n 1.33, #fdcc8a"
        self.shared_valid('colour_scale', set_option, config_str)

    def test_minimizer_comparison_mode_valid(self):
        """
        Checks user set comparison_mode is valid
        """
        set_option = "abs"
        config_str = \
            "[PLOTTING]\ncomparison_mode: abs"
        self.shared_valid('comparison_mode', set_option, config_str)

    def test_minimizer_comparison_mode_invalid(self):
        """
        Checks user set comparison_mode is invalid
        """
        config_str = \
            "[PLOTTING]\ncomparison_mode: absolute_values"
        self.shared_invalid('comparison_mode', config_str)

    def test_minimizer_table_type_valid(self):
        """
        Checks user set table_type is valid
        """
        set_option = ['acc', 'compare']
        config_str = \
            "[PLOTTING]\ntable_type: acc\n compare"
        self.shared_valid('table_type', set_option, config_str)

    def test_minimizer_table_type_invalid(self):
        """
        Checks user set table_type is invalid
        """
        config_str = \
            "[PLOTTING]\ntable_type: chi_sq\n "
        self.shared_invalid('table_type', config_str)

    def test_minimizer_results_dir_valid(self):
        """
        Checks user set results_dir is valid
        """
        set_option = os.path.abspath("results_dir")
        config_str = \
            "[PLOTTING]\nresults_dir: results_dir"
        self.shared_valid('results_dir', set_option, config_str)
