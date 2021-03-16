from unittest import TestCase
from unittest.mock import patch

from fitbenchmarking.cli import main
from fitbenchmarking.utils import exceptions


class TestMain(TestCase):
    """
    Tests for main.py
    """

    @patch('fitbenchmarking.cli.main.benchmark')
    def test_check_no_results_produced(self, benchmark):
        """
        Checks that exception is raised if no results are produced
        """
        benchmark.return_value = ([], [], {}, '')

        with self.assertRaises(exceptions.NoResultsError):
            main.run(['examples/benchmark_problems/simple_tests'], debug=True)
