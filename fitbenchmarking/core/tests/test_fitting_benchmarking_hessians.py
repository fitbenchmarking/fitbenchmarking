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

# Due to construction of the controllers two folder functions
# pylint: disable=unnecessary-pass

# Defines the module which we mock out certain function calls for
FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"


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
        self.has_jacobian = []
        self.invalid_jacobians = []
        self.has_hessian = []
        self.valid_hessians = []

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

    def jacobian_information(self):
        """
        Mock controller jacobian_information function
        """
        has_jacobian = self.has_jacobian[self.count]
        invalid_jacobians = self.invalid_jacobians[self.count]
        return has_jacobian, invalid_jacobians

    def hessian_information(self):
        """
        Mock controller jacobian_information function
        """
        has_hessian = self.has_hessian[self.count]
        valid_hessians = self.valid_hessians[self.count]
        return has_hessian, valid_hessians

    def cleanup(self):
        """
        Mock controller cleanup function
        """
        self.final_params = self.final_params_expected[self.count]
        self.flag = self.flag_expected[self.count]
        self.count += 1
        self.count = self.count % len(self.flag_expected)


def make_cost_function(file_name='cubic.dat', minimizers=None):
    """
    Helper function that returns a simple fitting problem
    """
    options = Options()
    if minimizers:
        options.minimizers = minimizers

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

    def mock_func_call(self, *args, **kwargs):
        """
        Mock function to be used instead of loop_over_jacobians
        """
        return [], [], []

    @patch('{}.loop_over_jacobians'.format(FITTING_DIR))
    def test_no_hessian(self, loop_over_jacobians):
        """
        Test that loop_over_jacobians is called when no hessian
        option is selected.
        """

        self.controller.minimizer = "general"
        self.controller.has_hessian = [True]
        self.controller.valid_hessians = ["general"]
        loop_over_jacobians.side_effect = self.mock_func_call

        loop_over_hessians(self.controller,
                           self.options,
                           self.grabbed_output)
        loop_over_jacobians.assert_called()

    @patch('{}.loop_over_jacobians'.format(FITTING_DIR))
    def test_hessian_minimizer_ok(self, loop_over_jacobians):
        """
        Test that loop_over_jacobians is called when use
        hessians is set to true and the minimizer selected
        can use hessian information
        """
        self.options.hes_method = ["analytic"]
        self.controller.minimizer = "general"
        self.controller.has_hessian = [True]
        self.controller.valid_hessians = ["general"]
        loop_over_jacobians.side_effect = self.mock_func_call

        loop_over_hessians(self.controller,
                           self.options,
                           self.grabbed_output)
        loop_over_jacobians.assert_called()


if __name__ == "__main__":
    unittest.main()
