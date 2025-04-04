"""
This file contains unit tests for the mantid controller.
"""

import inspect
from pathlib import Path
from unittest import TestCase

from parameterized import parameterized
from pytest import test_type as TEST_TYPE

from conftest import run_for_test_types
from fitbenchmarking import test_files
from fitbenchmarking.controllers.controller_factory import ControllerFactory
from fitbenchmarking.cost_func.weighted_nlls_cost_func import (
    WeightedNLLSCostFunc,
)
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.options import Options


@run_for_test_types(TEST_TYPE, "all")
class TestMantidController(TestCase):
    """
    Unit tests the MantidController class.
    """

    def setUp(self):
        """
        Set up resources before each test case.
        """
        bench_prob_dir = Path(inspect.getfile(test_files)).resolve().parent
        fname = bench_prob_dir / "multifit_set" / "multifit.txt"
        fitting_problem = parse_problem_file(fname, Options())
        fitting_problem.correct_data()
        cost_func = WeightedNLLSCostFunc(fitting_problem)
        controller = ControllerFactory.create_controller("mantid")
        self.controller = controller(cost_func)

    @parameterized.expand(
        [
            (
                True,
                4,
                [(0.0, 0.2), (0.0, 0.5), (0.0, 0.05), (0.0, 5.0), (0.0, 0.05)],
                ["f0.A0", "f1.A", "f1.Sigma", "f1.Frequency", "f1.Phi"],
                (
                    "0.0 < f0.f0.A0 < 0.2,0.0 < f1.f0.A0 < 0.2,0.0 < f2.f0.A0 "
                    "< 0.2,0.0 < f3.f0.A0 < 0.2,0.0 < f0.f1.A < 0.5,0.0 "
                    "< f1.f1.A < 0.5,0.0 < f2.f1.A < 0.5,0.0 < f3.f1.A < "
                    "0.5,0.0 < f0.f1.Sigma < 0.05,0.0 < f1.f1.Sigma < "
                    "0.05,0.0 < f2.f1.Sigma < 0.05,0.0 < f3.f1.Sigma < "
                    "0.05,0.0 < f0.f1.Frequency < 5.0,0.0 < f1.f1.Frequency"
                    " < 5.0,0.0 < f2.f1.Frequency < 5.0,0.0 < f3.f1.Frequency"
                    " < 5.0,0.0 < f0.f1.Phi < 0.05,0.0 < f1.f1.Phi < 0.05,0.0"
                    " < f2.f1.Phi < 0.05,0.0 < f3.f1.Phi < 0.05"
                ),
            ),
            (
                False,
                1,
                [(0.0, 0.5), (0.0, 0.05)],
                ["f0.A", "f0.Sigma"],
                ("0.0 < f0.A < 0.5,0.0 < f0.Sigma < 0.05"),
            ),
            (
                False,
                1,
                [(0.0, 0.2), (0.0, 0.5), (0.0, 0.05)],
                ["f0.A0", "f1.A", "f1.Sigma"],
                ("0.0 < f0.A0 < 0.2,0.0 < f1.A < 0.5,0.0 < f1.Sigma < 0.05"),
            ),
        ]
    )
    def test_get_constraint_str(
        self,
        is_multifit,
        dataset_count,
        value_ranges,
        param_names,
        expected,
    ):
        """
        Verifies the output of _get_constraint_str() method.
        """
        self.controller._dataset_count = dataset_count
        self.controller.value_ranges = value_ranges
        self.controller._param_names = param_names
        self.controller.problem.multifit = is_multifit
        result = self.controller._get_constraint_str()
        assert result == expected

    @parameterized.expand(
        [
            (["A1"], 2, "f1.A1=f0.A1"),
            (
                ["f1.Sigma", "f1.Frequency"],
                4,
                "f1.f1.Sigma=f0.f1.Sigma,"
                "f2.f1.Sigma=f0.f1.Sigma,"
                "f3.f1.Sigma=f0.f1.Sigma,"
                "f1.f1.Frequency=f0.f1.Frequency,"
                "f2.f1.Frequency=f0.f1.Frequency,"
                "f3.f1.Frequency=f0.f1.Frequency",
            ),
        ]
    )
    def test_get_ties_str(
        self,
        ties,
        dataset_count,
        expected,
    ):
        """
        Verifies the output of _get_ties_str() method.
        """
        self.controller.problem.additional_info["mantid_ties"] = ties
        self.controller._dataset_count = dataset_count
        assert self.controller._get_ties_str() == expected
