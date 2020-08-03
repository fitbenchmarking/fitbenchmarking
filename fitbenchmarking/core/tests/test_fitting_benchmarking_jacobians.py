"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_jacobians
"""
from __future__ import (absolute_import, division, print_function)
import inspect
import os
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.utils import fitbm_result, output_grabber
from fitbenchmarking.core.fitting_benchmarking import loop_over_jacobians
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.options import Options
from fitbenchmarking.jacobian.scipy_jacobian import Scipy


# Due to construction of the controllers two folder functions
# pylint: disable=unnecessary-pass
class DummyController(Controller):
    """
    Minimal instantiatable subclass of Controller class for testing
    """

    def __init__(self, problem):
        """
        Initialize dummy controller

        :param problem: Problem to fit
        :type problem: FittingProblem
        """
        super(DummyController, self).__init__(problem)
        self.algorithm_check = {'all': ['deriv_free_algorithm', 'general'],
                                'ls': [None],
                                'deriv_free': ['deriv_free_algorithm'],
                                'general': ['general']}
        self.count = 0
        self.has_jacobian = []
        self.invalid_jacobians = []

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

    def cleanup(self):
        """
        Mock controller cleanup function
        """
        self.final_params = self.final_params_expected[self.count]
        self.flag = self.flag_expected[self.count]
        self.count += 1


def make_fitting_problem(file_name='cubic.dat', minimizers=None):
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
    return fitting_problem


class LoopOverJacobiansTests(unittest.TestCase):
    """
    loop_over_jacobians tests
    """

    def setUp(self):
        """
        Setting up problem for tests
        """
        self.minimizers = ["deriv_free_algorithm", "general"]
        self.problem = make_fitting_problem(minimizers=self.minimizers)
        self.controller = DummyController(problem=self.problem)
        self.options = self.problem.options
        self.grabbed_output = output_grabber.OutputGrabber(self.options)
        self.controller.parameter_set = 0

    def test_single_jacobian(self):
        """
        Test to check that only on Jacobian option has been added
        """
        self.options.jac_method = ["scipy"]
        self.options.num_method = {"scipy": ["3-point"]}
        self.controller.has_jacobian = [True]
        self.controller.invalid_jacobians = ["deriv_free_algorithm"]
        self.controller.minimizer = "general"
        new_name = ['general: scipy 3-point']
        results, chi_sq, new_minimizer_list = \
            loop_over_jacobians(self.controller,
                                self.options,
                                self.grabbed_output)
        assert all(isinstance(x, dict) for x in results)
        assert all(x["minimizer"] == name for x, name in zip(results, new_name))
        assert new_minimizer_list == new_name

    def test_multiple_jacobian(self):
        """
        Test to check multiple Jacobian options are set correctly
        """
        self.options.jac_method = ["scipy"]
        self.options.num_method = {"scipy": ["3-point", "2-point"]}
        self.controller.has_jacobian = [True]
        self.controller.invalid_jacobians = ["deriv_free_algorithm"]
        self.controller.minimizer = "general"
        new_name = ['general: scipy 3-point', 'general: scipy 2-point']
        results, chi_sq, new_minimizer_list = \
            loop_over_jacobians(self.controller,
                                self.options,
                                self.grabbed_output)
        assert all(isinstance(x, dict) for x in results)
        assert all(x["minimizer"] == name for x, name in zip(results, new_name))
        assert new_minimizer_list == new_name

    def test_single_no_jacobian(self):
        """
        Test that checks that the minimizer doesn't need Jacobian information
        and the name does not have Jacobian information in it
        """
        self.options.jac_method = ["scipy"]
        self.options.num_method = {"scipy": ["3-point", "2-point"]}
        self.controller.has_jacobian = [True]
        self.controller.invalid_jacobians = ["deriv_free_algorithm"]
        self.controller.minimizer = "deriv_free_algorithm"
        new_name = ['deriv_free_algorithm']
        results, chi_sq, new_minimizer_list = \
            loop_over_jacobians(self.controller,
                                self.options,
                                self.grabbed_output)
        assert all(isinstance(x, dict) for x in results)
        assert all(x["minimizer"] == name for x, name in zip(results, new_name))
        assert new_minimizer_list == new_name


if __name__ == "__main__":
    unittest.main()
