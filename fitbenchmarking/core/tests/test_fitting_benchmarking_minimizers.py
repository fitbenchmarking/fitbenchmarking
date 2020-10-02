"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_minimizers
"""
from __future__ import (absolute_import, division, print_function)
import inspect
import os
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.utils import fitbm_result, output_grabber
from fitbenchmarking.core.fitting_benchmarking import loop_over_minimizers
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.options import Options
from fitbenchmarking.jacobian.SciPyFD_2point_jacobian import ScipyTwoPoint


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
        self.final_params_expected = [[1, 2, 3, 4], [4, 3, 2, 1]]
        self.flag_expected = [0, 1]
        self.count = 0

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
    jac = ScipyTwoPoint(fitting_problem)
    fitting_problem.jac = jac
    return fitting_problem


class LoopOverMinimizersTests(unittest.TestCase):
    """
    loop_over_minimizers tests
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

    def shared_tests(self):

        """
        Shared tests for the `loop_over_minimizer` function
        """

        results_problem, minimizer_failed = loop_over_minimizers(
            self.controller, self.minimizers, self.options,
            self.grabbed_output)
        algorithms = \
            self.controller.algorithm_check[self.options.algorithm_type]
        unselected_algorithms = [x for x in self.minimizers
                                 if x not in algorithms]
        assert len(results_problem) == len(algorithms)
        assert all(isinstance(x, fitbm_result.FittingResult)
                   for x in results_problem)
        for i, result in enumerate(results_problem):
            assert result.params == self.controller.final_params_expected[i]
            assert result.error_flag == self.controller.flag_expected[i]
        assert minimizer_failed == unselected_algorithms

    def test_run_all_minimzers(self):
        """
        Tests that all minimizers run
        """
        self.shared_tests()

    def test_run_minimzers_deriv_free(self):
        """
        Tests that ``algorithm_type = deriv_free`` minimizers run
        """
        self.options.algorithm_type = "deriv_free"
        self.shared_tests()


if __name__ == "__main__":
    unittest.main()
