"""
Test that accuracy of FitBenchmarking is consistent with previous versions
"""

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
import os
import tempfile
from unittest import TestCase

from fitbenchmarking.cli.main import run
from fitbenchmarking.utils.options import Options


class TestRegression(TestCase):
    """
    Regression tests for the Fitbenchmarking software
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """

        # Get defaults which should have minimizers for every software
        opts = Options()
        opts.num_runs = 1
        # Use only the first minimizer for each software
        opts.minimizers = {k: [v[0]] for k, v in opts.minimizers.items()}
        # Get a list of all softwares
        # (sorted to ensure it is the same order as expected)
        opts.software = sorted(opts.minimizers.keys())
        opts.results_dir = os.path.join(os.path.dirname(__file__), 'results')

        opt_file = tempfile.NamedTemporaryFile(suffix='.ini')
        opts.write(opt_file.name)

        problem = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               'mock_problems',
                                               'all_parsers_set'))
        run([problem], options_file=opt_file.name, debug=True)

        opts.software = ['mantid']
        opts.write(opt_file.name)
        problem = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               'mock_problems',
                                               'multifit_set'))
        run([problem], options_file=opt_file.name, debug=True)

    def test_results_consistent(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimiser from each of
        the supported softwares
        """

        expected_file = os.path.join(os.path.dirname(__file__),
                                     'expected_results',
                                     'all_parsers.txt')

        actual_file = os.path.join(os.path.dirname(__file__),
                                   'results',
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
        against a single minimiser from mantid.
        """

        expected_file = os.path.join(os.path.dirname(__file__),
                                     'expected_results',
                                     'multifit.txt')

        actual_file = os.path.join(os.path.dirname(__file__),
                                   'results',
                                   'multifit_set',
                                   'multifit_set_acc_weighted_table.txt')

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
