"""
This file contains unit tests for the main CLI script
"""

import inspect
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from fitbenchmarking import test_files
from fitbenchmarking.cli import main
from fitbenchmarking.controllers.scipy_controller import ScipyController
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import exceptions, fitbm_result
from fitbenchmarking.utils.options import Options


def make_controller(file_name="cubic.dat", minimizers=None):
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

    results: list[fitbm_result.FittingResult] = []
    controller.flag = 4
    controller.parameter_set = 0
    result = fitbm_result.FittingResult(controller=controller)
    results.append(result)

    failed_problems: list[str] = []
    unselected_minimizers = {}
    return results, failed_problems, unselected_minimizers


class TestMain(TestCase):
    """
    Tests for main.py
    """

    @patch("fitbenchmarking.cli.main.Fit.benchmark")
    def test_check_no_results_produced(self, benchmark):
        """
        Checks that exception is raised if no results are produced
        """
        benchmark.return_value = ([], [], {})

        with self.assertRaises(exceptions.NoResultsError):
            main.run(
                ["examples/benchmark_problems/simple_tests"],
                os.path.dirname(__file__),
                debug=True,
            )

    @patch("fitbenchmarking.cli.main.Fit.benchmark")
    def test_all_dummy_results_produced(self, benchmark):
        """
        Checks that exception is raised if all dummy results
        """
        benchmark.side_effect = mock_func_call

        with self.assertRaises(exceptions.NoResultsError):
            main.run(
                ["examples/benchmark_problems/simple_tests"],
                os.path.dirname(__file__),
                debug=True,
            )

    @patch("pathlib.Path.joinpath")
    @patch("sys.argv", new=["fitbenchmarking"])
    def test_file_path_exception_raised(self, mock):
        """
        Checks that SystemExit exception is raised if default
        problem set has been deleted or moved.
        """
        mock.return_value = Path("my/test/path")
        with self.assertRaises(SystemExit) as exp:
            main.main()
        self.assertEqual(exp.exception.code, 1)
