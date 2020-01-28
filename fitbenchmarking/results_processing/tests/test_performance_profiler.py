from __future__ import (absolute_import, division, print_function)
import numpy as np
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.core.results_output import preproccess_data
from fitbenchmarking.results_processing import performance_profiler
from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.fitbm_result import FittingResult


class PerformanceProfillerTests(unittest.TestCase):

    def generate_mock_results(self):
        num_problems = 5
        num_minizers = 3
        results = []
        self.options = Options()
        for i in range(num_problems):
            np.random.seed(i)
            acc_results = np.random.uniform(
                low=0, high=10000, size=(num_minizers,))
            np.random.seed(i + num_problems)
            runtime_results = np.random.uniform(
                low=0, high=10000, size=(num_minizers,))
            prob_results = []
            for j in range(num_minizers):
                minimizer = 'min_{}'.format(j)
                prob_results.append(FittingResult(options=self.options,
                                                  chi_sq=acc_results[j],
                                                  runtime=runtime_results[j],
                                                  minimizer=minimizer))
            results.append(prob_results)
        return results

    def setUp(self):
        self.results = self.generate_mock_results()
        _ = preproccess_data(self.results)
        self.correct_acc = {'min_0': [1, 3, 3, 3], 'min_1': [2, 3, 4, 4],
                            'min_2': [2, 4, 4, 4]}
        self.correct_runtime = {'min_0': [2, 4, 5, 5], 'min_1': [1, 2, 2, 2],
                                'min_2': [2, 2, 3, 3]}
        self.fig_dir = ''

    def test_correct_prepare_profile_data(self):
        acc, runtime = performance_profiler.prepare_profile_data(self.results)

        assert acc == self.correct_acc
        assert runtime == self.correct_runtime

    def test_correct_profile(self):
        acc, runtime = performance_profiler.profile(self.options,
                                                     self.results,
                                                     self.fig_dir)

        assert acc == "acc_profile.png"
        assert runtime == "runtime_profile.png"

    def test_incorrect_profile(self):
        self.options.make_plots = False
        acc, runtime = performance_profiler.profile(self.options,
                                                     self.results,
                                                     self.fig_dir)

        assert acc == False
        assert runtime == False


if __name__ == "__main__":
    unittest.main()
