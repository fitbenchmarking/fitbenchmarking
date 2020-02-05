from __future__ import (absolute_import, division, print_function)
from collections import OrderedDict
import numpy as np
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.core.results_output import preproccess_data
from fitbenchmarking.results_processing import performance_profiler
from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.fitbm_result import FittingResult


class PerformanceProfillerTests(unittest.TestCase):

    def generate_mock_results(self):
        self.num_problems = 5
        self.num_minizers = 3
        results = []
        options = Options()
        acc_expected = []
        runtime_expected = []
        for i in range(self.num_problems):
            np.random.seed(i)
            acc_results = np.random.uniform(
                low=0, high=10000, size=(self.num_minizers,))
            np.random.seed(i + self.num_problems)
            runtime_results = np.random.uniform(
                low=0, high=10000, size=(self.num_minizers,))
            acc_expected.append(list(acc_results) / np.min(acc_results))
            runtime_expected.append(
                list(runtime_results) / np.min(runtime_results))
            prob_results = []
            for j in range(self.num_minizers):
                minimizer = 'min_{}'.format(j)
                prob_results.append(FittingResult(options=options,
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
        acc, runtime = performance_profiler.prepare_profile_data(self.results)
        acc_expected = np.array(self.acc_expected).T
        runtime_expected = np.array(self.runtime_expected).T
        acc_dict = OrderedDict()
        runtime_dict = OrderedDict()
        for j in range(self.num_minizers):
            acc_dict['min_{}'.format(j)] = acc_expected[j]
            runtime_dict['min_{}'.format(j)] = runtime_expected[j]
        for k, v in acc_dict.items():
            assert np.allclose(v, acc[k])
        for k, v in runtime_dict.items():
            assert np.allclose(v, runtime[k])

    def test_correct_profile(self):
        acc, runtime = performance_profiler.profile(self.results,
                                                    self.fig_dir)

        assert acc == "acc_profile.png"
        assert runtime == "runtime_profile.png"


if __name__ == "__main__":
    unittest.main()
