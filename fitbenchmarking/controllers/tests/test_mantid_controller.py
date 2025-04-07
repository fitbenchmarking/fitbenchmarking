"""
This file contains unit tests for the mantid controller.
"""

import inspect
from pathlib import Path
from unittest import TestCase
from unittest.mock import call, patch

import numpy as np
from parameterized import parameterized
from pytest import test_type as TEST_TYPE

from conftest import run_for_test_types
from fitbenchmarking import test_files
from fitbenchmarking.controllers.controller_factory import ControllerFactory
from fitbenchmarking.cost_func.hellinger_nlls_cost_func import (
    HellingerNLLSCostFunc,
)
from fitbenchmarking.cost_func.weighted_nlls_cost_func import (
    WeightedNLLSCostFunc,
)
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import exceptions
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
                False,
                1,
                [(0.0, 0.5), (0.0, 0.05)],
                ["A", "Sigma"],
                ("0.0 < f0.A < 0.5,0.0 < f0.Sigma < 0.05"),
            ),
            (
                False,
                True,
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
        is_composite_function,
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
        self.controller._is_composite_function = is_composite_function
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

    @parameterized.expand(
        [
            (
                Path("multifit_set") / "multifit.txt",
                (
                    "name=LinearBackground,A0=0,A1=0;"
                    " name=GausOsc,A=0.2,Sigma=0.2,Frequency=1,Phi=0"
                ),
                True,
                [
                    "f0.A0",
                    "f0.A1",
                    "f1.A",
                    "f1.Sigma",
                    "f1.Frequency",
                    "f1.Phi",
                ],
                2,
                True,
            ),
            (
                Path("all_parsers_set") / "trig_noisy-fba.txt",
                (
                    "name=UserFunction, Formula=A1*cos(2*3.141592*x) "
                    "+ A2*sin(2*3.141592*x) + A3*x, A1=1.01, A2=3.98, A3=3.01"
                ),
                False,
                [
                    "A1",
                    "A2",
                    "A3",
                ],
                1,
                False,
            ),
        ]
    )
    def test_init(
        self,
        file_path,
        mantid_equation,
        is_composite_function,
        param_names,
        dataset_count,
        multifit,
    ):
        """
        Verifies the attributes are set correctly when the
        class is initialized.
        """
        # Create the controller
        bench_prob_dir = Path(inspect.getfile(test_files)).resolve().parent
        fname = bench_prob_dir / file_path
        fitting_problem = parse_problem_file(fname, Options())
        fitting_problem.correct_data()
        cost_func = WeightedNLLSCostFunc(fitting_problem)
        controller = ControllerFactory.create_controller("mantid")
        controller = controller(cost_func)
        # Verify the attributes
        assert controller._cost_function == "Least squares"
        assert controller._mantid_equation == mantid_equation
        assert controller._is_composite_function == is_composite_function
        assert controller._param_names == param_names
        assert controller._status is None
        assert controller._dataset_count == dataset_count
        assert controller.problem.multifit == multifit
        if controller.problem.multifit:
            assert list(controller._added_args.keys()) == ["InputWorkspace_1"]
        else:
            assert controller._added_args == {}
        assert controller._mantid_function is None
        assert controller._mantid_results is None

    def test_init_raises_error(self):
        """
        Verifies the error is raised when cost function is not
        compatible with mantid.
        """
        bench_prob_dir = Path(inspect.getfile(test_files)).resolve().parent
        fname = bench_prob_dir / "multifit_set" / "multifit.txt"
        fitting_problem = parse_problem_file(fname, Options())
        fitting_problem.correct_data()
        cost_func = HellingerNLLSCostFunc(fitting_problem)
        controller = ControllerFactory.create_controller("mantid")
        with self.assertRaises(exceptions.ControllerAttributeError) as exp:
            _ = controller(cost_func)

        assert str(exp.exception) == (
            "Error in the controller attributes.\n"
            "Details: Mantid Controller does not "
            "support the requested cost function "
            "HellingerNLLSCostFunc"
        )

    @parameterized.expand(
        [
            (
                True,
                [[1.0], [2.0]],
                [np.array([3.0]), np.array([4.0])],
                [np.array([5.0]), np.array([6.0])],
                [np.array([7.0]), np.array([8.0])],
                [np.array([25.0]), np.array([25.0])],
            ),
            (
                True,
                [[1.0], [2.0]],
                None,
                None,
                None,
                [np.array([25.0]), np.array([25.0])],
            ),
            (
                False,
                [1.0],
                np.array([2]),
                np.array([3]),
                np.array([4]),
                np.array([25.0]),
            ),
        ]
    )
    @patch("fitbenchmarking.controllers.base_controller.Controller.eval_chisq")
    def test_eval_chisq(
        self,
        multifit,
        params,
        x_data,
        y_data,
        e_data,
        expected,
        mock_eval_chisq,
    ):
        """
        Verifies the eval_chisq method.
        """
        mock_eval_chisq.return_value = np.array([25.0])
        self.controller.problem.multifit = multifit
        assert (
            self.controller.eval_chisq(params, x_data, y_data, e_data)
            == expected
        )
        assert mock_eval_chisq.call_count == len(params)
        if multifit:
            if x_data is None:
                expected_calls = [call(p, None, None, None) for p in params]
            else:
                expected_calls = [
                    call(p, x, y, e)
                    for p, x, y, e in zip(params, x_data, y_data, e_data)
                ]
        else:
            expected_calls = [call(params, x_data, y_data, e_data)]
        assert mock_eval_chisq.call_args_list == expected_calls
