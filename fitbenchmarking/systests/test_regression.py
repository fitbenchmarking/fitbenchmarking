"""
Test that accuracy of FitBenchmarking is consistent with previous versions
"""

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
import os
from sys import platform
import tempfile
from unittest import TestCase
import pytest
from pytest import test_type as TEST_TYPE

from fitbenchmarking.cli.main import run
from fitbenchmarking.utils.options import Options


@pytest.mark.skipif("TEST_TYPE == 'default'")
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
        opts = setup_options()
        opt_file = tempfile.NamedTemporaryFile(suffix='.ini',
                                               mode='w',
                                               delete=False)
        opts.write_to_stream(opt_file)
        opt_file.close()
        problem = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               'mock_problems',
                                               'all_parsers_set'))
        run([problem], options_file=opt_file.name, debug=True)
        os.remove(opt_file.name)
        opts = setup_options(multifit=True)
        opt_file = tempfile.NamedTemporaryFile(suffix='.ini',
                                               mode='w',
                                               delete=False)
        opts.write_to_stream(opt_file)
        opt_file.close()
        problem = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               'mock_problems',
                                               'multifit_set'))
        run([problem], options_file=opt_file.name, debug=True)
        os.remove(opt_file.name)

    def test_results_consistent_all(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """

        expected_file = os.path.join(os.path.dirname(__file__),
                                     '{}_expected_results'.format(platform),
                                     'all_parsers.txt')

        actual_file = os.path.join(os.path.dirname(__file__),
                                   'fitbenchmarking_results',
                                   'all_parsers_set',
                                   'all_parsers_set_acc_weighted_table.txt')

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
                                   'multifit_set_acc_weighted_table.txt')

        with open(expected_file, 'r') as f:
            expected = f.readlines()

        with open(actual_file, 'r') as f:
            actual = f.readlines()

        diff, msg = diff_result(actual, expected)
        self.assertListEqual([], diff, msg)


@pytest.mark.skipif("TEST_TYPE == 'all'")
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

        # Get defaults which should have minimizers for every software
        opts = setup_options()
        opt_file = tempfile.NamedTemporaryFile(suffix='.ini',
                                               mode='w',
                                               delete=False)
        # while opt_file is open it cannot be reoponed on Windows NT or later
        # and hence option available is to write to the stream directly
        opts.write_to_stream(opt_file)
        opt_file.close()
        problem = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               'mock_problems',
                                               'default_parsers'))

        run([problem], options_file=opt_file.name, debug=True)
        os.remove(opt_file.name)

    def test_results_consistent(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """

        expected_file = os.path.join(os.path.dirname(__file__),
                                     '{}_expected_results'.format(platform),
                                     'default_parsers.txt')

        actual_file = os.path.join(os.path.dirname(__file__),
                                   'fitbenchmarking_results',
                                   'default_parsers',
                                   'default_parsers_acc_weighted_table.txt')

        with open(expected_file, 'r') as f:
            expected = f.readlines()

        with open(actual_file, 'r') as f:
            actual = f.readlines()

        diff, msg = diff_result(actual, expected)
        self.assertListEqual([], diff, msg)


def diff_result(expected, actual):
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
    for exp_line, act_line in zip_longest(expected, actual):
        exp_line = '' if exp_line is None else exp_line.strip('\n')
        act_line = '' if act_line is None else act_line.strip('\n')
        if exp_line != act_line:
            diff.append([exp_line, act_line])

    num_diff = min(6, len(diff))
    msg = 'Accuracy has changed in at least 1 minimizer-' \
          + 'problem pair. \n' \
          + 'First {} of {} differences: \n'.format(num_diff, len(diff)) \
          + '\n'.join(['{} \n{}'.format(*diff[i])
                       for i in range(num_diff)])
    return diff, msg


def setup_options(multifit=False):
    """
    Setups up options class for system tests

    :return: Fitbenchmarking options file for tests
    :rtype: fitbenchmarking.utils.options.Options
    """

    # Get defaults which should have minimizers for every software
    opts = Options()
    opts.num_runs = 1
    opts.make_plots = False
    # Use only the first minimizer from the selected software packages
    if multifit:
        opts.software = ['mantid']
        opts.minimizers = {'mantid': [opts.minimizers['mantid'][0]]}
    elif TEST_TYPE != "default":
        opts.software = ['bumps', 'dfo', 'gsl', 'mantid', 'minuit',
                         'ralfit', 'scipy', 'scipy_ls']
        opts.minimizers = {k: [v[0]] for k, v in opts.minimizers.items()}
    else:
        opts.software = ['bumps', 'dfo', 'minuit', 'scipy', 'scipy_ls']
        opts.minimizers = {s: [opts.minimizers[s][0]] for s in opts.software}

    opts.results_dir = os.path.join(os.path.dirname(__file__),
                                    'fitbenchmarking_results')

    return opts
