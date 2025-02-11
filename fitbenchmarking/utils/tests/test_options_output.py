"""
Test the OUTPUT section for the options file
"""

import unittest
from pathlib import Path

from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.tests.test_options_fitting import (
    BaseFittingOptionTests,
)


class OutputOptionTests(unittest.TestCase):
    """
    Checks that the defaults in the OUTPUT section are set correctly
    """

    def test_results_dir_not_default(self):
        """
        Checks results_dir default
        """
        options = Options(
            additional_options={"results_dir": Path(__file__).parent}
        )
        default = Path("fitbenchmarking_results").resolve()
        self.assertNotEqual(default, options.results_dir)

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

    def test_colour_map_default(self):
        """
        Checks colour_map default
        """
        expected = "magma_r"
        actual = self.options.colour_map
        self.assertEqual(expected, actual)

    def test_cmap_range_default(self):
        """
        Checks cmap_range default
        """
        expected = [0.2, 0.8]
        actual = self.options.cmap_range
        self.assertEqual(expected, actual)

    def test_colour_ulim_default(self):
        """
        Checks colour_ulim default
        """
        expected = 100
        actual = self.options.colour_ulim
        self.assertEqual(expected, actual)

    def test_comparison_mode_default(self):
        """
        Checks comparison_mode default
        """
        expected = "both"
        actual = self.options.comparison_mode
        self.assertEqual(expected, actual)

    def test_table_type_default(self):
        """
        Checks table_type default
        """
        expected = ["acc", "runtime", "compare", "local_min", "energy_usage"]
        actual = self.options.table_type
        self.assertEqual(expected, actual)


class UserOutputOptionTests(BaseFittingOptionTests):
    """
    Checks the output options in the file are set correctly or raise errors
    """

    def test_output_results_directory_valid(self):
        """
        Checks user set make_plots is valid
        """
        set_option = Path("new_results").resolve()
        config_str = "[OUTPUT]\nresults_dir: new_results/"
        opts_file = self.generate_user_ini_file("results_dir", config_str)
        options = Options(opts_file)
        actual = getattr(options, "results_dir")
        self.assertEqual(str(set_option), actual)

    def test_invalid_option_key(self):
        """
        Tests that the user defined option key is invalid.
        """
        config_str = "[OUTPUT]\nmake_figures: True"
        self.shared_invalid("make_figures", config_str)

    def test_minimizer_make_plots_valid(self):
        """
        Checks user set make_plots is valid
        """
        set_option = False
        config_str = "[OUTPUT]\nmake_plots: no"
        self.shared_valid("make_plots", set_option, config_str)

    def test_minimizer_make_plots_invalid(self):
        """
        Checks user set make_plots is invalid
        """
        config_str = "[OUTPUT]\nmake_plots: a selection of plots"
        self.shared_invalid("make_plots", config_str)

    def test_minimizer_colour_map_valid(self):
        """
        Checks user set colour_map is valid
        """
        set_option = "plasma"
        config_str = "[OUTPUT]\ncolour_map: plasma"
        self.shared_valid("colour_map", set_option, config_str)

    def test_minimizer_colour_map_invalid(self):
        """
        Checks user set colour_map is invalid
        """
        config_str = "[OUTPUT]\ncolour_map: purple"
        self.shared_invalid("colour_map", config_str)

    def test_minimizer_cmap_range_valid(self):
        """
        Checks user set cmap_range is valid
        """
        set_option = [0.1, 0.9]
        config_str = "[OUTPUT]\ncmap_range: [0.1, 0.9]"
        self.shared_valid("cmap_range", set_option, config_str)

    def test_minimizer_cmap_range_invalid(self):
        """
        Checks user set cmap_range is invalid
        """
        config_str1 = "[OUTPUT]\ncmap_range: [0.1, 0.3"
        self.shared_invalid("cmap_range", config_str1)
        config_str2 = "[OUTPUT]\ncmap_range: [0.5, 0.3]"
        self.shared_invalid("cmap_range", config_str2)
        config_str3 = "[OUTPUT]\ncmap_range: [0.1, 0.3, 0.4]"
        self.shared_invalid("cmap_range", config_str3)
        config_str4 = "[OUTPUT]\ncmap_range: [0.1, 5]"
        self.shared_invalid("cmap_range", config_str4)

    def test_minimizer_comparison_mode_valid(self):
        """
        Checks user set comparison_mode is valid
        """
        set_option = "abs"
        config_str = "[OUTPUT]\ncomparison_mode: abs"
        self.shared_valid("comparison_mode", set_option, config_str)

    def test_minimizer_comparison_mode_invalid(self):
        """
        Checks user set comparison_mode is invalid
        """
        config_str = "[OUTPUT]\ncomparison_mode: absolute_values"
        self.shared_invalid("comparison_mode", config_str)

    def test_minimizer_table_type_valid(self):
        """
        Checks user set table_type is valid
        """
        set_option = ["acc", "compare"]
        config_str = "[OUTPUT]\ntable_type: acc\n compare"
        self.shared_valid("table_type", set_option, config_str)

    def test_minimizer_table_type_invalid(self):
        """
        Checks user set table_type is invalid
        """
        config_str = "[OUTPUT]\ntable_type: chi_sq\n "
        self.shared_invalid("table_type", config_str)
