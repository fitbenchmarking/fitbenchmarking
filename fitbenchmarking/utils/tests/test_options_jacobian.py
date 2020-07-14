'''
Test the JACOBIAN section for the options file
'''
import inspect
import shutil
import os
import unittest

from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


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
        expected = {'scipy': ['2-point'], 'analytic': ['cutest']}
        actual = self.options.num_method
        self.assertEqual(expected, actual)


class UserJacobianOptionTests(unittest.TestCase):
    """
    Checks the Jacobian in the options file are set correctly or raise errors
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
        Shared test to check that the Jacobian option set is valid

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
        Shared test to check that the Jacobian option set is invalid

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
            "[JACOBIAN]\nnum_minimizer_runs: 3"
        self.shared_invalid('num_minimizer_runs', config_str)

    def test_minimizer_num_method_valid(self):
        """
        Checks user set num_method is valid
        """
        set_option = {'scipy': ['cs'], 'analytic': ['cutest']}
        config_str = \
            "[JACOBIAN]\nscipy: cs"
        self.shared_valid('num_method', set_option, config_str)

    def test_minimizer_num_method_invalid(self):
        """
        Checks user set num_method is invalid
        """
        config_str = \
            "[JACOBIAN]\nnum_method: FD_3point"
        self.shared_invalid('num_method', config_str)
