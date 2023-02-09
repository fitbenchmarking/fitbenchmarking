"""
Tests for the performance profiler file.
"""
from __future__ import absolute_import, division, print_function

import inspect
import os
import unittest
from collections import OrderedDict

import numpy as np

from fitbenchmarking import test_files
from fitbenchmarking.core.results_output import preprocess_data
from fitbenchmarking.results_processing import performance_profiler
from fitbenchmarking.utils.checkpoint import get_checkpoint
from fitbenchmarking.utils.options import Options


def load_mock_results():
    """
    Load a predictable results set.

    :return: Manually generated results
    :rtype: list[FittingResult]
    """
    options = Options()
    cp_dir = os.path.dirname(inspect.getfile(test_files))
    options.checkpoint_filename = os.path.join(cp_dir, 'checkpoint.json')

    cp = get_checkpoint(options)
    results, _, _ = cp.load()

    return [v
            for lst in results.values()
            for v in lst]


class PerformanceProfilerTests(unittest.TestCase):
    """
    General tests for the performance profiler code.
    """

    def setUp(self):
        """
        Sets up acc runtime profile names
        """
        results = load_mock_results()
        _, self.results = preprocess_data(results)

        self.accuracy_expected = np.array(
            [[0.2, 0.3, 0.4, np.inf, 0.6, 0.7, 0.8],
             [1.0, 1.0, 2.0, np.inf, 3.0, 3.0, 0.2, np.inf]])
        self.runtime_expected = np.array(
            [[15.0, 14.0, 13.0, np.inf, 11.0, 10.0, 9.0],
             [1.0, 1.0, 2.0, np.inf, 3.0, 3.0, 15.0, np.inf]])

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

    def test_correct_prepare_profile_data(self):
        """
        Test that prepare profile data gives the correct result
        """

        list(list(self.results.values())[0].values())[0][0].jacobian_tag = ''
        acc, runtime = performance_profiler.prepare_profile_data(self.results)
        acc_expected = np.array(self.accuracy_expected).T
        runtime_expected = np.array(self.runtime_expected).T
        acc_dict = OrderedDict()
        runtime_dict = OrderedDict()
        for j, (a, r) in enumerate(zip(acc_expected, runtime_expected)):
            acc_dict['min_{} [s1]: j:j1'.format(j)] = a
            runtime_dict['min_{} [s1]: j:j1'.format(j)] = r
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
