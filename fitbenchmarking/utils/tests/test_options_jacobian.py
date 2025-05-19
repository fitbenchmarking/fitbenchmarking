"""
Test the JACOBIAN section for the options file
"""

import unittest

from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.tests.test_options_fitting import (
    BaseFittingOptionTests,
)


class JacobianOptionTesJacobians(unittest.TestCase):
    """
    Checks that the defaults in the JACOBIAN section are set correctly
    """

    def setUp(self):
        """
        Initializes options class with defaults
        """
        self.options = Options()

    def test_num_method_default(self):
        """
        Checks num_method default
        """
        expected = {
            "analytic": ["default"],
            "best_available": ["default"],
            "default": ["default"],
            "numdifftools": ["central"],
            "scipy": ["2-point"],
        }
        actual = self.options.jac_num_method
        self.assertEqual(expected, actual)


class UserJacobianOptionTests(BaseFittingOptionTests):
    """
    Checks the Jacobian in the options file are set correctly or raise errors
    """

    def test_invalid_option_key(self):
        """
        Tests that the user defined option key is invalid.
        """
        config_str = "[JACOBIAN]\nnum_minimizer_runs: 3"
        self.shared_invalid("num_minimizer_runs", config_str)

    def test_minimizer_num_method_valid(self):
        """
        Checks user set num_method is valid
        """
        set_option = {
            "analytic": ["default"],
            "best_available": ["default"],
            "default": ["default"],
            "numdifftools": ["central"],
            "scipy": ["cs"],
        }
        config_str = "[JACOBIAN]\nscipy: cs"
        self.shared_valid("jac_num_method", set_option, config_str)

    def test_minimizer_num_method_invalid(self):
        """
        Checks user set num_method is invalid
        """
        config_str = "[JACOBIAN]\nnum_method: FD_3point"
        self.shared_invalid("jac_num_method", config_str)
