"""
This file contains unit tests for the main CLI script
"""
import inspect
import os
from json import load
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from fitbenchmarking import test_files
from fitbenchmarking.cli import main
from fitbenchmarking.controllers.scipy_controller import ScipyController
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import exceptions, fitbm_result
from fitbenchmarking.utils.misc import get_problem_files
from fitbenchmarking.utils.options import Options


def make_controller(file_name='cubic.dat', minimizers=None):
    """
    Helper function that returns a simple fitting problem
    in a scipy controller.
    """
    options = Options()
    if minimizers:
        options.minimizers = minimizers

    bench_prob_dir = os.path.dirname(inspect.getfile(test_files))
    fname = os.path.join(bench_prob_dir, file_name)

    fitting_problem = parse_problem_file(fname, options)
    fitting_problem.correct_data()
    cost_func = NLLSCostFunc(fitting_problem)

    controller = ScipyController(cost_func)
    return controller


def mock_func_call(*args, **kwargs):
    """
    Mock function to be used instead of benchmark
    """
    controller = make_controller()

    results: 'list[fitbm_result.FittingResult]' = []
    controller.flag = 4
    controller.parameter_set = 0
    result = fitbm_result.FittingResult(controller=controller)
    results.append(result)

    failed_problems: 'list[str]' = []
    unselected_minimizers = {}
    return results, failed_problems, unselected_minimizers


class TestMain(TestCase):
    """
    Tests for main.py
    """

    @patch('fitbenchmarking.cli.main.Fit.benchmark')
    def test_check_no_results_produced(self, benchmark):
        """
        Checks that exception is raised if no results are produced
        """
        benchmark.return_value = ([], [], {})

        with self.assertRaises(exceptions.NoResultsError):
            main.run(['examples/benchmark_problems/simple_tests'],
                     debug=True)

    @patch('fitbenchmarking.cli.main.Fit.benchmark')
    def test_all_dummy_results_produced(self, benchmark):
        """
        Checks that exception is raised if all dummy results
        """
        benchmark.side_effect = mock_func_call

        with self.assertRaises(exceptions.NoResultsError):
            main.run(['examples/benchmark_problems/simple_tests'],
                     debug=True)

    @patch('fitbenchmarking.cli.main.save_results')
    @patch('fitbenchmarking.utils.misc.get_problem_files')
    def test_checkpoint_file_on_fail(self, get_problems, save_results):
        """
        Checks that the checkpoint file is valid json if there's a crash.
        """
        get_problems.side_effect = lambda path: [get_problem_files(path)[0]]
        save_results.side_effect = RuntimeError(
            "Exception raised during save...")

        with TemporaryDirectory() as results_dir:
            with self.assertRaises(RuntimeError):
                main.run(['examples/benchmark_problems/NIST/low_difficulty'],
                         additional_options={'scipy_ls': ['lm-scipy'],
                                             'software': ['scipy_ls'],
                                             'num_runs': 1,
                                             'results_dir': results_dir},
                         debug=True)

            with open(f'{results_dir}/checkpoint.json', encoding='utf8') as f:
                # This will fail if the json is invalid
                contents = load(f)

        # Check that it's not empty
        self.assertTrue(contents)
