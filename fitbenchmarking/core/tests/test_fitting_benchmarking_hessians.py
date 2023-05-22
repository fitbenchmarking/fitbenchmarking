"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_hessians
"""
import inspect
import os
import unittest
from unittest.mock import patch
from shutil import rmtree
from pytest import test_type as TEST_TYPE  # pylint: disable=no-name-in-module

from conftest import run_for_test_types
from fitbenchmarking import test_files
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.core.fitting_benchmarking import loop_over_hessians
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import output_grabber
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.options import Options

# Due to construction of the controllers two folder functions
# pylint: disable=unnecessary-pass


class DummyController(Controller):
    """
    Minimal instantiatable subclass of Controller class for testing
    """

    def __init__(self, cost_func):
        """
        Initialize dummy controller

        :param cost_func: cost function class
        :type cost_func: CostFunc class
        """
        super().__init__(cost_func)
        self.algorithm_check = {'all': ['deriv_free_algorithm', 'general'],
                                'ls': [None],
                                'deriv_free': ['deriv_free_algorithm'],
                                'general': ['general']}
        self.final_params_expected = [[1, 2, 3, 4], [4, 3, 2, 1]]
        self.flag_expected = [0, 1]
        self.count = 0
        self.jacobian_enabled_solvers = ["general"]
        self.hessian_enabled_solvers = ["general"]

    def validate(self):
        """
        Mock controller validate function.
        """
        pass

    def setup(self):
        """
        Mock controller setup function
        """
        pass

    def fit(self):
        """
        Mock controller fit function
        """
        self.eval_chisq([1, 1, 1, 1])

    def cleanup(self):
        """
        Mock controller cleanup function
        """
        self.final_params = self.final_params_expected[self.count]
        self.flag = self.flag_expected[self.count]
        self.count += 1
        self.count = self.count % len(self.flag_expected)


def make_cost_function(file_name='cubic.dat', minimizers=None,
                       max_runtime=None):
    """
    Helper function that returns a simple fitting problem
    """
    results_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'fitbenchmarking_results')
    options = Options(additional_options={'external_output': 'debug',
                                          'results_dir': results_dir})
    if minimizers:
        options.minimizers = minimizers
    if max_runtime:
        options.max_runtime = max_runtime

    bench_prob_dir = os.path.dirname(inspect.getfile(test_files))
    fname = os.path.join(bench_prob_dir, file_name)

    fitting_problem = parse_problem_file(fname, options)
    fitting_problem.correct_data()
    cost_func = NLLSCostFunc(fitting_problem)
    return cost_func


class LoopOverHessiansTests(unittest.TestCase):
    """
    loop_over_hessians tests
    """

    def setUp(self):
        """
        Setting up problem for tests
        """
        self.minimizers = ["deriv_free_algorithm", "general"]
        self.cost_func = make_cost_function(minimizers=self.minimizers)
        self.problem = self.cost_func.problem
        self.cost_func.jacobian = Scipy(self.problem)
        self.cost_func.jacobian.method = '2-point'
        self.controller = DummyController(cost_func=self.cost_func)
        self.options: Options = self.problem.options
        self.grabbed_output = output_grabber.OutputGrabber(self.options)
        self.controller.parameter_set = 0
        self.cp = Checkpoint(self.options)

    def tearDown(self) -> None:
        """
        Clean up after the test
        """
        rmtree(self.options.results_dir)

    def test_single_hessian(self):
        """
        Test to check that only one Hessian option has been added
        """
        self.options.hes_method = ["analytic"]
        self.controller.minimizer = "general"
        _ = loop_over_hessians(self.controller,
                               options=self.options,
                               grabbed_output=self.grabbed_output,
                               checkpointer=self.cp)
        self.assertEqual(self.controller.count, 1)

    @patch.object(DummyController, "check_bounds_respected")
    def test_bounds_respected_func_called(
            self, check_bounds_respected):
        """
        Test that the check to verify that check_bounds_respected is called
        when the controller runs succesfully and parameter bounds
        have been set.
        """
        self.controller.problem.value_ranges = {'test': (0, 1)}
        self.controller.minimizer = "deriv_free_algorithm"

        _ = loop_over_hessians(self.controller,
                               options=self.options,
                               grabbed_output=self.grabbed_output,
                               checkpointer=self.cp)
        check_bounds_respected.assert_called()

    @patch.object(DummyController, "check_bounds_respected")
    def test_bounds_respected_func_not_called(
            self, check_bounds_respected):
        """
        Test that the check to verify that check_bounds_respected is not called
        when bounds have been set but the controller fails.
        """
        self.controller.problem.value_ranges = {'test': (0, 1)}
        self.controller.minimizer = "deriv_free_algorithm"
        self.controller.flag_expected = [3]

        _ = loop_over_hessians(self.controller,
                               options=self.options,
                               grabbed_output=self.grabbed_output,
                               checkpointer=self.cp)
        check_bounds_respected.assert_not_called()

    def test_max_runtime_exceeded(self):
        """
        Test that the correct flag is set when the max_runtime is exceeded.
        """
        cost_func = make_cost_function(minimizers=self.minimizers,
                                       max_runtime=0.1)
        cost_func.jacobian = Scipy(cost_func.problem)
        cost_func.jacobian.method = '2-point'
        cost_func.problem.timer.total_elapsed_time = 5
        controller = DummyController(cost_func=cost_func)
        options = cost_func.problem.options
        grabbed_output = output_grabber.OutputGrabber(options)
        controller.parameter_set = 0

        controller.minimizer = "deriv_free_algorithm"
        results = loop_over_hessians(controller,
                                     options=options,
                                     grabbed_output=grabbed_output,
                                     checkpointer=self.cp)
        self.assertEqual(results[0].error_flag, 6)

    @run_for_test_types(TEST_TYPE, 'all')
    @patch('fitbenchmarking.core.fitting_benchmarking.perform_fit')
    def test_multifit_num_results(self, perform_fit):
        """
        Test that a multifit problem produces the correct number of results.
        """
        cost_func = make_cost_function('multifit_set/multifit.txt')
        problem = cost_func.problem
        cost_func.jacobian = Scipy(problem)
        cost_func.jacobian.method = '2-point'
        controller = DummyController(cost_func=cost_func)
        options = problem.options
        grabbed_output = output_grabber.OutputGrabber(options)
        controller.final_params = [[0.1, 0.1], [0.1, 0.1]]
        controller.parameter_set = 0
        perform_fit.return_value = ([0.1, 0.2], [0.1, 0.01], [10e-3, 10e-4])
        results = loop_over_hessians(controller=controller,
                                     options=options,
                                     grabbed_output=grabbed_output,
                                     checkpointer=self.cp)
        self.assertTrue(len(results) == 2)


if __name__ == "__main__":
    unittest.main()
