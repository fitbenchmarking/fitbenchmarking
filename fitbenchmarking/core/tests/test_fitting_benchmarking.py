from __future__ import (absolute_import, division, print_function)
import inspect
import os
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.utils import fitbm_result, output_grabber
import fitbenchmarking.core.fitting_benchmarking as fitting_benchmarking
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.options import Options
from fitbenchmarking.jacobian.SciPyFD_2point_jacobian import ScipyTwoPoint

fitting_benchmarking_dir = "fitbenchmarking.core.fitting_benchmarking"


class DummyController(Controller):
    """
    Minimal instantiatable subclass of Controller class for testing
    """

    def __init__(self, problem):
        super(DummyController, self).__init__(problem)
        self.algorithm_check = {'all': ['deriv_free_algorithm', 'general'],
                                'ls': [None],
                                'deriv_free': ['deriv_free_algorithm'],
                                'general': ['general']}
        self.final_params_expected = [[1, 2, 3, 4], [4, 3, 2, 1]]
        self.flag_expected = [0, 1]
        self.count = 0

    def setup(self):
        pass

    def fit(self):
        pass

    def cleanup(self):
        self.final_params = self.final_params_expected[self.count]
        self.flag = self.flag_expected[self.count]
        self.count += 1

    def error_flags(self):
        pass


def make_fitting_problem(file_name='cubic.dat'):
    """
    Helper function that returns a simple fitting problem
    """
    options = Options()
    options.minimizers = ["deriv_free_algorithm", "general"]

    bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
    fname = os.path.join(bench_prob_dir, file_name)

    fitting_problem = parse_problem_file(fname, options)
    fitting_problem.correct_data()
    jac = ScipyTwoPoint(fitting_problem)
    fitting_problem.jac = jac
    return fitting_problem


class LoopOverMinimizersTests(unittest.TestCase):

    def setUp(self):
        self.problem = make_fitting_problem()
        self.controller = DummyController(problem=self.problem)
        self.options = self.problem.options
        self.minimizers = self.options.minimizers
        self.grabbed_output = output_grabber.OutputGrabber(self.options)
        self.controller.parameter_set = 0

    def shared_tests(self, results_problem, minimizer_failed):
        """
        Shared tests for the `loop_over_minimizer` function

        :param results_problem: list of all results
        :type results_problem: list
        :param minimizer_failed: list of failed minimizers
        :type minimizer_failed: list
        """

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
        results_problem, minimizer_failed = \
            fitting_benchmarking.loop_over_minimizers(self.controller,
                                                      self.minimizers,
                                                      self.options,
                                                      self.grabbed_output)
        self.shared_tests(results_problem, minimizer_failed)

    def test_run_minimzers_deriv_free(self):
        """
        Tests that ``algorithm_type = deriv_free`` minimizers run
        """
        self.options.algorithm_type = "deriv_free"
        results_problem, minimizer_failed = \
            fitting_benchmarking.loop_over_minimizers(self.controller,
                                                      self.minimizers,
                                                      self.options,
                                                      self.grabbed_output)
        self.shared_tests(results_problem, minimizer_failed)


if __name__ == "__main__":
    unittest.main()
