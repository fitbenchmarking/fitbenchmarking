"""
This file contains unit tests for the main CLI script
"""
from unittest import TestCase
from unittest.mock import patch
import os
import inspect

from fitbenchmarking.cli import main
from fitbenchmarking import mock_problems
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.utils import fitbm_result, exceptions
from fitbenchmarking.utils.options import Options
from fitbenchmarking.parsing.parser_factory import parse_problem_file


def make_cost_function(file_name='cubic.dat', minimizers=None):
    """
    Helper function that returns a simple fitting problem
    """
    options = Options()
    if minimizers:
        options.minimizers = minimizers

    bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
    fname = os.path.join(bench_prob_dir, file_name)

    fitting_problem = parse_problem_file(fname, options)
    fitting_problem.correct_data()
    cost_func = NLLSCostFunc(fitting_problem)
    return cost_func


def mock_func_call(*args, **kwargs):
    """
    Mock function to be used instead of benchmark
    """
    options = Options()
    cost_func = make_cost_function()

    results = []
    result_args = {'options': options,
                   'cost_func': cost_func,
                   'jac': 'jac',
                   'hess': 'hess',
                   'initial_params': [],
                   'params': [],
                   'error_flag': 4}
    result = fitbm_result.FittingResult(**result_args)
    results.append(result)

    failed_problems = []
    unselected_minimizers = {}
    return results, failed_problems, unselected_minimizers


class TestMain(TestCase):
    """
    Tests for main.py
    """

    @patch('fitbenchmarking.cli.main.benchmark')
    def test_check_no_results_produced(self, benchmark):
        """
        Checks that exception is raised if no results are produced
        """
        benchmark.return_value = ([], [], {})

        with self.assertRaises(exceptions.NoResultsError):
            main.run(['examples/benchmark_problems/simple_tests'],
                     os.path.dirname(__file__), debug=True)

    @patch('fitbenchmarking.cli.main.benchmark')
    def test_all_dummy_results_produced(self, benchmark):
        """
        Checks that exception is raised if all dummy results
        """
        benchmark.side_effect = mock_func_call

        with self.assertRaises(exceptions.NoResultsError):
            main.run(['examples/benchmark_problems/simple_tests'],
                     os.path.dirname(__file__), debug=True)
