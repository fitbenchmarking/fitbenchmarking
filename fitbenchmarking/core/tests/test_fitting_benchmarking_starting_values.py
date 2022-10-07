"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_starting_values
"""
from __future__ import (absolute_import, division, print_function)
import inspect
import os
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.utils import fitbm_result, output_grabber
from fitbenchmarking.core.fitting_benchmarking import loop_over_starting_values
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.options import Options

# Defines the module which we mock out certain function calls for
FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"


# Due to structure of tests, some variables may not be previously defined
# in the init function. Removes pytest dictionary iteration suggestion
# pylint: disable=attribute-defined-outside-init, consider-iterating-dictionary
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


def dict_test(expected, actual):
    """
    Test to check two dictionaries are the same

    :param expected: expected dictionary result
    :type expected: dict
    :param actual: actual dictionary result
    :type actual: dict
    """
    for key in actual.keys():
        assert key in expected.keys()
        assert sorted(actual[key]) == sorted(expected[key])


class LoopOverStartingValuesTests(unittest.TestCase):
    """
    loop_over_starting_values tests
    """

    def setUp(self):
        """
        Setting up problem for tests
        """
        self.cost_func = make_cost_function()
        self.problem = self.cost_func.problem
        self.options = self.problem.options
        self.options.cost_func_type = ['weighted_nlls']
        self.options.software = ["scipy"]
        self.minimizers = self.options.minimizers
        self.grabbed_output = output_grabber.OutputGrabber(self.options)
        self.count = 0
        self.scipy_len = len(self.options.minimizers["scipy"])
        self.result_args = {'options': self.options,
                            'cost_func': self.cost_func,
                            'jac': 'jac',
                            'hess': 'hess',
                            'initial_params': self.problem.starting_values[0],
                            'params': [],
                            'chi_sq': 1}

    def mock_func_call(self, *args, **kwargs):
        """
        Mock function to be used instead of loop_over_fitting_software
        """
        individual_problem_results = \
            self.individual_problem_results[self.count]
        unselected_minimizers = self.unselected_minimizers
        self.count += 1
        return (individual_problem_results,
                unselected_minimizers)

    def shared_tests(self, expected_list_len, expected_problem_fails,
                     expected_unselected_minimizers):
        """
        Shared tests for the `loop_over_starting_values` function

        :param expected_list_len: number of expect fitting results
        :type expected_list_len: int
        :param expected_problem_fails: Expected list of failed problems
        :type expected_problem_fails: list
        :param expected_unselected_minimizers: Expected dictionary of
                                               unselected minimizer
        :type expected_unselected_minimizers: dict
        """
        problem_results, problem_fails, unselected_minimizers \
            = loop_over_starting_values(self.problem,
                                        self.options,
                                        self.grabbed_output)
        assert len(problem_results) == expected_list_len
        assert problem_fails == expected_problem_fails

        dict_test(unselected_minimizers, expected_unselected_minimizers)

    @unittest.mock.patch('{}.loop_over_fitting_software'.format(FITTING_DIR))
    def test_run_multiple_starting_values(self, loop_over_fitting_software):
        """
        Checks that all selected minimizers run with multiple starting
        values
        """
        list_results = [fitbm_result.FittingResult(**self.result_args)
                        for i in range(self.scipy_len)]
        self.individual_problem_results = [list_results, list_results]
        self.problem_fails = []
        self.unselected_minimizers = {"scipy": []}
        loop_over_fitting_software.side_effect = self.mock_func_call
        expected_list_length = len(list_results) * 2
        expected_problem_fails = self.problem_fails
        expected_unselected_minimizers = self.unselected_minimizers
        self.shared_tests(expected_list_length, expected_problem_fails,
                          expected_unselected_minimizers)

    @unittest.mock.patch('{}.loop_over_fitting_software'.format(FITTING_DIR))
    def test_run_one_starting_values(self, loop_over_fitting_software):
        """
        Checks that all selected minimizers run with one starting
        values
        """
        self.problem.starting_values = [self.problem.starting_values[0]]
        self.individual_problem_results = \
            [[fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_len)]]
        self.problem_fails = []
        self.unselected_minimizers = {"scipy": []}
        loop_over_fitting_software.side_effect = self.mock_func_call
        expected_list_length = len(self.individual_problem_results[0])
        expected_problem_fails = self.problem_fails
        expected_unselected_minimizers = self.unselected_minimizers
        self.shared_tests(expected_list_length, expected_problem_fails,
                          expected_unselected_minimizers)

    @unittest.mock.patch('{}.loop_over_fitting_software'.format(FITTING_DIR))
    def test_run_reports_unselected_minimizers(self,
                                               loop_over_fitting_software):
        """
        Checks that the unselected minimizers are reported correctly
        """
        list_results = [fitbm_result.FittingResult(**self.result_args)
                        for i in range(self.scipy_len)]
        self.individual_problem_results = [list_results, list_results]
        self.problem_fails = []
        self.unselected_minimizers = {"scipy": ['Powell', 'CG']}
        loop_over_fitting_software.side_effect = self.mock_func_call
        expected_list_length = len(list_results) * 2
        expected_problem_fails = self.problem_fails
        expected_unselected_minimizers = self.unselected_minimizers
        self.shared_tests(expected_list_length, expected_problem_fails,
                          expected_unselected_minimizers)


if __name__ == "__main__":
    unittest.main()
