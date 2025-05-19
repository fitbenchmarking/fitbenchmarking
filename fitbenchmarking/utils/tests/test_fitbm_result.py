"""
Tests for FitBenchmarking object
"""

import inspect
import os
import textwrap
import unittest
from statistics import StatisticsError
from typing import TYPE_CHECKING
from unittest.mock import patch

import numpy as np
from parameterized import parameterized

from fitbenchmarking import test_files
from fitbenchmarking.controllers.scipy_controller import ScipyController
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.hessian.analytic_hessian import (
    Analytic as AnalyticHessian,
)
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.log import get_logger
from fitbenchmarking.utils.options import Options

if TYPE_CHECKING:
    from fitbenchmarking.parsing.fitting_problem import FittingProblem

LOGGER = get_logger()


class FitbmResultTests(unittest.TestCase):
    """
    Tests for FitBenchmarking results object
    """

    def setUp(self):
        """
        Setting up FitBenchmarking results object
        """
        self.options = Options()
        test_files_dir = os.path.dirname(inspect.getfile(test_files))
        problem_dir = os.path.join(test_files_dir, "cubic.dat")

        self.problem: FittingProblem = parse_problem_file(
            problem_dir, self.options
        )
        self.problem.correct_data()

        cost_func = NLLSCostFunc(self.problem)

        controller = ScipyController(cost_func=cost_func)
        controller.flag = 0
        controller.minimizer = "Newton-CG"
        controller.initial_params = np.array([0, 0, 0, 0])
        controller.final_params = np.array([1, 3, 4, 4])
        controller.parameter_set = 0

        jac = Scipy(problem=self.problem)
        jac.method = "2-point"
        cost_func.jacobian = jac

        hess = AnalyticHessian(self.problem, jac)
        cost_func.hessian = hess
        self.controller = controller

        self.accuracy = 10
        self.runtime = 0.01
        self.runtimes = [0.005, 0.015, 0.01]
        self.energy = 0.001
        self.result = FittingResult(
            controller=controller,
            accuracy=self.accuracy,
            runtimes=self.runtimes,
            energy=self.energy,
        )

        self.min_accuracy = 0.1
        self.result.min_accuracy = self.min_accuracy
        self.min_runtime = 1
        self.result.min_runtime = self.min_runtime

    def test_fitting_result_str(self):
        """
        Test that the fitting result can be printed as a readable string.
        """
        expected = textwrap.dedent("""\
            +=======================================+
            | FittingResult                         |
            +=======================================+
            | Cost Function  | NLLSCostFunc         |
            +---------------------------------------+
            | Problem        | cubic                |
            +---------------------------------------+
            | Software       | scipy                |
            +---------------------------------------+
            | Minimizer      | Newton-CG            |
            +---------------------------------------+
            | Jacobian       | scipy 2-point        |
            +---------------------------------------+
            | Hessian        | analytic             |
            +---------------------------------------+
            | Accuracy       | 10                   |
            +---------------------------------------+
            | Runtime        | 0.01                 |
            +---------------------------------------+
            | Runtime metric | mean                 |
            +---------------------------------------+
            | Runtimes       | [0.005, 0.015, 0.01] |
            +---------------------------------------+
            | Energy usage   | 0.001                |
            +---------------------------------------+""")

        for i, (r, e) in enumerate(
            zip(str(self.result).splitlines(), expected.splitlines())
        ):
            if r != e:
                print(f"Issue on line {i}:\n>{r}\n<{e}")
        self.assertEqual(str(self.result), expected)

    def test_init_with_dataset_id(self):
        """
        Tests to check that the multifit id is setup correctly
        """
        controller = self.controller
        problem = self.controller.problem

        chi_sq = [10, 5, 1]
        runtimes = [0.005, 0.015, 0.01]
        controller.final_params = [
            np.array([1, 3, 4, 4]),
            np.array([2, 3, 57, 8]),
            np.array([4, 2, 5, 1]),
        ]

        problem.data_x = [
            np.array([3, 2, 1, 4]),
            np.array([5, 1, 2, 3]),
            np.array([6, 7, 8, 1]),
        ]
        problem.data_y = [
            np.array([2, 1, 7, 40]),
            np.array([8, 9, 4, 2]),
            np.array([7, 4, 4, 2]),
        ]
        problem.data_e = [
            np.array([1, 1, 1, 1]),
            np.array([2, 2, 2, 1]),
            np.array([2, 3, 4, 4]),
        ]
        problem.sorted_index = [
            np.array([2, 1, 0, 3]),
            np.array([1, 2, 3, 0]),
            np.array([3, 0, 1, 2]),
        ]

        result = FittingResult(
            controller=controller,
            accuracy=chi_sq,
            runtimes=runtimes,
            dataset=1,
        )

        self.assertTrue(np.isclose(result.data_x, problem.data_x[1]).all())
        self.assertTrue(np.isclose(result.data_y, problem.data_y[1]).all())
        self.assertTrue(np.isclose(result.data_e, problem.data_e[1]).all())
        self.assertTrue(
            np.isclose(result.sorted_index, problem.sorted_index[1]).all()
        )

        self.assertTrue(
            np.isclose(controller.final_params[1], result.params).all()
        )
        self.assertEqual(chi_sq[1], result.accuracy)

    @parameterized.expand(
        [
            ("mean", [0.005, 0.015, 0.01], 0.01),
            ("mean", [1.00, 2.00, 3.00], 2.0),
            ("mean", [3.00], 3.0),
            ("mean", [np.inf, 2.00, 3.00], np.inf),
            ("mean", [np.inf, np.inf, np.inf], np.inf),
            ("minimum", [1.00, 2.00, 3.00, 4.00, 6.00], 1.00),
            ("minimum", [0, 2.00, 3.00, 4.00, 6.00], 0),
            ("maximum", [0, 2.00, 3.00, 4.00, 6.00], 6.00),
            ("maximum", [0], 0),
            ("first", [40, 100, 10], 40),
            ("median", [0, 3.00, 2.00, 4.00, 6.00], 3.0),
            ("median", [0, 2.00, 3.00, 4.00, 6.00, 10.0], 3.5),
            ("harmonic", [2.00, 5.00, 4.00, 6.00], 3.58209),
            ("harmonic", [2.00, 5.00, 4.00, 6.00, 10.0, 20.0], 4.73684),
            ("harmonic", [0, 5.00, 4.00, 6.00, 10.0, 20.0], 0),
            ("trim", [0, 5.00, 4.00, 6.00, 10.0, 20.0], 6.25),
            ("trim", [1.0, 4.00, 6.00, 10.0, 20.0, 40], 10),
        ]
    )
    def test_runtime_metrics(self, metric, runtimes, expected):
        """
        Tests the runtime metrics calculations within FittingResults
        """
        result = FittingResult(
            controller=self.controller,
            runtimes=runtimes,
            runtime_metric=metric,
        )
        self.assertAlmostEqual(expected, result.runtime, places=5)

    @patch(
        "fitbenchmarking.utils.fitbm_result.harmonic_mean",
        side_effect=StatisticsError,
    )
    def test_harmonic_runtime_is_inf_when_error(self, mock):
        """
        Tests the harmonic runtime is set to np.inf in case of invalid values.
        """
        result = FittingResult(
            controller=self.controller,
            runtimes=[0, -5, -10],
            runtime_metric="harmonic",
        )
        self.assertEqual(np.inf, result.runtime)

    @parameterized.expand(
        [
            (np.inf, np.inf, np.inf, False),
            (np.nan, np.nan, np.inf, False),
            (1, 0.01, 100, False),
            (1e-10, 0, 1, True),
            (2e-10, 0, 2, True),
            (1e-5, 0, 1e5, True),
        ]
    )
    def test_norm_acc(self, acc, min_acc, expected, warn):
        """
        Test norm_acc returns the expected results and raises the warning.
        """
        self.result.accuracy = acc
        self.result.min_accuracy = min_acc
        if warn:
            with self.assertLogs(LOGGER, level="WARNING") as log:
                self.assertEqual(self.result.norm_acc, expected)
                self.assertIn(
                    "The min accuracy of the dataset is 0. The "
                    "relative performance will be approximated "
                    "using a min of 1e-10.",
                    log.output[0],
                )
        else:
            self.assertEqual(self.result.norm_acc, expected)

    @parameterized.expand(
        [
            ("mean", [0.005, 0.015, 0.01], 0.001, 10),
            ("minimum", [1.00, 2.00, 3.00, 4.00, 6.00], 0.05, 20),
            ("maximum", [0, 2.00, 3.00, 4.00, 6.00], 3.00, 2),
            ("first", [40, 100, 10], 10, 4),
            ("median", [0, 2.00, 3.00, 4.00, 6.00, 10.0], 0.5, 7),
            ("harmonic", [2.00, 5.00, 4.00, 6.00, 10.0, 20.0], 4.73684, 1),
            ("trim", [0, 5.00, 4.00, 6.00, 10.0, 20.0], 0.25, 25),
        ]
    )
    def test_norm_runtime_finite_min(
        self, metric, runtimes, min_runtime, expected
    ):
        """
        Test that norm_runtime is correct when min_runtime is finite.
        """
        result = FittingResult(
            controller=self.controller,
            runtimes=runtimes,
            runtime_metric=metric,
        )
        setattr(result, "min_" + metric + "_runtime", min_runtime)
        self.assertAlmostEqual(expected, result.norm_runtime(metric), places=5)

    def test_norm_runtime_infinite_min(self):
        """
        Test that norm_runtime is correct when min_runtime is infinite.
        """
        self.result.runtime = np.inf
        self.result.min_runtime = np.inf
        self.assertEqual(self.result.norm_runtime(), np.inf)

    def test_sanitised_name(self):
        """
        Test that sanitised names are correct.
        """
        self.result.name = "test, name with commas"
        self.assertEqual(self.result.sanitised_name, "test_name_with_commas")

    def test_modified_minimizer_name_no_software(self):
        """
        Test modified minimizer name is correct when not including software.
        """
        self.result.software_tag = "s1"
        self.result.minimizer_tag = "m1"
        self.result.jacobian_tag = "j1"
        self.result.hessian_tag = "h1"
        self.assertEqual(
            self.result.modified_minimizer_name(False), "m1: j:j1 h:h1"
        )

    def test_modified_minimizer_name_with_software(self):
        """
        Test modified minimizer name is correct when including software.
        """
        self.result.software_tag = "s1"
        self.result.minimizer_tag = "m1"
        self.result.jacobian_tag = "j1"
        self.result.hessian_tag = "h1"
        self.assertEqual(
            self.result.modified_minimizer_name(True), "m1 [s1]: j:j1 h:h1"
        )

    def test_sanitised_min_name_no_software(self):
        """
        Test that sanitised minimizer names are correct without software.
        """
        self.result.software_tag = "s1"
        self.result.minimizer_tag = "m1"
        self.result.jacobian_tag = "j1"
        self.result.hessian_tag = "h1"
        self.assertEqual(self.result.sanitised_min_name(False), "m1_jj1_hh1")

    def test_sanitised_min_name_with_software(self):
        """
        Test that sanitised minimizer names are correct with software.
        """
        self.result.software_tag = "s1"
        self.result.minimizer_tag = "m1"
        self.result.jacobian_tag = "j1"
        self.result.hessian_tag = "h1"
        self.assertEqual(
            self.result.sanitised_min_name(True), "m1_[s1]_jj1_hh1"
        )

    def test_get_indexes_1d_cuts_spinw(self):
        """
        Test that get_indexes_1d_cuts_spinw returns expected output.
        """
        problem = self.controller.problem
        problem.additional_info["modQ_cens"] = np.array(
            [
                0.39491525,
                0.4440678,
                0.49322034,
                0.54237288,
                0.59152542,
                0.64067797,
                0.68983051,
                0.73898305,
                0.78813559,
                0.83728814,
                0.88644068,
                0.93559322,
                0.98474576,
                1.03389831,
                1.08305085,
                1.13220339,
                1.18135593,
                1.23050847,
                1.27966102,
                1.32881356,
                1.3779661,
                1.42711864,
                1.47627119,
                1.52542373,
                1.57457627,
                1.62372881,
                1.67288136,
                1.7220339,
                1.77118644,
                1.82033898,
            ]
        )

        problem.additional_info["q_cens"] = np.array(["0.8", "1.2"])
        problem.additional_info["dq"] = 0.05
        expected_ind = [
            (np.array([8, 9]),),
            (np.array([16, 17]),),
        ]
        obtained_ind = self.result.get_indexes_1d_cuts_spinw(problem)

        expected_ind_list = [tuple_i[0].tolist() for tuple_i in expected_ind]
        obtained_ind_list = [tuple_i[0].tolist() for tuple_i in obtained_ind]

        self.assertEqual(expected_ind_list, obtained_ind_list)

    def test_get_1d_cuts_spinw(self):
        """
        Test that get_1d_cuts_spinw returns expected output.
        """
        problem = self.controller.problem
        problem.additional_info["ebin_cens"] = np.array(
            [
                0.02531646,
                0.07594937,
                0.12658228,
                0.17721519,
            ]
        )
        array_to_cut = np.array(
            [
                0.02531646,
                0.07594937,
                0.12658228,
                0.17721519,
                0.2278481,
                0.27848101,
                0.32911392,
                0.37974684,
                0.43037975,
                0.48101266,
                0.53164557,
                0.58227848,
                0.63291139,
                0.6835443,
                0.73417722,
                0.78481013,
                0.83544304,
                0.88607595,
                0.93670886,
                0.98734177,
            ]
        )
        indexes = [(np.array([3, 4]),)]
        obtained = self.result.get_1d_cuts_spinw(
            problem, indexes, array_to_cut
        )
        expected = (
            [0.734177215, 0.7848101249999999, 0.8354430399999999, 0.88607595],
            np.array(
                [
                    [
                        0.02531646,
                        0.07594937,
                        0.12658228,
                        0.17721519,
                    ],
                    [
                        0.2278481,
                        0.27848101,
                        0.32911392,
                        0.37974684,
                    ],
                    [
                        0.43037975,
                        0.48101266,
                        0.53164557,
                        0.58227848,
                    ],
                    [
                        0.63291139,
                        0.6835443,
                        0.73417722,
                        0.78481013,
                    ],
                    [
                        0.83544304,
                        0.88607595,
                        0.93670886,
                        0.98734177,
                    ],
                ]
            ),
        )
        self.assertEqual(obtained[0], expected[0])
        self.assertTrue((obtained[1] == expected[1]).all())

    def test_get_1d_cuts_spinw_when_indexes_are_not_tuples(self):
        """
        Test that get_1d_cuts_spinw returns expected output.
        """
        problem = self.controller.problem
        problem.additional_info["ebin_cens"] = np.array(
            [
                0.02531646,
                0.07594937,
                0.12658228,
                0.17721519,
            ]
        )
        array_to_cut = np.array(
            [
                0.02531646,
                0.07594937,
                0.12658228,
                0.17721519,
                0.2278481,
                0.27848101,
                0.32911392,
                0.37974684,
                0.43037975,
                0.48101266,
                0.53164557,
                0.58227848,
                0.63291139,
                0.6835443,
                0.73417722,
                0.78481013,
                0.83544304,
                0.88607595,
                0.93670886,
                0.98734177,
            ]
        )
        indexes = [(np.array([3]),)]
        obtained = self.result.get_1d_cuts_spinw(
            problem, indexes, array_to_cut
        )
        expected = (
            [[0.63291139, 0.6835443, 0.73417722, 0.78481013]],
            np.array(
                [
                    [
                        0.02531646,
                        0.07594937,
                        0.12658228,
                        0.17721519,
                    ],
                    [
                        0.2278481,
                        0.27848101,
                        0.32911392,
                        0.37974684,
                    ],
                    [
                        0.43037975,
                        0.48101266,
                        0.53164557,
                        0.58227848,
                    ],
                    [
                        0.63291139,
                        0.6835443,
                        0.73417722,
                        0.78481013,
                    ],
                    [
                        0.83544304,
                        0.88607595,
                        0.93670886,
                        0.98734177,
                    ],
                ]
            ),
        )
        self.assertEqual(obtained[0], expected[0])
        self.assertTrue((obtained[1] == expected[1]).all())

    def test_data_x_when_plot_type_1d_cuts(self):
        """
        Test data_x is correct when plot_type is "1d_cuts".
        """
        problem = self.problem
        problem.additional_info["plot_type"] = "1d_cuts"
        problem.additional_info["n_plots"] = 2
        problem.additional_info["subplot_titles"] = []
        problem.additional_info["ax_titles"] = []
        problem.data_y = np.arange(10)
        problem.additional_info["ebin_cens"] = np.array(
            [0.02, 0.075, 0.126, 0.177, 0.22]
        )

        cost_func = NLLSCostFunc(problem)
        jac = Scipy(problem=problem)
        jac.method = "2-point"
        cost_func.jacobian = jac
        hess = AnalyticHessian(problem, jac)
        cost_func.hessian = hess

        controller = ScipyController(cost_func=cost_func)
        controller.minimizer = "Newton-CG"
        controller.parameter_set = 0

        result = FittingResult(
            controller=controller,
            accuracy=self.accuracy,
            runtimes=self.runtimes,
            energy=self.energy,
        )
        obtained = result.data_x
        expected = np.array(
            [0.02, 0.075, 0.126, 0.177, 0.22, 0.02, 0.075, 0.126, 0.177, 0.22]
        )
        self.assertTrue((obtained == expected).all())

    @patch(
        "fitbenchmarking.utils.fitbm_result.FittingResult.get_indexes_1d_cuts_spinw",
        return_value=[
            (np.array([8, 9]),),
        ],
    )
    @patch(
        "fitbenchmarking.utils.fitbm_result.FittingResult.get_1d_cuts_spinw",
        return_value=(None, None),
    )
    def test_data_x_cuts_when_plot_type_2d(
        self, mock_get_cuts, mock_get_indexes
    ):
        """
        Test data_x_cuts is correct when plot_type is "2d".
        Also test that get_indexes_1d_cuts_spinw and get_1d_cuts_spinw
        get called.
        """
        problem = self.problem
        problem.additional_info["plot_type"] = "2d"
        problem.additional_info["n_plots"] = 2
        problem.additional_info["subplot_titles"] = []
        problem.additional_info["ax_titles"] = []
        problem.additional_info["q_cens"] = np.array(["0.8", "1.2"])
        problem.additional_info["dq"] = 0.05
        problem.additional_info["ebin_cens"] = np.array([0.075, 0.126, 0.177])
        problem.additional_info["modQ_cens"] = np.array(
            [0.837, 0.886, 0.935, 0.984]
        )

        cost_func = NLLSCostFunc(problem)
        jac = Scipy(problem=problem)
        jac.method = "2-point"
        cost_func.jacobian = jac
        hess = AnalyticHessian(problem, jac)
        cost_func.hessian = hess

        controller = ScipyController(cost_func=cost_func)
        controller.minimizer = "Newton-CG"
        controller.parameter_set = 0

        result = FittingResult(
            controller=controller,
            accuracy=self.accuracy,
            runtimes=self.runtimes,
            energy=self.energy,
        )
        obtained = result.data_x_cuts
        expected = np.array([0.075, 0.126, 0.177, 0.075, 0.126, 0.177])

        self.assertTrue((obtained == expected).all())
        mock_get_indexes.assert_called()
        mock_get_cuts.assert_called()


if __name__ == "__main__":
    unittest.main()
