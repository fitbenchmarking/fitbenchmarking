"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_fitting_software
"""
from __future__ import (absolute_import, division, print_function)
import inspect
import os
import unittest
import numpy as np

from fitbenchmarking import mock_problems
from fitbenchmarking.utils import fitbm_result, output_grabber
from fitbenchmarking.core.fitting_benchmarking import \
    loop_over_fitting_software
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.options import Options
from fitbenchmarking.jacobian.SciPyFD_2point_jacobian import ScipyTwoPoint
from fitbenchmarking.utils.exceptions import UnsupportedMinimizerError

# Defines the module which we mock out certain function calls for
FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"

# Due to structure of tests, some variables may not be previously defined
# in the init function
# pylint: disable=attribute-defined-outside-init
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


class LoopOverSoftwareTests(unittest.TestCase):
    """
    loop_over_fitting_software tests
    """

    def setUp(self):
        """
        Setting up problem for tests
        """
        self.problem = make_fitting_problem()
        self.options = self.problem.options
        self.options.software = ["scipy", "dfo"]
        self.minimizers = self.options.minimizers
        self.grabbed_output = output_grabber.OutputGrabber(self.options)
        self.start_values_index = 0
        self.scipy_len = len(self.options.minimizers["scipy"])
        self.dfo_len = len(self.options.minimizers["dfo"])
        self.result_args = {'options': self.options,
                            'problem': self.problem,
                            'jac': self.problem.jac,
                            'initial_params': self.problem.starting_values[0],
                            'params': [],
                            'chi_sq': 1}

    def mock_func_call(self, *args, **kwargs):
        """
        Mock function to be used instead of loop_over_minimizers
        """
        minimizer_failed = self.minimizer_failed[self.count]
        results_problem = self.results_problem[self.count]
        self.count += 1
        return results_problem, minimizer_failed

    def shared_test(self, expected_list_len, expected_problem_fails,
                    expected_minimizer_failed):
        """
        Shared tests for the `loop_over_fitting_software` function

        :param expected_list_len: number of expect fitting results
        :type expected_list_len: int
        :param expected_problem_fails: expected list of failed problems
        :type expected_problem_fails: list
        :param expected_minimizer_failed: expected list of failed minimizers
        :type expected_minimizer_failed: list
        """
        results, problem_fails, unselected_minimzers = \
            loop_over_fitting_software(self.problem,
                                       self.options,
                                       self.start_values_index,
                                       self.grabbed_output)
        assert len(results) == expected_list_len
        assert problem_fails == expected_problem_fails
        for i, (keys, values) in enumerate(unselected_minimzers.items()):
            assert keys in self.options.software
            assert values == expected_minimizer_failed[i]

    @unittest.mock.patch('{}.loop_over_minimizers'.format(FITTING_DIR))
    def test_run_software(self, loop_over_minimizers):
        """
        Checks that results are produced for all minimizers within the
        softwares
        """
        self.count = 0
        self.minimizer_failed = [[], []]
        self.problem_fails = []
        self.results_problem = \
            [[fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_len)],
             [fitbm_result.FittingResult(**self.result_args)
              for i in range(self.dfo_len)]]
        loop_over_minimizers.side_effect = self.mock_func_call
        expected_list_len = self.scipy_len + self.dfo_len
        expected_problem_fails = self.problem_fails
        expected_minimizer_failed = self.minimizer_failed
        self.shared_test(expected_list_len, expected_problem_fails,
                         expected_minimizer_failed)

    @unittest.mock.patch('{}.loop_over_minimizers'.format(FITTING_DIR))
    def test_run_software_failed_minimizers(self, loop_over_minimizers):
        """
        Checks that the failed minimizers are reported
        """
        self.count = 0
        self.minimizer_failed = [['Powell'], ['dfogn', 'dfols']]
        failed_scipy = 1
        failed_dfo = 2
        self.problem_fails = []
        self.results_problem = \
            [[fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_len - failed_scipy)],
             [fitbm_result.FittingResult(**self.result_args)
              for i in range(self.dfo_len - failed_dfo)]]
        loop_over_minimizers.side_effect = self.mock_func_call
        expected_list_len = self.scipy_len + self.dfo_len - \
            failed_scipy - failed_dfo
        expected_problem_fails = self.problem_fails
        expected_minimizer_failed = self.minimizer_failed
        self.shared_test(expected_list_len, expected_problem_fails,
                         expected_minimizer_failed)

    @unittest.mock.patch('{}.loop_over_minimizers'.format(FITTING_DIR))
    def test_run_software_all_failed_minimizers(self, loop_over_minimizers):
        """
        Tests that when all minimizers raise and exception for a problem
        that this is reported correctly
        """
        self.count = 0
        self.minimizer_failed = [self.options.minimizers[s]
                                 for s in self.options.software]
        self.result_args['chi_sq'] = np.inf
        self.problem_fails = ['cubic']
        self.results_problem = [[fitbm_result.FittingResult(**self.result_args)
                                 for i in range(self.scipy_len)],
                                [fitbm_result.FittingResult(**self.result_args)
                                 for i in range(self.dfo_len)]]
        loop_over_minimizers.side_effect = self.mock_func_call
        expected_list_len = 0
        expected_problem_fails = self.problem_fails
        expected_minimizer_failed = self.minimizer_failed
        self.shared_test(expected_list_len, expected_problem_fails,
                         expected_minimizer_failed)

    def test_incorrect_software(self):
        """
        Tests an exception is raised when an incorrect software is selected
        """
        self.options.software = ['incorrect_software']
        with self.assertRaises(UnsupportedMinimizerError):
            _, _, _ = \
                loop_over_fitting_software(self.problem,
                                           self.options,
                                           self.start_values_index,
                                           self.grabbed_output)


if __name__ == "__main__":
    unittest.main()
