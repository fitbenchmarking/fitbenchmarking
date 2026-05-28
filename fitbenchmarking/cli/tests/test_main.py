"""
This file contains unit tests for the main CLI script
"""

import argparse
import inspect
import os
from dataclasses import dataclass
from json import load
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from parameterized import parameterized

from fitbenchmarking import test_files
from fitbenchmarking.cli import main
from fitbenchmarking.controllers.scipy_controller import ScipyController
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import exceptions, fitbm_result
from fitbenchmarking.utils.misc import get_problem_files
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

    fitting_problem = parse_problem_file(fname, options)[0]
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


def get_default_args():
    return {
        "options_file": "",
        "problem_sets": ["/test/path"],
        "results_dir": "",
        "debug_mode": False,
        "num_runs": 0,
        "algorithm_type": [],
        "software": [],
        "jac_method": [],
        "cost_func_type": [],
        "runtime_metric": "",
        "port": 0,
        "ip_address": "",
        "make_plots": False,
        "dont_make_plots": False,
        "results_browser": False,
        "no_results_browser": False,
        "pbar": False,
        "no_pbar": False,
        "run_name": "",
        "comparison_mode": "",
        "table_type": [],
        "logging_file_name": "",
        "append_log": False,
        "overwrite_log": False,
        "level": "",
        "external_output": "",
        "load_checkpoint": False,
        "run_dash": False,
        "dont_run_dash": False,
        "check_jacobian": False,
        "dont_check_jacobian": False,
    }


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
            main.run(["examples/benchmark_problems/simple_tests"], debug=True)

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

    @patch("fitbenchmarking.cli.main.save_results")
    @patch("fitbenchmarking.utils.misc.get_problem_files")
    def test_checkpoint_file_on_fail(self, get_problems, save_results):
        """
        Checks that the checkpoint file is valid json if there's a crash.
        """
        get_problems.side_effect = lambda path: [get_problem_files(path)[0]]
        save_results.side_effect = RuntimeError(
            "Exception raised during save..."
        )

        with TemporaryDirectory() as results_dir:
            with self.assertRaises(RuntimeError):
                main.run(
                    ["examples/benchmark_problems/NIST/low_difficulty"],
                    additional_options={
                        "scipy_ls": ["lm-scipy"],
                        "software": ["scipy_ls"],
                        "num_runs": 1,
                        "results_dir": results_dir,
                    },
                    debug=True,
                )

            with open(f"{results_dir}/checkpoint.json", encoding="utf8") as f:
                # This will fail if the json is invalid
                contents = load(f)

        # Check that it's not empty
        self.assertTrue(contents)

    @dataclass
    class OptionMapping:
        cli_key: str
        cli_value: bool | str
        expected_output_key: str
        expected_output_value: bool | str = "test_value"

    valid_options = [
        OptionMapping("results_dir", "test_value", "results_dir"),
        OptionMapping("num_runs", "test_value", "num_runs"),
        OptionMapping("algorithm_type", "test_value", "algorithm_type"),
        OptionMapping("software", "test_value", "software"),
        OptionMapping("jac_method", "test_value", "jac_method"),
        OptionMapping("cost_func_type", "test_value", "cost_func_type"),
        OptionMapping("comparison_mode", "test_value", "comparison_mode"),
        OptionMapping("table_type", "test_value", "table_type"),
        OptionMapping("level", "test_value", "level"),
        OptionMapping("external_output", "test_value", "external_output"),
        OptionMapping("run_name", "test_value", "run_name"),
        OptionMapping("runtime_metric", "test_value", "runtime_metric"),
        OptionMapping("port", "test_value", "port"),
        OptionMapping("ip_address", "test_value", "ip_address"),
        OptionMapping("logging_file_name", "test_value", "file_name"),
        OptionMapping("make_plots", True, "make_plots", True),
        OptionMapping("dont_make_plots", True, "make_plots", False),
        OptionMapping("run_dash", True, "run_dash", True),
        OptionMapping("dont_run_dash", True, "run_dash", False),
        OptionMapping("pbar", True, "pbar", True),
        OptionMapping("no_pbar", True, "pbar", False),
        OptionMapping("append_log", True, "append", True),
        OptionMapping("overwrite_log", True, "append", False),
        OptionMapping("results_browser", True, "results_browser", True),
        OptionMapping("no_results_browser", True, "results_browser", False),
        OptionMapping("check_jacobian", True, "check_jacobian", True),
        OptionMapping("dont_check_jacobian", True, "check_jacobian", False),
    ]

    # format the data so that parameterized can add informative test names
    valid_options = [
        (f"{option.cli_key}_{option.cli_value}", option)
        for option in valid_options
    ]

    # _ used to discard the test name
    @parameterized.expand(valid_options)
    def test_cli_options_handled_correctly(self, _, option_mapping):
        """
        Tests that CLI options are correctly parsed by `parse_options_from_cli`
        """
        test_options = get_default_args()
        test_options[option_mapping.cli_key] = option_mapping.cli_value

        args = argparse.Namespace(**test_options)
        parsed_options = main.parse_options_from_cli(args)

        assert (
            parsed_options[option_mapping.expected_output_key]
            == option_mapping.expected_output_value
        )

    # _ used to discard the test name
    @parameterized.expand(valid_options)
    def test_cli_options_do_not_have_side_effects(self, _, option_mapping):
        """
        Test that when cli options are parsed, all of the other options are
        returned with their default value preseved.
        """

        # Get all of the default values
        expected_result = main.parse_options_from_cli(
            argparse.Namespace(**get_default_args())
        )

        test_options = get_default_args()
        test_options[option_mapping.cli_key] = option_mapping.cli_value

        args = argparse.Namespace(**test_options)
        parsed_options = main.parse_options_from_cli(args)

        # Test that excluding the option we changed, everything else is the
        # same as the default
        if option_mapping.expected_output_key in parsed_options:
            parsed_options.pop(option_mapping.expected_output_key)

        if option_mapping.expected_output_key in expected_result:
            expected_result.pop(option_mapping.expected_output_key)

        assert parsed_options == expected_result
