"""
Tests for
fitbenchmarking.core.fitting_benchmarking.loop_over_benchmark_problems
"""
import inspect
import os
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.core.fitting_benchmarking import \
    loop_over_benchmark_problems
from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import fitbm_result
from fitbenchmarking.utils.options import Options

# Defines the module which we mock out certain function calls for
FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"


# Due to structure of tests, some variables may not be previously defined
# in the init function.
# pylint: disable=attribute-defined-outside-init
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
    cost_func = WeightedNLLSCostFunc(fitting_problem)
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


class LoopOverBenchmarkProblemsTests(unittest.TestCase):
    """
    loop_over_starting_values tests
    """

    def setUp(self):
        """
        Setting up problem for tests
        """
        self.cost_func = make_cost_function()
        self.problem = self.cost_func.problem
        self.options = Options()
        self.options.software = ["scipy"]
        self.scipy_len = len(self.options.minimizers["scipy"])
        bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
        self.default_parsers_dir = os.path.join(bench_prob_dir,
                                                "default_parsers")
        self.count = 0
        self.result_args = {'options': self.options,
                            'cost_func': self.cost_func,
                            'jac': 'jac',
                            'hess': 'hess',
                            'initial_params': self.problem.starting_values[0],
                            'params': [],
                            'chi_sq': 1}
        self.list_results = [fitbm_result.FittingResult(**self.result_args)
                             for i in range(self.scipy_len)]
        self.individual_problem_results = [
            self.list_results, self.list_results]

    def mock_func_call(self, *args, **kwargs):
        """
        Mock function to be used instead of loop_over_starting_values
        """
        individual_problem_results = \
            self.individual_problem_results[self.count]
        problem_fails = self.problem_fails
        unselected_minimizers = {"scipy": []}
        self.count += 1
        return individual_problem_results, problem_fails, \
            unselected_minimizers

    def shared_tests(self, list_len, expected_problem_fails):
        """
        Shared tests for the `loop_over_starting_values` function

        :param list_len: number of expect fitting results
        :type list_len: int
        :param expected_problem_fails: list of problems which fail
        :type expected_problem_fails: list
        """
        results, failed_problems, unselected_minimizers = \
            loop_over_benchmark_problems(self.problem_group, self.options)
        assert len(results) == list_len
        assert failed_problems == expected_problem_fails
        dict_test(unselected_minimizers, {"scipy": []})

    @unittest.mock.patch('{}.loop_over_starting_values'.format(FITTING_DIR))
    def test_run_multiple_benchmark_problems(self, loop_over_starting_values):
        """
        Checks that all benchmark problems run with no failures
        """
        self.problem_fails = []
        loop_over_starting_values.side_effect = self.mock_func_call

        self.problem_group = []
        for file_name in ["cubic.dat", "prob_def_1.txt"]:
            self.problem_group.append(
                os.path.join(self.default_parsers_dir, file_name))
        expected_problem_fails = self.problem_fails
        expected_list_length = len(self.list_results) * 2
        self.shared_tests(expected_list_length, expected_problem_fails)

    @unittest.mock.patch('{}.loop_over_starting_values'.format(FITTING_DIR))
    def test_run_multiple_failed_problems(self, loop_over_starting_values):
        """
        Checks that multiple failed problems are reported correctly
        """
        self.problem_fails = ['Random_failed_problem_1',
                              'Random_failed_problem_2']
        loop_over_starting_values.side_effect = self.mock_func_call
        self.problem_group = [os.path.join(self.default_parsers_dir,
                                           "cubic.dat")]

        expected_problem_fails = self.problem_fails
        expected_list_length = len(self.list_results)
        self.shared_tests(expected_list_length, expected_problem_fails)


if __name__ == "__main__":
    unittest.main()
