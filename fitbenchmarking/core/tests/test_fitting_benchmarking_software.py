"""
Tests for fitbenchmarking.core.fitting_benchmarking.loop_over_fitting_software
"""
import inspect
import os
import unittest

import numpy as np

from fitbenchmarking import test_files
from fitbenchmarking.controllers.scipy_controller import ScipyController
from fitbenchmarking.core.fitting_benchmarking import \
    loop_over_fitting_software
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import fitbm_result, output_grabber
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.exceptions import UnsupportedMinimizerError
from fitbenchmarking.utils.options import Options

# Defines the module which we mock out certain function calls for
FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"


# Due to structure of tests, some variables may not be previously defined
# in the init function
# pylint: disable=attribute-defined-outside-init
def make_cost_function(file_name='cubic.dat', minimizers=None):
    """
    Helper function that returns a simple fitting problem
    """
    options = Options(additional_options={'external_output': 'debug'})
    if minimizers:
        options.minimizers = minimizers

    bench_prob_dir = os.path.dirname(inspect.getfile(test_files))
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


class LoopOverSoftwareTests(unittest.TestCase):
    """
    loop_over_fitting_software tests
    """

    def setUp(self):
        """
        Setting up problem for tests
        """
        self.cost_func = make_cost_function()
        problem = self.cost_func.problem
        self.options = problem.options
        self.options.software = ["scipy", "dfo", "scipy_ls"]
        self.grabbed_output = output_grabber.OutputGrabber(self.options)
        self.start_values_index = 0
        self.scipy_len = len(self.options.minimizers["scipy"])
        self.dfo_len = len(self.options.minimizers["dfo"])
        self.scipy_ls_len = len(self.options.minimizers["scipy_ls"])
        controller = ScipyController(self.cost_func)
        controller.parameter_set = 0
        self.result_args = {'controller': controller,
                            'accuracy': 1,
                            'runtimes': [1]}
        self.cp = Checkpoint(self.options)

    def mock_func_call(self, *args, **kwargs):
        """
        Mock function to be used instead of loop_over_minimizers
        """
        minimizer_failed = list(self.minimizer_failed.values())[self.count]
        results_problem = self.results_problem[self.count]
        self.count += 1
        return results_problem, minimizer_failed

    def shared_test(self, expected_list_len, expected_minimizer_failed):
        """
        Shared tests for the `loop_over_fitting_software` function

        :param expected_list_len: number of expect fitting results
        :type expected_list_len: int
        :param expected_minimizer_failed: expected dict of failed minimizers
        :type expected_minimizer_failed: dict
        """
        results, unselected_minimzers = \
            loop_over_fitting_software(
                self.cost_func,
                options=self.options,
                start_values_index=self.start_values_index,
                grabbed_output=self.grabbed_output,
                checkpointer=self.cp)
        assert len(results) == expected_list_len

        dict_test(unselected_minimzers, expected_minimizer_failed)

    @unittest.mock.patch(f'{FITTING_DIR}.loop_over_minimizers')
    def test_run_one_software(self, loop_over_minimizers):
        """
        Checks that results are produced for one minimizer within the
        softwares
        """
        self.count = 0
        self.options.software = ["scipy"]
        self.minimizer_failed = {'scipy': []}
        self.results_problem = \
            [[fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_len)]]
        loop_over_minimizers.side_effect = self.mock_func_call
        expected_list_len = self.scipy_len
        expected_minimizer_failed = self.minimizer_failed
        self.shared_test(expected_list_len, expected_minimizer_failed)

    @unittest.mock.patch(f'{FITTING_DIR}.loop_over_minimizers')
    def test_run_multiple_softwares(self, loop_over_minimizers):
        """
        Checks that results are produced for all minimizers within the
        softwares when the variable software is wrapped a tdqm object.
        """

        self.count = 0
        self.minimizer_failed = {'scipy': [], 'dfo': [], 'scipy_ls': []}
        self.results_problem = \
            [[fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_len)],
             [fitbm_result.FittingResult(**self.result_args)
              for i in range(self.dfo_len)],
             [fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_ls_len)]]

        loop_over_minimizers.side_effect = self.mock_func_call
        expected_list_len = self.scipy_len + self.dfo_len + self.scipy_ls_len
        expected_minimizer_failed = self.minimizer_failed
        self.shared_test(expected_list_len, expected_minimizer_failed)

    @unittest.mock.patch(f'{FITTING_DIR}.loop_over_minimizers')
    def test_run_software_failed_minimizers(self, loop_over_minimizers):
        """
        Checks that the failed minimizers are reported
        """
        self.count = 0
        self.minimizer_failed = {'scipy': ['Powell'],
                                 'dfo': ['dfogn', 'dfols'],
                                 'scipy_ls': ['dogbox']}
        failed_scipy = 1
        failed_dfo = 2
        failed_scipy_ls = 1
        self.results_problem = \
            [[fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_len - failed_scipy)],
             [fitbm_result.FittingResult(**self.result_args)
              for i in range(self.dfo_len - failed_dfo)],
             [fitbm_result.FittingResult(**self.result_args)
              for i in range(self.scipy_ls_len - failed_scipy_ls)]]
        loop_over_minimizers.side_effect = self.mock_func_call
        expected_list_len = self.scipy_len + self.dfo_len +  \
            self.scipy_ls_len - failed_scipy - failed_dfo - failed_scipy_ls
        expected_minimizer_failed = self.minimizer_failed
        self.shared_test(expected_list_len, expected_minimizer_failed)

    @unittest.mock.patch(f'{FITTING_DIR}.loop_over_minimizers')
    def test_run_software_all_failed_minimizers(self, loop_over_minimizers):
        """
        Tests that when all minimizers raise an exception for a problem, it
        is reported correctly and no results are excluded.
        """
        self.count = 0
        self.minimizer_failed = {s: self.options.minimizers[s]
                                 for s in self.options.software}

        self.result_args['accuracy'] = np.inf
        self.results_problem = [[fitbm_result.FittingResult(**self.result_args)
                                 for i in range(self.scipy_len)],
                                [fitbm_result.FittingResult(**self.result_args)
                                 for i in range(self.dfo_len)],
                                [fitbm_result.FittingResult(**self.result_args)
                                 for i in range(self.scipy_ls_len)]]
        loop_over_minimizers.side_effect = self.mock_func_call
        expected_list_len = 14
        expected_minimizer_failed = self.minimizer_failed
        self.shared_test(expected_list_len, expected_minimizer_failed)

    def test_incorrect_software(self):
        """
        Tests an exception is raised when an incorrect software is selected
        """
        self.options.software = ['incorrect_software']
        with self.assertRaises(UnsupportedMinimizerError):
            _ = loop_over_fitting_software(
                self.cost_func,
                options=self.options,
                start_values_index=self.start_values_index,
                grabbed_output=self.grabbed_output,
                checkpointer=self.cp)


if __name__ == "__main__":
    unittest.main()
