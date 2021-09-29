'''
Test the LOGGING section for the options file
'''
import inspect
import shutil
import os
import unittest

from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


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
        expected = 'fitbenchmarking.log'
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
        expected = 'INFO'
        actual = self.options.log_level
        self.assertEqual(expected, actual)

    def test_external_output_default(self):
        """
        Checks external_output default
        """
        expected = 'log_only'
        actual = self.options.external_output
        self.assertEqual(expected, actual)


class UserLoggingOptionTests(unittest.TestCase):
    """
    Checks the logging in the options file are set correctly or raise errors
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
        Shared test to check that the logging option set is valid

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
        Shared test to check that the logging option set is invalid

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
            "[LOGGING]\nlog_level: DEBUG"
        self.shared_invalid('log_level', config_str)

    def test_minimizer_file_name_valid(self):
        """
        Checks user set file_name is valid
        """
        set_option = "fitb.log"
        config_str = \
            "[LOGGING]\nfile_name: fitb.log"
        self.shared_valid('log_file', set_option, config_str)

    def test_minimizer_log_append_valid(self):
        """
        Checks user set log_append is valid
        """
        set_option = True
        config_str = \
            "[LOGGING]\nappend: yes"
        self.shared_valid('log_append', set_option, config_str)

    def test_minimizer_log_append_invalid(self):
        """
        Checks user set log_append are invalid
        """
        config_str = \
            "[LOGGING]\nappend: append_to_bottom"
        self.shared_invalid('log_append', config_str)

    def test_minimizer_log_level_valid(self):
        """
        Checks user set log_level is valid
        """
        set_option = "DEBUG"
        config_str = \
            "[LOGGING]\nlevel: DEBUG"
        self.shared_valid('log_level', set_option, config_str)

    def test_minimizer_log_level_invalid(self):
        """
        Checks user set log_level is invalid
        """
        config_str = \
            "[LOGGING]\nlevel: debug"
        self.shared_invalid('log_level', config_str)

    def test_minimizer_external_output_valid(self):
        """
        Checks user set external_output is valid
        """
        set_option = 'debug'
        config_str = \
            "[LOGGING]\nexternal_output: debug"
        self.shared_valid('external_output', set_option, config_str)

    def test_minimizer_external_output_invalid(self):
        """
        Checks user set external_output is invalid
        """
        config_str = \
            "[LOGGING]\nexternal_output: remove_third_party_output"
        self.shared_invalid('external_output', config_str)
