"""
Tests for FitBenchmarking object
"""

import inspect
import os
import textwrap
import unittest
from typing import TYPE_CHECKING

import numpy as np

from fitbenchmarking import test_files
from fitbenchmarking.controllers.scipy_controller import ScipyController
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.hessian.analytic_hessian import \
    Analytic as AnalyticHessian
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options

if TYPE_CHECKING:
    from fitbenchmarking.parsing.fitting_problem import FittingProblem


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

        problem: 'FittingProblem' = parse_problem_file(
            problem_dir, self.options)
        problem.correct_data()

        cost_func = NLLSCostFunc(problem)

        controller = ScipyController(cost_func=cost_func)
        controller.flag = 0
        controller.minimizer = "Newton-CG"
        controller.initial_params = np.array([0, 0, 0, 0])
        controller.final_params = np.array([1, 3, 4, 4])
        controller.parameter_set = 0

        jac = Scipy(problem=problem)
        jac.method = "2-point"
        cost_func.jacobian = jac

        hess = AnalyticHessian(problem, jac)
        cost_func.hessian = hess
        self.controller = controller

        self.accuracy = 10
        self.runtime = 0.01
        self.runtimes = [0.005, 0.015, 0.01]
        self.emissions = 0.001
        self.result = FittingResult(
            controller=controller,
            accuracy=self.accuracy,
            runtimes=self.runtimes,
            emissions=self.emissions)

        self.min_accuracy = 0.1
        self.result.min_accuracy = self.min_accuracy
        self.min_runtime = 1
        self.result.min_runtime = self.min_runtime

    def test_fitting_result_str(self):
        """
        Test that the fitting result can be printed as a readable string.
        """
        expected = textwrap.dedent('''\
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
            | Emissions      | 0.001                |
            +---------------------------------------+''')

        for i, (r, e) in enumerate(zip(str(self.result).splitlines(),
                                       expected.splitlines())):
            if r != e:
                print(f'Issue on line {i}:\n>{r}\n<{e}')
        self.assertEqual(str(self.result), expected)

    def test_init_with_dataset_id(self):
        """
        Tests to check that the multifit id is setup correctly
        """
        controller = self.controller
        problem = self.controller.problem

        chi_sq = [10, 5, 1]
        runtimes = [0.005, 0.015, 0.01]
        controller.final_params = [np.array([1, 3, 4, 4]),
                                   np.array([2, 3, 57, 8]),
                                   np.array([4, 2, 5, 1])]

        problem.data_x = [np.array([3, 2, 1, 4]),
                          np.array([5, 1, 2, 3]),
                          np.array([6, 7, 8, 1])]
        problem.data_y = [np.array([2, 1, 7, 40]),
                          np.array([8, 9, 4, 2]),
                          np.array([7, 4, 4, 2])]
        problem.data_e = [np.array([1, 1, 1, 1]),
                          np.array([2, 2, 2, 1]),
                          np.array([2, 3, 4, 4])]
        problem.sorted_index = [np.array([2, 1, 0, 3]),
                                np.array([1, 2, 3, 0]),
                                np.array([3, 0, 1, 2])]

        result = FittingResult(
            controller=controller,
            accuracy=chi_sq,
            runtimes=runtimes,
            dataset=1)

        self.assertTrue(
            np.isclose(result.data_x, problem.data_x[1]).all())
        self.assertTrue(
            np.isclose(result.data_y, problem.data_y[1]).all())
        self.assertTrue(
            np.isclose(result.data_e, problem.data_e[1]).all())
        self.assertTrue(
            np.isclose(result.sorted_index,
                       problem.sorted_index[1]).all())

        self.assertTrue(
            np.isclose(controller.final_params[1], result.params).all())
        self.assertEqual(chi_sq[1], result.accuracy)

    def test_runtime_metrics(self):
        """
        Tests the mean metric with in FittingResults
        """
        testcases = [{
                        'metric': 'mean',
                        'runtimes':  [0.005, 0.015, 0.01],
                        'expected':  0.01,
                     },
                     {
                        'metric': 'mean',
                        'runtimes':  [1.00, 2.00, 3.00],
                        'expected':  2.0,
                     },
                     {
                        'metric': 'mean',
                        'runtimes':  [3.00],
                        'expected':  3.0,
                     },
                     {
                        'metric': 'mean',
                        'runtimes':  [np.inf, 2.00, 3.00],
                        'expected':  np.inf,
                     },
                     {
                        'metric': 'mean',
                        'runtimes':  [np.inf, np.inf, np.inf],
                        'expected':  np.inf,
                     },
                     {
                        'metric': 'minimum',
                        'runtimes':  [1.00, 2.00, 3.00, 4.00, 6.00],
                        'expected':  1.00,
                     },
                     {
                        'metric': 'minimum',
                        'runtimes':  [0, 2.00, 3.00, 4.00, 6.00],
                        'expected':  0,
                     },
                     {
                        'metric': 'maximum',
                        'runtimes':  [0, 2.00, 3.00, 4.00, 6.00],
                        'expected':  6.00,
                     },
                     {
                        'metric': 'maximum',
                        'runtimes':  [0],
                        'expected':  0,
                     },
                     {
                        'metric': 'first',
                        'runtimes':  [0],
                        'expected':  0,
                     },
                     {
                        'metric': 'first',
                        'runtimes':  [40, 100, 10],
                        'expected':  40,
                     },
                     {
                        'metric': 'median',
                        'runtimes':  [0, 3.00, 2.00, 4.00, 6.00],
                        'expected':  3.0,
                     },
                     {
                        'metric': 'median',
                        'runtimes':  [0, 2.00, 3.00, 4.00, 6.00, 10.0],
                        'expected':  3.5,
                     },
                     {
                        'metric': 'harmonic',
                        'runtimes':  [2.00, 5.00, 4.00, 6.00],
                        'expected':  3.58209,
                     },
                     {
                        'metric': 'harmonic',
                        'runtimes':  [2.00, 5.00, 4.00, 6.00, 10.0, 20.0],
                        'expected':  4.73684,
                     },
                     {
                        'metric': 'harmonic',
                        'runtimes':  [0, 5.00, 4.00, 6.00, 10.0, 20.0],
                        'expected':  0,
                     },
                     {
                        'metric': 'trim',
                        'runtimes':  [0, 5.00, 4.00, 6.00, 10.0, 20.0],
                        'expected':  6.25,
                     },
                     {
                        'metric': 'trim',
                        'runtimes':  [1.0, 4.00, 6.00, 10.0, 20.0, 40],
                        'expected':  10,
                     }]

        for case in testcases:
            with self.subTest(case['runtimes']):
                controller = self.controller
                result = FittingResult(
                    controller=controller,
                    runtimes=case['runtimes'],
                    runtime_metric=case['metric'])
                self.assertAlmostEqual(case['expected'],
                                       result.runtime,
                                       places=5)

    def test_norm_acc_finite_min(self):
        """
        Test that sanitised names are correct when min_chi_sq is finite.
        """
        expected = self.accuracy / self.min_accuracy
        self.assertEqual(self.result.norm_acc, expected)

    def test_norm_acc_infinite_min(self):
        """
        Test that sanitised names are correct when min_chi_sq is infinite.
        """
        expected = np.inf
        self.result.accuracy = np.inf
        self.result.min_accuracy = np.inf
        self.assertEqual(self.result.norm_acc, expected)

    def test_norm_runtime_finite_min(self):
        """
        Test that sanitised names are correct when min_runtime is finite.
        """
        expected = self.runtime / self.min_runtime
        self.assertEqual(self.result.norm_runtime, expected)

    def test_norm_runtime_infinite_min(self):
        """
        Test that sanitised names are correct when min_runtime is infinite.
        """
        expected = np.inf
        self.result.runtime = np.inf
        self.result.min_runtime = np.inf
        self.assertEqual(self.result.norm_runtime, expected)

    def test_sanitised_name(self):
        """
        Test that sanitised names are correct.
        """
        self.result.name = 'test, name with commas'
        self.assertEqual(self.result.sanitised_name, 'test_name_with_commas')

    def test_modified_minimizer_name_no_software(self):
        """
        Test modified minimizer name is correct when not including software.
        """
        self.result.software_tag = 's1'
        self.result.minimizer_tag = 'm1'
        self.result.jacobian_tag = 'j1'
        self.result.hessian_tag = 'h1'
        self.assertEqual(self.result.modified_minimizer_name(False),
                         'm1: j:j1 h:h1')

    def test_modified_minimizer_name_with_software(self):
        """
        Test modified minimizer name is correct when including software.
        """
        self.result.software_tag = 's1'
        self.result.minimizer_tag = 'm1'
        self.result.jacobian_tag = 'j1'
        self.result.hessian_tag = 'h1'
        self.assertEqual(self.result.modified_minimizer_name(True),
                         'm1 [s1]: j:j1 h:h1')

    def test_sanitised_min_name_no_software(self):
        """
        Test that sanitised minimizer names are correct without software.
        """
        self.result.software_tag = 's1'
        self.result.minimizer_tag = 'm1'
        self.result.jacobian_tag = 'j1'
        self.result.hessian_tag = 'h1'
        self.assertEqual(self.result.sanitised_min_name(False),
                         'm1_jj1_hh1')

    def test_sanitised_min_name_with_software(self):
        """
        Test that sanitised minimizer names are correct with software.
        """
        self.result.software_tag = 's1'
        self.result.minimizer_tag = 'm1'
        self.result.jacobian_tag = 'j1'
        self.result.hessian_tag = 'h1'
        self.assertEqual(self.result.sanitised_min_name(True),
                         'm1_[s1]_jj1_hh1')


if __name__ == "__main__":
    unittest.main()
