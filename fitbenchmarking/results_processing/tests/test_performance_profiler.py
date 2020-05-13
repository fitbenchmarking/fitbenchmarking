"""
Tests for the performance profiler file.
"""
from __future__ import absolute_import, division, print_function

import unittest
from collections import OrderedDict

import numpy as np

from fitbenchmarking.core.results_output import preproccess_data
from fitbenchmarking.jacobian.SciPyFD_2point_jacobian import ScipyTwoPoint
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.results_processing import performance_profiler
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


class PerformanceProfillerTests(unittest.TestCase):
    """
    General tests for the performance profiler code.
    """

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
            acc_results = acc_in[i][:]
            acc_expected.append(list(acc_results) / np.min(acc_results))

            runtime_results = runtime_in[i][:]
            runtime_expected.append(
                list(runtime_results) / np.min(runtime_results))
            prob_results = []
            jac = ScipyTwoPoint(problem)
            for j in range(self.num_minimizers):
                minimizer = 'min_{}'.format(j)
                prob_results.append(FittingResult(options=options,
                                                  problem=problem,
                                                  jac=jac,
                                                  initial_params=[1, 2, 3],
                                                  params=[1, 2, 3],
                                                  chi_sq=acc_results[j],
                                                  runtime=runtime_results[j],
                                                  minimizer=minimizer))
            results.append(prob_results)
        return results, acc_expected, runtime_expected

    def setUp(self):
        self.results, self.acc_expected, self.runtime_expected = \
            self.generate_mock_results()
        _ = preproccess_data(self.results)
        self.fig_dir = ''

    def test_correct_prepare_profile_data(self):
        """
        Test that prepare profile data gives the correct result
        """
        acc, runtime = performance_profiler.prepare_profile_data(self.results)
        acc_expected = np.array(self.acc_expected).T
        runtime_expected = np.array(self.runtime_expected).T
        acc_dict = OrderedDict()
        runtime_dict = OrderedDict()
        for j in range(self.num_minimizers):
            acc_dict['min_{}'.format(j)] = acc_expected[j]
            runtime_dict['min_{}'.format(j)] = runtime_expected[j]
        for k, v in acc_dict.items():
            assert np.allclose(v, acc[k])
        for k, v in runtime_dict.items():
            assert np.allclose(v, runtime[k])

    def test_correct_profile(self):
        """
        Test that th performance profiler returns the expected paths
        """
        acc, runtime = performance_profiler.profile(self.results,
                                                    self.fig_dir)

        assert acc == "acc_profile.png"
        assert runtime == "runtime_profile.png"


if __name__ == "__main__":
    unittest.main()
