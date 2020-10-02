"""
Tests for fitbenchmarking.core.fitting_benchmarking.benchmark
"""
from __future__ import (absolute_import, division, print_function)
import inspect
import copy
import os
import unittest
from unittest import mock

from fitbenchmarking import mock_problems
from fitbenchmarking.utils import fitbm_result
from fitbenchmarking.core.fitting_benchmarking import benchmark
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.options import Options
from fitbenchmarking.jacobian.SciPyFD_2point_jacobian import ScipyTwoPoint
from fitbenchmarking.utils.exceptions import NoResultsError

# Defines the module which we mock out certain function calls for
FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"


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


class BenchmarkTests(unittest.TestCase):
    """
    benchmark tests
    """

    def setUp(self):
        """
        Setting up problem for tests
        """
        self.problem = make_fitting_problem()
        self.options = Options()
        self.options.software = ["scipy"]
        self.scipy_len = len(self.options.minimizers["scipy"])
        bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
        self.default_parsers_dir = os.path.join(bench_prob_dir,
                                                "default_parsers")
        self.all_minimzers = copy.copy(self.options.minimizers)

    def shared_tests(self, expected_names, expected_unselected_minimzers,
                     expected_minimzers):
        """
        Shared tests for the `benchmark` function. The function test

        :param expected_names: expected sorted list of problem names
        :type expected_names: list
        :param expected_unselected_minimzers: expected unselected minimizers
        :type expected_unselected_minimzers: dict
        :param expected_minimzers: expected minimizers
        :type expected_minimzers: dict
        """
        results, failed_problems, unselected_minimzers = \
            benchmark(self.options, self.default_parsers_dir)

        assert len(results) == len(expected_names)
        for i, name in enumerate(expected_names):
            assert all(p.name == name for p in results[i])

        assert failed_problems == []
        dict_test(expected_unselected_minimzers, unselected_minimzers)
        dict_test(expected_minimzers, self.options.minimizers)

    @mock.patch('{}.loop_over_benchmark_problems'.format(FITTING_DIR))
    def test_check_no_unselected_minimizers(self,
                                            loop_over_benchmark_problems):
        """
        Checks benchmarking runs with no unselected minimizers
        """
        # define mock return for loop_over_benchmark_problems
        problem_names = ["random_1", "random_3", "random_2"]
        results = []
        for name in problem_names:
            result_args = {'options': self.options,
                           'problem': self.problem,
                           'jac': self.problem.jac,
                           'initial_params': self.problem.starting_values[0],
                           'params': [],
                           'chi_sq': 1,
                           'name': name}
            list_results = [fitbm_result.FittingResult(**result_args)
                            for j in range(self.scipy_len)]
            results.extend(list_results)
        problem_fails = []
        expected_unselected_minimzers = {"scipy": []}
        loop_over_benchmark_problems.return_value = \
            (results, problem_fails, expected_unselected_minimzers)

        # run shared test and see if it match expected
        expected_problem_names = sorted(problem_names)
        expected_minimzers = copy.copy(self.all_minimzers)
        self.shared_tests(expected_problem_names,
                          expected_unselected_minimzers,
                          expected_minimzers)

    @mock.patch('{}.loop_over_benchmark_problems'.format(FITTING_DIR))
    def test_check_unselected_minimizers(self, loop_over_benchmark_problems):
        """
        Checks benchmarking runs with a few unselected minimizers
        """
        # define mock return for loop_over_benchmark_problems
        problem_names = ["random_1", "random_3", "random_2"]
        expected_names = sorted(problem_names)
        results = []
        for name in problem_names:
            result_args = {'options': self.options,
                           'problem': self.problem,
                           'jac': self.problem.jac,
                           'initial_params': self.problem.starting_values[0],
                           'params': [],
                           'chi_sq': 1,
                           'name': name}
            list_results = [fitbm_result.FittingResult(**result_args)
                            for j in range(self.scipy_len)]
            results.extend(list_results)
        problem_fails = []
        expected_unselected_minimzers = {"scipy": ['SLSQP', 'Powell', 'CG']}
        loop_over_benchmark_problems.return_value = \
            (results, problem_fails, expected_unselected_minimzers)

        # run shared test and see if it match expected
        expected_minimzers = copy.copy(self.all_minimzers)
        for keys, minimzers in expected_unselected_minimzers.items():
            diff = set(expected_minimzers[keys]) - set(minimzers)
            expected_minimzers[keys] = [x for x in expected_minimzers[keys]
                                        if x in diff]

        self.shared_tests(expected_names, expected_unselected_minimzers,
                          expected_minimzers)


if __name__ == "__main__":
    unittest.main()
