"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_minimizers
"""
import inspect
import os
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.core.fitting_benchmarking import loop_over_minimizers
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import fitbm_result, output_grabber
from fitbenchmarking.utils.options import Options

# Defines the module which we mock out certain function calls for
FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"


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
        super(DummyController, self).__init__(cost_func)
        self.algorithm_check = {'all': ['deriv_free_algorithm', 'general'],
                                'ls': [None],
                                'deriv_free': ['deriv_free_algorithm'],
                                'general': ['general']}
        self.no_bounds_minimizers = ['general']
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

    def jacobian_information(self):
        """
        Mock controller jacobian_information function
        """
        pass

    def cleanup(self):
        """
        Mock controller cleanup function
        """
        self.final_params = self.final_params_expected[self.count]
        self.flag = self.flag_expected[self.count]
        self.count += 1


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


# pylint: disable=attribute-defined-outside-init
class LoopOverMinimizersTests(unittest.TestCase):
    """
    loop_over_minimizers tests
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
        self.count = 0
        self.result_args = {'options': self.options,
                            'cost_func': self.cost_func,
                            'jac': "jac",
                            'initial_params': self.problem.starting_values[0],
                            'params': [],
                            'chi_sq': 1}

    def mock_func_call(self, *args, **kwargs):
        """
        Mock function to be used instead of loop_over_jacobians
        """
        results = self.results[self.count]
        minimizer_list = self.minimizer_list[self.count]
        self.count += 1
        return results, self.chi_sq, minimizer_list

    def test_run_minimzers_none_selected(self):
        """
        Tests that no minimizers are selected
        """
        self.options.algorithm_type = ["ls"]
        results_problem, minimizer_failed, new_minimizer_list = \
            loop_over_minimizers(self.controller, self.minimizers,
                                 self.options, self.grabbed_output)
        assert results_problem == []
        assert minimizer_failed == self.minimizers
        assert new_minimizer_list == []

    @unittest.mock.patch('{}.loop_over_jacobians'.format(FITTING_DIR))
    def test_run_minimzers_selected(self, loop_over_jacobians):
        """
        Tests that some minimizers are selected
        """
        self.options.algorithm_type = ["general"]
        self.results = [[self.result_args]]
        self.chi_sq = 1
        self.minimizer_list = [["general"]]
        loop_over_jacobians.side_effect = self.mock_func_call

        results_problem, minimizer_failed, new_minimizer_list = \
            loop_over_minimizers(self.controller, self.minimizers,
                                 self.options, self.grabbed_output)
        assert all(isinstance(x, fitbm_result.FittingResult)
                   for x in results_problem)
        assert minimizer_failed == ["deriv_free_algorithm"]
        assert new_minimizer_list == ["general"]

    @unittest.mock.patch('{}.loop_over_jacobians'.format(FITTING_DIR))
    def test_run_minimzers_all(self, loop_over_jacobians):
        """
        Tests that all minimizers are selected
        """
        self.results = [[self.result_args], [self.result_args]]
        self.chi_sq = [1]
        self.minimizer_list = [["general"], ["deriv_free_algorithm"]]
        loop_over_jacobians.side_effect = self.mock_func_call

        results_problem, minimizer_failed, new_minimizer_list = \
            loop_over_minimizers(self.controller, self.minimizers,
                                 self.options, self.grabbed_output)
        assert all(isinstance(x, fitbm_result.FittingResult)
                   for x in results_problem)
        assert minimizer_failed == []
        assert new_minimizer_list == ["general", "deriv_free_algorithm"]

    def test_no_bounds_minimizer(self):
        """
        Test that if a minimizer that doesn't support bounds is
        selected with a bounded problem, results have the
        correct error flag
        """
        self.controller.problem.value_ranges = {'test': (0, 1)}
        self.minimizers = ["general"]

        results_problem, minimizer_failed, new_minimizer_list = \
            loop_over_minimizers(self.controller, self.minimizers,
                                 self.options, self.grabbed_output)

        assert results_problem[0].error_flag == 4
        assert minimizer_failed == []
        assert new_minimizer_list == ["general"]


if __name__ == "__main__":
    unittest.main()
