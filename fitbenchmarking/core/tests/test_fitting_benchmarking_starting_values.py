"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_starting_values
"""
from __future__ import (absolute_import, division, print_function)
import inspect
import os
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.utils import fitbm_result, output_grabber
from fitbenchmarking.core.fitting_benchmarking import loop_over_starting_values
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.options import Options
from fitbenchmarking.jacobian.SciPyFD_2point_jacobian import ScipyTwoPoint

# Defines the module which we mock out certain function calls for
FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"


# Due to structure of tests, some variables may not be previously defined
# in the init function. Removes pytest dictionary iteration suggestion
# pylint: disable=attribute-defined-outside-init, consider-iterating-dictionary
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


class LoopOverStartingValuesTests(unittest.TestCase):
    """
    loop_over_starting_values tests
    """

    def setUp(self):
        """
        Setting up problem for tests
        """
        self.problem = make_fitting_problem()
        self.options = self.problem.options
        self.options.software = ["scipy"]
        self.minimizers = self.options.minimizers
        self.grabbed_output = output_grabber.OutputGrabber(self.options)
        self.count = 0
        self.scipy_len = len(self.options.minimizers["scipy"])
        self.result_args = {'options': self.options,
                            'problem': self.problem,
                            'jac': self.problem.jac,
                            'initial_params': self.problem.starting_values[0],
                            'params': [],
                            'chi_sq': 1}

    def mock_func_call(self, *args, **kwargs):
        """
        Mock function to be used instead of loop_over_fitting_software
        """
        individual_problem_results = \
            self.individual_problem_results[self.count]
        problem_fails = self.problem_fails
        unselected_minimzers = self.unselected_minimzers
        self.count += 1
        return individual_problem_results, problem_fails, unselected_minimzers

    def shared_tests(self, expected_list_len, expected_problem_fails,
                     expected_unselected_minimzers):
        """
        Shared tests for the `loop_over_starting_values` function

        :param expected_list_len: number of expect fitting results
        :type expected_list_len: int
        :param expected_problem_fails: Expected list of failed problems
        :type expected_problem_fails: list
        :param expected_unselected_minimzers: Expected dictionary of unselected
                                              minimizer
        :type expected_unselected_minimzers: dict
        """
        problem_results, problem_fails, unselected_minimzers = \
            loop_over_starting_values(self.problem,
                                      self.options,
                                      self.grabbed_output)
        assert len(problem_results) == expected_list_len
        assert problem_fails == expected_problem_fails

        for key in unselected_minimzers.keys():
            assert key in expected_unselected_minimzers.keys()
            assert sorted(unselected_minimzers[key]) == \
                sorted(expected_unselected_minimzers[key])

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
        self.unselected_minimzers = {"scipy": []}
        loop_over_fitting_software.side_effect = self.mock_func_call
        expected_list_length = len(list_results) * 2
        expected_problem_fails = self.problem_fails
        expected_unselected_minimzers = self.unselected_minimzers
        self.shared_tests(expected_list_length, expected_problem_fails,
                          expected_unselected_minimzers)

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
        self.unselected_minimzers = {"scipy": []}
        loop_over_fitting_software.side_effect = self.mock_func_call
        expected_list_length = len(self.individual_problem_results[0])
        expected_problem_fails = self.problem_fails
        expected_unselected_minimzers = self.unselected_minimzers
        self.shared_tests(expected_list_length, expected_problem_fails,
                          expected_unselected_minimzers)

    @unittest.mock.patch('{}.loop_over_fitting_software'.format(FITTING_DIR))
    def test_run_reports_failed_problems(self, loop_over_fitting_software):
        """
        Checks that the failed problems are reported correctly
        """
        list_results = [fitbm_result.FittingResult(**self.result_args)
                        for i in range(self.scipy_len)]
        self.individual_problem_results = [list_results, list_results]
        self.problem_fails = ['Cubic_failed']
        self.unselected_minimzers = {"scipy": []}
        loop_over_fitting_software.side_effect = self.mock_func_call
        expected_list_length = len(list_results) * 2
        expected_problem_fails = self.problem_fails
        expected_unselected_minimzers = self.unselected_minimzers
        self.shared_tests(expected_list_length, expected_problem_fails,
                          expected_unselected_minimzers)

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
        self.unselected_minimzers = {"scipy": ['Powell', 'CG']}
        loop_over_fitting_software.side_effect = self.mock_func_call
        expected_list_length = len(list_results) * 2
        expected_problem_fails = self.problem_fails
        expected_unselected_minimzers = self.unselected_minimzers
        self.shared_tests(expected_list_length, expected_problem_fails,
                          expected_unselected_minimzers)


if __name__ == "__main__":
    unittest.main()
