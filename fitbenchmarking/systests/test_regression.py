"""
Test that accuracy of FitBenchmarking is consistent with previous versions
"""

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

import os
from sys import platform
from tempfile import NamedTemporaryFile
from unittest import TestCase
from pytest import test_type as TEST_TYPE  # pylint: disable=no-name-in-module
from conftest import run_for_test_types

from fitbenchmarking.cli.main import run
from fitbenchmarking.utils.options import Options


@run_for_test_types(TEST_TYPE, 'all')
class TestRegressionAll(TestCase):
    """
    Regression tests for the Fitbenchmarking software with all fitting software
    packages
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """
        results_dir = os.path.join(os.path.dirname(__file__),
                                   'fitbenchmarking_results')

        opt_file_name = create_options_file()
        problem = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               'mock_problems',
                                               'all_parsers_set'))
        run([problem], results_dir, options_file=opt_file_name,
            debug=True)
        os.remove(opt_file_name)

        opt_file_name = create_options_file(multi_fit=True)
        problem = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               'mock_problems',
                                               'multifit_set'))
        run([problem], results_dir, options_file=opt_file_name,
            debug=True)
        os.remove(opt_file_name)

    def test_results_consistent_all(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """

        expected_file = os.path.join(os.path.dirname(__file__),
                                     '{}_expected_results'.format(platform),
                                     'all_parsers.txt')

        actual_file = \
            os.path.join(os.path.dirname(__file__),
                         'fitbenchmarking_results',
                         'all_parsers_set',
                         'acc_table.txt')

        with open(expected_file, 'r') as f:
            expected = f.readlines()

        with open(actual_file, 'r') as f:
            actual = f.readlines()

        diff, msg = diff_result(actual, expected)
        self.assertListEqual([], diff, msg)

    def test_multifit_consistent(self):
        """
        Regression testing that the results of fitting multifit problems
        against a single minimizer from mantid.
        """

        expected_file = os.path.join(os.path.dirname(__file__),
                                     '{}_expected_results'.format(platform),
                                     'multifit.txt')

        actual_file = os.path.join(os.path.dirname(__file__),
                                   'fitbenchmarking_results',
                                   'multifit_set',
                                   'acc_table.txt')

        with open(expected_file, 'r') as f:
            expected = f.readlines()

        with open(actual_file, 'r') as f:
            actual = f.readlines()

        diff, msg = diff_result(actual, expected)
        self.assertListEqual([], diff, msg)


@run_for_test_types(TEST_TYPE, 'matlab')
class TestRegressionMatlab(TestCase):
    """
    Regression tests for the Fitbenchmarking software with
    matlab fitting software
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """
        results_dir = os.path.join(os.path.dirname(__file__),
                                   'fitbenchmarking_results')

        opt_file_name = create_options_file()
        problem = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               'mock_problems',
                                               'all_parsers_set'))
        run([problem], results_dir, options_file=opt_file_name,
            debug=True)
        os.remove(opt_file_name)

    def test_results_consistent_all(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """

        expected_file = os.path.join(os.path.dirname(__file__),
                                     '{}_expected_results'.format(platform),
                                     'matlab.txt')

        actual_file = \
            os.path.join(os.path.dirname(__file__),
                         'fitbenchmarking_results',
                         'all_parsers_set',
                         'acc_table.txt')

        with open(expected_file, 'r') as f:
            expected = f.readlines()

        with open(actual_file, 'r') as f:
            actual = f.readlines()

        diff, msg = diff_result(actual, expected)
        self.assertListEqual([], diff, msg)


@run_for_test_types(TEST_TYPE, 'default')
class TestRegressionDefault(TestCase):
    """
    Regression tests for the Fitbenchmarking software with all default fitting
    software packages
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """
        results_dir = os.path.join(os.path.dirname(__file__),
                                   'fitbenchmarking_results')

        opt_file_name = create_options_file()
        problem = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               'mock_problems',
                                               'default_parsers'))

        run([problem], results_dir, options_file=opt_file_name,
            debug=True)
        os.remove(opt_file_name)

    def test_results_consistent(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """

        expected_file = os.path.join(os.path.dirname(__file__),
                                     '{}_expected_results'.format(platform),
                                     'default_parsers.txt')
        actual_file = \
            os.path.join(os.path.dirname(__file__),
                         'fitbenchmarking_results',
                         'default_parsers',
                         'acc_table.txt')

        with open(expected_file, 'r') as f:
            expected = f.readlines()

        with open(actual_file, 'r') as f:
            actual = f.readlines()

        diff, msg = diff_result(actual, expected)
        self.assertListEqual([], diff, msg)


def diff_result(actual, expected):
    """
    Return the lines which differ between expected and actual along with a
    formatted message.

    :param expected: The expected result
    :type expected: list of strings
    :param actual: The actual result
    :type actual: list of strings
    :return: The lines which differ and a formatted message
    :rtype: list of list of strings and str
    """
    diff = []
    for i, (exp_line, act_line) in enumerate(
            zip_longest(expected, actual)):
        exp_line = '' if exp_line is None else exp_line.strip('\n')
        act_line = '' if act_line is None else act_line.strip('\n')
        if exp_line != act_line:
            diff.append([i, exp_line, act_line])

    msg = '\n\nOutput has changed in {} '.format(len(diff)) \
          + 'minimizer-problem pairs. \n' \
          + '\n'.join(['== Line {} ==\n'
                       'Expected :{}\n'
                       'Actual   :{}'.format(*line_change)
                       for line_change in diff])
    if diff != []:
        print("\n==\n")
        print("Output generated (also saved as actual.out):")
        with open("actual.out", "w") as outfile:
            for line in actual:
                print(line)
                outfile.write(line)
    return diff, msg


def setup_options(multi_fit=False) -> Options:
    """
    Setups up options class for system tests

    :param multi_fit: Whether or not you are testing multi fitting.
    :type multi_fit: bool

    :return: Fitbenchmarking options file for tests
    :rtype: fitbenchmarking.utils.options.Options
    """
    opts = Options()
    opts.num_runs = 1
    opts.make_plots = False

    # The software to test for the different test types
    # 'gradient_free' and 'scipy_go' are left out as they require bounds
    # 'dfo' is left out for now as it gives unreliable results
    software = {"all": ["bumps", "gsl", "levmar", "mantid",
                        "minuit", "ralfit", "scipy", "scipy_ls"],
                "default": ["bumps", "scipy", "scipy_ls"],
                "matlab": ["matlab", "matlab_curve", "matlab_opt",
                           "matlab_stats"]}

    # The minimizers to test for each software
    minimizers = {"bumps": "lm-bumps",
                  "gsl": "lmsder",
                  "levmar": "levmar",
                  "mantid": "Levenberg-Marquardt",
                  "matlab": "Nelder-Mead Simplex",
                  "matlab_curve": "Levenberg-Marquardt",
                  "matlab_opt": "levenberg-marquardt",
                  "matlab_stats": "Levenberg-Marquardt",
                  "minuit": "minuit",
                  "ralfit": "hybrid",
                  "scipy": "Nelder-Mead",
                  "scipy_ls": "lm-scipy"}

    opts.software = software.get(TEST_TYPE) if not multi_fit else ["mantid"]
    opts.minimizers = {s: [minimizers[s]] for s in opts.software}
    return opts


def create_options_file(**kwargs):
    """
    Creates a temporary options file and returns its name.

    :return: Name of the temporary options file.
    :rtype: str
    """
    opts = setup_options(**kwargs)
    with NamedTemporaryFile(suffix='.ini', mode='w',
                            delete=False) as opt_file:
        opts.write_to_stream(opt_file)
        name = opt_file.name
    return name
