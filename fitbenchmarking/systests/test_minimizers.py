"""
Test that accuracy of a single minimizer for each fitting software is
consistent with previous versions
"""

import os
from unittest import TestCase

from fitbenchmarking.cli.main import run
from fitbenchmarking.utils.options import Options


class TestMinimizers(TestCase):
    """
    Test that the minimizers are consistent.
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """

        opts = Options()
        opts.minimizers = {k: v[0] for k, v in opts.minimizers.items()}
        opts.results_dir = os.path.join(os.path.dirname(__file__), 'results')

        opt_file = os.path.join(os.path.dirname(__file__), 'test_options.ini')
        opts.write(opt_file)

        cd = os.path.abspath(os.curdir)

        problem_set_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, 'examples',
            'benchmark_problems'))
        os.chdir(problem_set_dir)
        run(['simple_tests'], options_file=opt_file)
        os.chdir(cd)

    def test_minimizers_consistent(self):
        """
        Compare the results with the expected
        """

        expected_file = os.path.join(
            os.path.dirname(__file__), 'expected_results', 'minimizers.rst')

        actual_file = os.path.join(
            os.path.dirname(__file__), 'results', 'simple_tests',
            'simple_tests_acc_weighted_table.rst')

        with open(expected_file, 'r') as f:
            expected = f.readlines()

        with open(actual_file, 'r') as f:
            actual = f.readlines()

        self.assertListEqual(expected, actual)
