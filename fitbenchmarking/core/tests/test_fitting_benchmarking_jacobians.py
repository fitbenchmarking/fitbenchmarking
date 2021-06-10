"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_jacobians
"""
import inspect
import os
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.core.fitting_benchmarking import loop_over_jacobians
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import output_grabber
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
        results, _, new_minimizer_list = \
            loop_over_jacobians(self.controller,
                                self.options,
                                self.grabbed_output)
        assert all(isinstance(x, dict) for x in results)
        assert all(x["minimizer"] == name for x,
                   name in zip(results, new_name))
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
        results, _, new_minimizer_list = \
            loop_over_jacobians(self.controller,
                                self.options,
                                self.grabbed_output)
        assert all(isinstance(x, dict) for x in results)
        assert all(x["minimizer"] == name for x,
                   name in zip(results, new_name))
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
        results, _, new_minimizer_list = \
            loop_over_jacobians(self.controller,
                                self.options,
                                self.grabbed_output)
        assert all(isinstance(x, dict) for x in results)
        assert all(x["minimizer"] == name for x,
                   name in zip(results, new_name))
        assert new_minimizer_list == new_name

    # pylint: disable=unused-argument
    @unittest.mock.patch.object(DummyController, "cleanup")
    @unittest.mock.patch.object(DummyController, "check_bounds_respected")
    def test_bounds_respected_func_called(
            self, check_bounds_respected, cleanup):
        """
        Test that the check to verify that bounds are respected is called when
        the controller runs succesfully.
        """
        self.controller.problem.value_ranges = {'test': (0, 1)}
        self.controller.has_jacobian = [True]
        self.controller.invalid_jacobians = ["deriv_free_algorithm"]
        self.controller.minimizer = "deriv_free_algorithm"

        # Cleanup has been mocked out with a no-op, so set the outputs now.
        self.controller.flag = 0
        self.controller.final_params = [1, 2, 3, 4]

        _ = loop_over_jacobians(self.controller,
                                self.options,
                                self.grabbed_output)
        check_bounds_respected.assert_called()

    @unittest.mock.patch.object(DummyController, "cleanup")
    @unittest.mock.patch.object(DummyController, "check_bounds_respected")
    def test_bounds_respected_func_not_called(
            self, check_bounds_respected, cleanup):
        """
        Test that the check to verify that bounds are respected is not called
        when the controller fails.
        """
        self.controller.problem.value_ranges = {'test': (0, 1)}
        self.controller.has_jacobian = [True]
        self.controller.invalid_jacobians = ["deriv_free_algorithm"]
        self.controller.minimizer = "deriv_free_algorithm"

        # Cleanup has been mocked out with a no-op, so set the outputs now.
        self.controller.flag = 3
        self.controller.final_params = [1, 2, 3, 4]

        _ = loop_over_jacobians(self.controller,
                                self.options,
                                self.grabbed_output)
        check_bounds_respected.assert_not_called()
    # pylint: enable=unused-argument


if __name__ == "__main__":
    unittest.main()
