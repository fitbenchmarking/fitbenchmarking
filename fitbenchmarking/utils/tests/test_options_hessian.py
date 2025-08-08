"""
Test the HESSIAN section for the options file
"""

import unittest

from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.tests.test_options_fitting import (
    BaseFittingOptionTests,
)


class HessianOptionTesHessians(unittest.TestCase):
    """
    Checks that the defaults in the HESSIAN section are set correctly
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
        actual = self.options.hes_num_method
        self.assertEqual(expected, actual)


class UserHessianOptionTests(BaseFittingOptionTests):
    """
    Checks the Hessian in the options file are set correctly or raise errors
    """

    def test_invalid_option_key(self):
        """
        Tests that the user defined option key is invalid.
        """
        config_str = "[HESSIAN]\nnum_minimizer_runs: 3"
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
        config_str = "[HESSIAN]\nscipy: cs"
        self.shared_valid("hes_num_method", set_option, config_str)

    def test_minimizer_num_method_invalid(self):
        """
        Checks user set num_method is invalid
        """
        config_str = "[HESSIAN]\nnum_method: FD_3point"
        self.shared_invalid("hes_num_method", config_str)
