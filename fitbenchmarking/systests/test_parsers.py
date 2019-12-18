"""
Test that accuracy of a single parser for each fitting software is
consistent with previous versions
"""

import os
from unittest import TestCase

from fitbenchmarking.cli.main import run
from fitbenchmarking.utils.options import Options


class TestParsers(TestCase):
    """
    Test that the parsers are consistent.
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """

        opts = Options()
        opts.minimizers = {k: v[0] for k, v in opts.minimizers.items()}
        opts.software = ['scipy']
        opts.results_dir = os.path.join(os.path.dirname(__file__), 'results')

        opt_file = os.path.join(
            os.path.dirname(__file__), 'test_parsers_options.ini')
        opts.write(opt_file)

        cd = os.path.abspath(os.curdir)

        problem_set_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), os.pardir, 'mock_problems'))
        os.chdir(problem_set_dir)
        run(['all_parser_test_set'], options_file=opt_file)
        os.chdir(cd)

    def test_minimizers_consistent(self):
        """
        Compare the results with the expected
        """

        expected_file = os.path.join(
            os.path.dirname(__file__), 'expected_results', 'parsers.rst')

        actual_file = os.path.join(
            os.path.dirname(__file__), 'results', 'all_parser_test_set',
            'all_parser_test_set_acc_weighted_table.rst')

        with open(expected_file, 'r') as f:
            expected = f.readlines()

        with open(actual_file, 'r') as f:
            actual = f.readlines()

        diff = []
        for i in range(len(expected)):
            if expected[i] != actual[i]:
                diff.append([expected[i], actual[i]])

        num_diff = min(6, len(diff))
        msg = 'Accuracy has changed in at least 1 parser ' \
              + 'with scipy. \n' \
              + 'First {} of {} differences: \n'.format(num_diff, len(diff)) \
              + '\n'.join(['{} \n{}'.format(*diff[i])
                           for i in range(num_diff)])
        self.assertListEqual(expected, actual, msg)
