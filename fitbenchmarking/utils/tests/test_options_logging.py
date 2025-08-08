"""
Test the LOGGING section for the options file
"""

import unittest

from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.tests.test_options_fitting import (
    BaseFittingOptionTests,
)


class LoggingOptionTests(unittest.TestCase):
    """
    Checks the logging defaults are set correctly
    """

    def setUp(self):
        """
        Initializes options class with defaults
        """
        self.options = Options()

    def test_file_name_default(self):
        """
        Checks file_name default
        """
        expected = "fitbenchmarking.log"
        actual = self.options.log_file
        self.assertEqual(expected, actual)

    def test_append_default(self):
        """
        Checks append default
        """
        expected = False
        actual = self.options.log_append
        self.assertEqual(expected, actual)

    def test_level_default(self):
        """
        Checks level default
        """
        expected = "INFO"
        actual = self.options.log_level
        self.assertEqual(expected, actual)

    def test_external_output_default(self):
        """
        Checks external_output default
        """
        expected = "log_only"
        actual = self.options.external_output
        self.assertEqual(expected, actual)


class UserLoggingOptionTests(BaseFittingOptionTests):
    """
    Checks the logging in the options file are set correctly or raise errors
    """

    def test_invalid_option_key(self):
        """
        Tests that the user defined option key is invalid.
        """
        config_str = "[LOGGING]\nlog_level: DEBUG"
        self.shared_invalid("log_level", config_str)

    def test_minimizer_file_name_valid(self):
        """
        Checks user set file_name is valid
        """
        set_option = "fitb.log"
        config_str = "[LOGGING]\nfile_name: fitb.log"
        self.shared_valid("log_file", set_option, config_str)

    def test_minimizer_log_append_valid(self):
        """
        Checks user set log_append is valid
        """
        set_option = True
        config_str = "[LOGGING]\nappend: yes"
        self.shared_valid("log_append", set_option, config_str)

    def test_minimizer_log_append_invalid(self):
        """
        Checks user set log_append are invalid
        """
        config_str = "[LOGGING]\nappend: append_to_bottom"
        self.shared_invalid("log_append", config_str)

    def test_minimizer_log_level_valid(self):
        """
        Checks user set log_level is valid
        """
        set_option = "DEBUG"
        config_str = "[LOGGING]\nlevel: DEBUG"
        self.shared_valid("log_level", set_option, config_str)

    def test_minimizer_log_level_invalid(self):
        """
        Checks user set log_level is invalid
        """
        config_str = "[LOGGING]\nlevel: debug"
        self.shared_invalid("log_level", config_str)

    def test_minimizer_external_output_valid(self):
        """
        Checks user set external_output is valid
        """
        set_option = "debug"
        config_str = "[LOGGING]\nexternal_output: debug"
        self.shared_valid("external_output", set_option, config_str)

    def test_minimizer_external_output_invalid(self):
        """
        Checks user set external_output is invalid
        """
        config_str = "[LOGGING]\nexternal_output: remove_third_party_output"
        self.shared_invalid("external_output", config_str)
