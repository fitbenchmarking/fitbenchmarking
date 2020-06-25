"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_fitting_software
"""
from __future__ import (absolute_import, division, print_function)
import inspect
import mock
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

fitting_benchmarking_dir = "fitbenchmarking.core.fitting_benchmarking"


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
        self.problem = make_fitting_problem()
        self.options = self.problem.options
        self.options.software = ["scipy", "ralfit"]
        self.minimizers = self.options.minimizers
        self.grabbed_output = output_grabber.OutputGrabber(self.options)
        self.start_values_index = 0
        self.scipy_len = len(self.options.minimizers["scipy"])
        self.ralfit_len = len(self.options.minimizers["ralfit"])
        self.result_args = {'options': self.options,
                            'problem': self.problem,
                            'jac': self.problem.jac,
                            'initial_params': self.problem.starting_values[0],
                            'params': [],
                            'chi_sq': 1}

    def mock_func_call(self, *args, **kwargs):
        minimizer_failed = self.minimizer_failed[self.count]
        results_problem = self.results_problem[self.count]
        self.count += 1
        return results_problem, minimizer_failed

    @mock.patch('{}.loop_over_minimizers'.format(fitting_benchmarking_dir))
    def test_run_software(self, loop_over_minimizers):
        """
        Checks that results are produced for all minimizers within the
        softwares
        """
        self.count = 0
        self.minimizer_failed = [[], []]
        self.results_problem = \
            [[fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_len)],
             [fitbm_result.FittingResult(**self.result_args)
              for i in range(self.ralfit_len)]]
        loop_over_minimizers.side_effect = self.mock_func_call
        results, problem_fails, unselected_minimzers = \
            loop_over_fitting_software(self.problem,
                                       self.options,
                                       self.start_values_index,
                                       self.grabbed_output)
        assert len(results) == self.scipy_len + self.ralfit_len
        assert problem_fails == []
        for keys, values in unselected_minimzers.items():
            assert keys in self.options.software
            assert values == []

    @mock.patch('{}.loop_over_minimizers'.format(fitting_benchmarking_dir))
    def test_run_software_failed_minimizers(self, loop_over_minimizers):
        """
        Checks that the failed minimizers are reported
        """
        self.count = 0
        self.minimizer_failed = [['Powell'], ['gn', 'gn_reg']]
        failed_scipy = 1
        failed_ralfit = 2
        self.results_problem = \
            [[fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_len - failed_scipy)],
             [fitbm_result.FittingResult(**self.result_args)
              for i in range(self.ralfit_len - failed_ralfit)]]
        loop_over_minimizers.side_effect = self.mock_func_call
        results, problem_fails, unselected_minimzers = \
            loop_over_fitting_software(self.problem,
                                       self.options,
                                       self.start_values_index,
                                       self.grabbed_output)
        assert len(results) == self.scipy_len + \
            self.ralfit_len - failed_scipy - failed_ralfit
        assert problem_fails == []
        i = 0
        for keys, values in unselected_minimzers.items():
            assert keys in self.options.software
            assert values == self.minimizer_failed[i]
            i += 1

    @mock.patch('{}.loop_over_minimizers'.format(fitting_benchmarking_dir))
    def test_run_software_all_failed_minimizers(self, loop_over_minimizers):
        """
        Tests that when all minimizers raise and exception for a problem
        that this is reported correctly
        """
        self.count = 0
        self.minimizer_failed = [self.options.minimizers[s]
                                 for s in self.options.software]
        failed_scipy = 1
        failed_ralfit = 2
        self.result_args['chi_sq'] = np.inf
        self.results_problem = \
            [[fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_len - failed_scipy)],
             [fitbm_result.FittingResult(**self.result_args)
              for i in range(self.ralfit_len - failed_ralfit)]]
        loop_over_minimizers.side_effect = self.mock_func_call
        results, problem_fails, unselected_minimzers = \
            loop_over_fitting_software(self.problem,
                                       self.options,
                                       self.start_values_index,
                                       self.grabbed_output)
        assert len(results) == 0
        assert problem_fails == ['cubic']
        i = 0
        for keys, values in unselected_minimzers.items():
            assert keys in self.options.software
            assert values == self.minimizer_failed[i]
            i += 1


if __name__ == "__main__":
    unittest.main()
