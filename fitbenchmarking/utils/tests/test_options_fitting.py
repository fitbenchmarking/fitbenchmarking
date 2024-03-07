'''
Test the FITTING section for the options file
'''
import inspect
import shutil
import os
import unittest

from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


class FittingOptionTests(unittest.TestCase):
    """
    Checks that the defaults in the FITTING section are set correctly
    """

    def setUp(self):
        """
        Initializes options class with defaults
        """
        self.options = Options()

    def test_num_runs_default(self):
        """
        Checks num_runs default
        """
        expected = 5
        actual = self.options.num_runs
        self.assertEqual(expected, actual)

    def test_algorithm_type_default(self):
        """
        Checks algorithm_type default
        """
        expected = ['all']
        actual = self.options.algorithm_type
        self.assertEqual(expected, actual)

    def test_software_default(self):
        """
        Checks software default
        """
        expected = ['scipy', 'scipy_ls']
        actual = self.options.software
        self.assertEqual(expected, actual)

    def test_jac_method_default(self):
        """
        Checks jac_method default
        """
        expected = ['best_available']
        actual = self.options.jac_method
        self.assertEqual(expected, actual)

    def test_hes_method_default(self):
        """
        Checks hes_method default
        """
        expected = ['analytic']
        actual = self.options.hes_method
        self.assertEqual(expected, actual)

    def test_cost_func_default(self):
        """
        Checks cost_func default
        """
        expected = ['weighted_nlls']
        actual = self.options.cost_func_type
        self.assertEqual(expected, actual)

    def test_max_runtime_default(self):
        """
        Checks max_rutime default
        """
        expected = 600
        actual = self.options.max_runtime
        self.assertEqual(expected, actual)


class UserFittingOptionTests(unittest.TestCase):
    """
    Checks the fitting in the options file are set correctly or raise errors
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
                                 f'test_{opt_name}_valid.ini')
        with open(opts_file, 'w') as f:
            f.write(config_str)
        return opts_file

    def shared_valid(self, opt_name, options_set, config_str):
        """
        Shared test to check that the fitting option set is valid

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
        Shared test to check that the fitting option set is invalid

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
            "[FITTING]\nnum_minimizer_runs: 3"
        self.shared_invalid('num_minimizer_runs', config_str)

    def test_minimizer_num_runs_valid(self):
        """
        Checks user set num_runs is valid
        """
        set_option = 3
        config_str = \
            "[FITTING]\nnum_runs: 3"
        self.shared_valid('num_runs', set_option, config_str)

    def test_minimizer_num_runs_invalid(self):
        """
        Checks user set num_runs is invalid
        """
        config_str = \
            "[FITTING]\nnum_runs: two"
        self.shared_invalid('num_runs', config_str)

    def test_minimizer_algorithm_type_valid(self):
        """
        Checks user set algorithm_type is valid
        """
        set_option = ['general']
        config_str = \
            "[FITTING]\nalgorithm_type: general"
        self.shared_valid('algorithm_type', set_option, config_str)

    def test_minimizer_algorithm_type_invalid(self):
        """
        Checks user set algorithm_type is invalid
        """
        config_str = \
            "[FITTING]\nalgorithm_type: all_the_minimizers"
        self.shared_invalid('algorithm_type', config_str)

    def test_minimizer_jac_method_valid(self):
        """
        Checks user set jac_method is valid
        """
        set_option = ["analytic"]
        config_str = \
            "[FITTING]\njac_method: analytic"
        self.shared_valid('jac_method', set_option, config_str)

    def test_minimizer_jac_method_invalid(self):
        """
        Checks user set jac_method is invalid
        """
        config_str = \
            "[FITTING]\njac_method: NumPyFD"
        self.shared_invalid('jac_method', config_str)

    def test_minimizer_hes_method_valid(self):
        """
        Checks user set hes_method is valid
        """
        set_option = ["analytic"]
        config_str = \
            "[FITTING]\nhes_method: analytic"
        self.shared_valid('hes_method', set_option, config_str)

    def test_minimizer_hes_method_invalid(self):
        """
        Checks user set hes_method is invalid
        """
        config_str = \
            "[FITTING]\nhes_method: numpy"
        self.shared_invalid('hes_method', config_str)

    def test_minimizer_cost_func_type_valid(self):
        """
        Checks user set cost_func_type is valid
        """
        set_option = ["nlls"]
        config_str = \
            "[FITTING]\ncost_func_type: nlls"
        self.shared_valid('cost_func_type', set_option, config_str)

    def test_minimizer_cost_func_type_invalid(self):
        """
        Checks user set cost_func_type is invalid
        """
        config_str = \
            "[FITTING]\ncost_func_type: normal_dist"
        self.shared_invalid('cost_func_type', config_str)

    def test_minimizer_max_runtime_type_valid(self):
        """
        Checks user set max_runtime is valid
        """
        set_option = 10
        config_str = \
            "[FITTING]\nmax_runtime: 10"
        self.shared_valid('max_runtime', set_option, config_str)

    def test_minimizer_max_runtime_invalid(self):
        """
        Checks user set max_runtime is invalid
        """
        config_str = \
            "[FITTING]\nmax_runtime: 10 seconds"
        self.shared_invalid('max_runtime', config_str)
