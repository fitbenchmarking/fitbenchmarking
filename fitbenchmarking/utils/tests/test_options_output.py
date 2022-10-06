'''
Test the OUTPUT section for the options file
'''
import inspect
import shutil
import os
import unittest

from fitbenchmarking.utils.options import Options


class OutputOptionTests(unittest.TestCase):
    """
    Checks that the defaults in the PLOTTING section are set correctly
    """

    def test_results_dir_not_default(self):
        """
        Checks results_dir default
        """
        options = Options(additional_options={
                          'results_dir': os.path.dirname(__file__)})
        default = os.path.abspath('fitbenchmarking_results')
        self.assertNotEqual(default, options.results_dir)


class UserOutputOptionTests(unittest.TestCase):
    """
    Checks the output options in the file are set correctly or raise errors
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

    def test_output_results_directory_valid(self):
        """
        Checks user set make_plots is valid
        """
        set_option = os.path.abspath("new_results")
        config_str = \
            "[OUTPUT]\nresults_dir: new_results/"
        self.shared_valid('results_dir', set_option, config_str)
