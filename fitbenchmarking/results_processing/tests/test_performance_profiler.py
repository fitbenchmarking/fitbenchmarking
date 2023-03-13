"""
Tests for the performance profiler file.
"""

import os
import unittest
from collections import OrderedDict

import numpy as np

from fitbenchmarking.core.results_output import preprocess_data
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.results_processing import performance_profiler
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


class PerformanceProfilerTests(unittest.TestCase):
    """
    General tests for the performance profiler code.
    """

    def setUp(self):
        """
        Sets up acc runtime profile names
        """
        self.results, self.acc_expected, self.runtime_expected = \
            self.generate_mock_results()
        _, self.results = preprocess_data(self.results)
        self.fig_dir = ''
        self.acc_name = "acc_profile.png"
        self.runtime_name = "runtime_profile.png"

    def tearDown(self):
        """
        Removes expected acc and runtime plots
        """
        for name in [self.acc_name, self.runtime_name]:
            if os.path.isfile(name):
                os.remove(name)

    def generate_mock_results(self):
        """
        Generates results to test against

        :return: A list of results objects along with expected values for
                 normallised accuracy and runtimes
        :rtype: tuple(list of FittingResults,
                      list of list of float,
                      list of list of float)
        """
        self.num_problems = 4
        self.num_minimizers = 2
        results = []
        options = Options()
        problem = FittingProblem(options)
        problem.starting_values = [{'a': 1, 'b': 2, 'c': 3}]

        acc_in = [[1, 5],
                  [7, 3],
                  [10, 8],
                  [2, 3]]

        runtime_in = [[float('Inf'), 2.2e-3],
                      [3.0e-10, 5.0e-14],
                      [6.9e-7, 4.3e-5],
                      [1.6e-13, 1.8e-13]]

        acc_expected = []
        runtime_expected = []
        for i in range(self.num_problems):
            problem.name = f'problem {i}'
            acc_results = acc_in[i][:]
            acc_expected.append(list(acc_results) / np.min(acc_results))

            runtime_results = runtime_in[i][:]
            runtime_expected.append(
                list(runtime_results) / np.min(runtime_results))
            prob_results = []
            cost_func = NLLSCostFunc(problem)
            jac = 'j1'
            hess = None
            for j in range(self.num_minimizers):
                minimizer = 'min_{}'.format(j)
                prob_results.append(FittingResult(options=options,
                                                  cost_func=cost_func,
                                                  jac=jac,
                                                  hess=hess,
                                                  initial_params=[1, 2, 3],
                                                  params=[1, 2, 3],
                                                  chi_sq=acc_results[j],
                                                  runtime=runtime_results[j],
                                                  software='s1',
                                                  minimizer=minimizer))
            results.extend(prob_results)
        return results, acc_expected, runtime_expected

    def test_correct_prepare_profile_data(self):
        """
        Test that prepare profile data gives the correct result
        """
        list(list(self.results.values())[0].values())[0][0].jacobian_tag = ''
        acc, runtime = performance_profiler.prepare_profile_data(self.results)
        acc_expected = np.array(self.acc_expected).T
        runtime_expected = np.array(self.runtime_expected).T
        acc_dict = OrderedDict()
        runtime_dict = OrderedDict()
        for j in range(self.num_minimizers):
            acc_dict['min_{} [s1]: j:j1'.format(j)] = acc_expected[j]
            runtime_dict['min_{} [s1]: j:j1'.format(j)] = runtime_expected[j]
        for k, v in acc_dict.items():
            assert np.allclose(v, acc[k])
        for k, v in runtime_dict.items():
            assert np.allclose(v, runtime[k])

    # pylint: disable=W0632
    def test_correct_profile(self):
        """
        Test that the performance profiler returns the expected paths
        """
        acc, runtime = performance_profiler.profile(self.results,
                                                    self.fig_dir)

        assert acc == "acc_profile.png"
        assert runtime == "runtime_profile.png"
    # pylint: enable=W0632


if __name__ == "__main__":
    unittest.main()
