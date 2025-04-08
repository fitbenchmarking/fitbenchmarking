"""
This file contains unit tests for the mantid controller.
"""

import inspect
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

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
    def test_get_constraints_str(
        self,
        is_multifit,
        is_composite_function,
        dataset_count,
        value_ranges,
        param_names,
        expected,
    ):
        """
        Verifies the output of _get_constraints_str() method.
        """
        self.controller._dataset_count = dataset_count
        self.controller.value_ranges = value_ranges
        self.controller._param_names = param_names
        self.controller.problem.multifit = is_multifit
        self.controller._is_composite_function = is_composite_function
        result = self.controller._get_constraints_str()
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
        result = self.controller.eval_chisq(params, x_data, y_data, e_data)
        assert result == expected
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

    @parameterized.expand(
        [
            (
                "name=LinearBackground,A0=0,A1=0",
                False,
                False,
                [(0, 1), (0, 2)],
                1,
                1,
                0,
                "name=LinearBackground,A0=0,A1=0; constraints=(constraints)",
            ),
            (
                "name=LinearBackground,A0=0,A1=0",
                True,
                False,
                [(0, 1), (0, 2)],
                2,
                1,
                1,
                (
                    "composite=MultiDomainFunction, NumDeriv=1;"
                    "name=LinearBackground,A0=0,A1=0, $domains=i; "
                    "name=LinearBackground,A0=0,A1=0, $domains=i; "
                    "ties=(ties); constraints=(constraints)"
                ),
            ),
            (
                (
                    "name=LinearBackground,A0=0,A1=0;"
                    " name=GausOsc,A=0.2,Sigma=0.2,Frequency=1,Phi=0"
                ),
                True,
                True,
                None,
                2,
                0,
                1,
                (
                    "composite=MultiDomainFunction, NumDeriv=1; "
                    "(composite=CompositeFunction, NumDeriv=false, $domains=i;"
                    " name=LinearBackground,A0=0,A1=0; "
                    "name=GausOsc,A=0.2,Sigma=0.2,Frequency=1,Phi=0); "
                    "(composite=CompositeFunction, NumDeriv=false, $domains=i;"
                    " name=LinearBackground,A0=0,A1=0; "
                    "name=GausOsc,A=0.2,Sigma=0.2,Frequency=1,Phi=0);ties=(ties)"
                ),
            ),
        ]
    )
    @patch(
        "fitbenchmarking.controllers.mantid_controller.MantidController._get_ties_str"
    )
    @patch(
        "fitbenchmarking.controllers.mantid_controller.MantidController._get_constraints_str"
    )
    def test_setup_mantid(
        self,
        mantid_equation,
        multifit,
        is_composite_function,
        value_ranges,
        dataset_count,
        constraint_count,
        ties_count,
        expected,
        constraint_mock,
        ties_mock,
    ):
        """
        Verifies the output of the _setup_mantid method.
        """
        constraint_mock.return_value = "constraints"
        ties_mock.return_value = "ties"
        self.controller.problem.multifit = multifit
        self.controller.value_ranges = value_ranges
        self.controller._mantid_equation = mantid_equation
        self.controller._is_composite_function = is_composite_function
        self.controller._dataset_count = dataset_count

        assert self.controller._setup_mantid() == expected
        assert constraint_mock.call_count == constraint_count
        assert ties_mock.call_count == ties_count

    def test_setup_mantid_dev(self):
        """
        Verifies the output of the _setup_mantid_dev method.
        """
        self.controller._param_names = ["A", "Sigma"]
        self.controller.initial_params = [1.0, 2.0]
        mock_jacobian = MagicMock()
        mock_jacobian.use_default_jac = False
        self.controller.cost_func.jacobian = mock_jacobian
        assert (
            self.controller._setup_mantid_dev()
            == "name=fitFunction, A=1.0, Sigma=2.0"
        )

    def test_fitfunction_init(self):
        """
        Verifies the fitFunction init method.
        """
        self.controller._param_names = ["A"]
        self.controller.initial_params = [1.0]
        self.controller.value_ranges = [(0, 2)]

        mock_jacobian = MagicMock()
        mock_jacobian.use_default_jac = False
        self.controller.cost_func.jacobian = mock_jacobian

        FitFunc = self.controller._setup_mantid_dev(return_class=True)
        mock_ff_self = MagicMock()
        FitFunc.init(mock_ff_self)

        mock_ff_self.declareParameter.assert_called_with("A")
        mock_ff_self.addConstraints.assert_called_with("0 < A < 2")

    def test_fitfunction_function1D(self):
        """
        Verifies the fitFunction function1D method.
        """
        self.controller._param_names = ["A", "B"]
        self.controller.initial_params = [1.0, 2.0]
        self.controller.problem.eval_model = MagicMock(
            return_value=np.array([42.0])
        )

        mock_jacobian = MagicMock()
        mock_jacobian.use_default_jac = False
        self.controller.cost_func.jacobian = mock_jacobian

        FitFunc = self.controller._setup_mantid_dev(return_class=True)
        mock_ff_self = MagicMock()
        mock_ff_self.getParameterValue.side_effect = [3.0, 4.0]

        result = FitFunc.function1D(mock_ff_self, np.array([5.0, 6.0]))
        _, call_arg = self.controller.problem.eval_model.call_args

        np.testing.assert_array_equal(call_arg["x"], np.array([5.0, 6.0]))
        np.testing.assert_array_equal(call_arg["params"], np.array([3.0, 4.0]))
        np.testing.assert_array_equal(result, np.array([42.0]))

    def test_fitfunction_functionDeriv1D(self):
        """
        Verifies the fitFunction functionDeriv1D method.
        """
        self.controller._param_names = ["A", "B"]
        self.controller.initial_params = [1.0, 2.0]

        mock_jacobian = MagicMock()
        mock_jacobian.use_default_jac = False
        self.controller.cost_func.jacobian = mock_jacobian
        self.controller.cost_func.jacobian.eval.return_value = np.array(
            [[1.0, 2.0], [3.0, 4.0]]
        )

        FitFunc = self.controller._setup_mantid_dev(return_class=True)

        mock_ff_self = MagicMock()
        mock_ff_self.getParameterValue.side_effect = [5.0, 6.0]
        jacobian = MagicMock()

        FitFunc.functionDeriv1D(mock_ff_self, np.array([10.0, 20.0]), jacobian)

        call_arg = self.controller.cost_func.jacobian.eval.call_args[0][0]
        np.testing.assert_array_equal(call_arg, np.array([5.0, 6.0]))
        jacobian.set.assert_any_call(0, 0, 1.0)
        jacobian.set.assert_any_call(0, 1, 2.0)
        jacobian.set.assert_any_call(1, 0, 3.0)
        jacobian.set.assert_any_call(1, 1, 4.0)

    @parameterized.expand(
        [
            (None, 0, 1),
            ("test", 1, 0),
        ]
    )
    @patch(
        "fitbenchmarking.controllers.mantid_controller.MantidController._setup_mantid_dev"
    )
    @patch(
        "fitbenchmarking.controllers.mantid_controller.MantidController._setup_mantid"
    )
    def test_setup(
        self,
        mantid_equation,
        mock_setup_mantid_count,
        mock_setup_mantid_dev_count,
        mock_setup_mantid,
        mock_setup_mantid_dev,
    ):
        """
        Verifies the setup method.
        """
        self.controller._mantid_equation = mantid_equation
        self.controller.setup()
        assert mock_setup_mantid.call_count == mock_setup_mantid_count
        assert mock_setup_mantid_dev.call_count == mock_setup_mantid_dev_count

    @parameterized.expand(
        [
            ("BFGS", "BFGS"),
            (
                "FABADA",
                (
                    "FABADA,Chain Length=100000,Steps between values=10,"
                    "Convergence Criteria=0.01,PDF=1,ConvergedChain=chain"
                ),
            ),
        ]
    )
    @patch("mantid.simpleapi.Fit")
    def test_fit(
        self,
        minimiizer,
        minimizer_arg,
        mock_fit,
    ):
        """
        Verifies the fit method.
        """
        self.controller._mantid_function = "mantid_function"
        self.controller._cost_function = "cost_function"
        self.controller.minimizer = minimiizer
        self.controller._mantid_data = "mantid_data"
        self.controller._added_args = {}

        mock_fit.return_value = MagicMock()

        self.controller.fit()
        call_args = mock_fit.call_args_list[0]
        assert call_args.kwargs["Function"] == "mantid_function"
        assert call_args.kwargs["CostFunction"] == "cost_function"
        assert call_args.kwargs["Minimizer"] == minimizer_arg
        assert call_args.kwargs["InputWorkspace"] == "mantid_data"
        assert call_args.kwargs["Output"] == "fit"
        if minimiizer == "FABADA":
            assert call_args.kwargs["MaxIterations"] == 2000000
