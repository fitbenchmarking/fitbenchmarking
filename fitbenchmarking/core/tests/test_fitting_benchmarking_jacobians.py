"""
Tests for fitbenchmarking.core.fitting_benchmarking.Fit.__loop_over_jacobians
"""
import inspect
import os
import unittest
from unittest.mock import patch

from fitbenchmarking import test_files
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.core.fitting_benchmarking import Fit
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import output_grabber
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.options import Options

# Due to construction of the controllers two folder functions
# pylint: disable=unnecessary-pass

# Defines the module which we mock out certain function calls for
FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking.Fit"


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
        self.hessian_enabled_solvers = []

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


def make_cost_function(file_name='cubic.dat', minimizers=None):
    """
    Helper function that returns a simple fitting problem
    """
    options = Options()
    if minimizers:
        options.minimizers = minimizers

    bench_prob_dir = os.path.dirname(inspect.getfile(test_files))
    fname = os.path.join(bench_prob_dir, file_name)

    fitting_problem = parse_problem_file(fname, options)
    fitting_problem.correct_data()
    cost_func = NLLSCostFunc(fitting_problem)
    return cost_func


class LoopOverJacobiansTests(unittest.TestCase):
    """
    loop_over_jacobians tests
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
        self.cp = Checkpoint(self.options)

    @staticmethod
    def mock_func_call(*args, **kwargs):
        """
        Mock function to be used instead of loop_over_hessians
        """
        return []

    @patch(f'{FITTING_DIR}._Fit__loop_over_hessians')
    def test_single_jacobian(self, loop_over_hessians):
        """
        Test to check that only one Jacobian option has been added
        """
        self.options.jac_method = ["scipy"]
        self.options.jac_num_method = {"scipy": ["3-point"]}
        self.controller.minimizer = "general"
        loop_over_hessians.side_effect = self.mock_func_call

        fit = Fit(options=self.options,
                  data_dir=FITTING_DIR,
                  checkpointer=self.cp)

        _ = fit._Fit__loop_over_jacobians(self.controller)
        loop_over_hessians.assert_called_once()

    @patch(f'{FITTING_DIR}._Fit__loop_over_hessians')
    def test_multiple_jacobian(self, loop_over_hessians):
        """
        Test to check multiple Jacobian options are set correctly
        """
        self.options.jac_method = ["scipy"]
        self.options.jac_num_method = {"scipy": ["3-point", "2-point"]}
        self.controller.minimizer = "general"
        loop_over_hessians.side_effect = self.mock_func_call

        fit = Fit(options=self.options,
                  data_dir=FITTING_DIR,
                  checkpointer=self.cp)

        _ = fit._Fit__loop_over_jacobians(self.controller)
        self.assertEqual(loop_over_hessians.call_count, 2)


if __name__ == "__main__":
    unittest.main()
