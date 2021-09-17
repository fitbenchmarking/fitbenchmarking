"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_hessians
"""
import inspect
import os
import unittest
from unittest.mock import patch

from fitbenchmarking import mock_problems
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.core.fitting_benchmarking import loop_over_hessians
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import output_grabber
from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.timer import TimerWithMaxTime

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

    def setup(self):
        """
        Mock controller setup function
        """
        pass

    def fit(self):
        """
        Mock controller fit function
        """
        pass

    def cleanup(self):
        """
        Mock controller cleanup function
        """
        self.final_params = self.final_params_expected[self.count]
        self.flag = self.flag_expected[self.count]
        self.count += 1
        self.count = self.count % len(self.flag_expected)


def make_cost_function(file_name='cubic.dat', minimizers=None, max_runtime=None):
    """
    Helper function that returns a simple fitting problem
    """
    options = Options()
    if minimizers:
        options.minimizers = minimizers
    if max_runtime:
        options.max_runtime = max_runtime

    bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
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
        self.controller = DummyController(cost_func=self.cost_func)
        self.options = self.problem.options
        self.grabbed_output = output_grabber.OutputGrabber(self.options)
        self.controller.parameter_set = 0

    def test_single_hessian(self):
        """
        Test to check that only one Hessian option has been added
        """
        self.options.hes_method = ["analytic"]
        self.controller.minimizer = "general"
        new_name = ['general, analytic hessian']
        jacobian = False
        minimizer_name = "general"
        _, _, new_minimizer_list = \
            loop_over_hessians(self.controller,
                               self.options,
                               minimizer_name,
                               jacobian,
                               self.grabbed_output)
        assert new_minimizer_list == new_name

    def test_single_no_hessian(self):
        """
        Test that checks that the minimizer doesn't need Hessian information
        and the name does not have Hessian information in it
        """
        self.options.hes_method = ["analytic"]
        self.controller.minimizer = "deriv_free_algorithm"
        new_name = ['deriv_free_algorithm']
        jacobian = False
        minimizer_name = "deriv_free_algorithm"
        _, _, new_minimizer_list = \
            loop_over_hessians(self.controller,
                               self.options,
                               minimizer_name,
                               jacobian,
                               self.grabbed_output)
        assert new_minimizer_list == new_name

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
        jacobian = False
        minimizer_name = "deriv_free_algorithm"

        _ = loop_over_hessians(self.controller,
                               self.options,
                               minimizer_name,
                               jacobian,
                               self.grabbed_output)
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
        jacobian = False
        minimizer_name = "deriv_free_algorithm"

        _ = loop_over_hessians(self.controller,
                               self.options,
                               minimizer_name,
                               jacobian,
                               self.grabbed_output)
        check_bounds_respected.assert_not_called()

    @patch.object(TimerWithMaxTime, 'reset', lambda *args: None)
    def test_max_runtime_exceeded(self):
        """
        Test that the correct flag is set when the max_runtime is exceeded.
        """
        self.cost_func = make_cost_function(minimizers=self.minimizers, max_runtime=0.1)
        self.cost_func.problem.timer._total_elapsed_time = 5
        self.controller = DummyController(cost_func=self.cost_func)
        self.options = self.cost_func.problem.options
        self.grabbed_output = output_grabber.OutputGrabber(self.options)
        self.controller.parameter_set = 0

        jacobian = False
        self.controller.minimizer = "deriv_free_algorithm"
        results, _, _ = loop_over_hessians(self.controller, self.options,
                                           self.controller.minimizer,
                                           jacobian, self.grabbed_output)
        assert results[0]["error_flag"] == 6


if __name__ == "__main__":
    unittest.main()
