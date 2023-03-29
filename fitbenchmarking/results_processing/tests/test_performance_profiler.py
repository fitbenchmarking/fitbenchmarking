"""
Tests for the performance profiler file.
"""

import inspect
import os
import unittest
import numpy as np

from fitbenchmarking import test_files
from fitbenchmarking.core.results_output import preprocess_data
from fitbenchmarking.results_processing import performance_profiler
from fitbenchmarking.utils.checkpoint import Checkpoint
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

    cp = Checkpoint(options)
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

        min_acc = 0.2
        self.accuracy_expected = {
            'm00 [s0]: j:j0': [np.inf, np.inf],
            'm00 [s0]: j:j1': [np.inf, np.inf],
            'm01 [s0]: j:j0': [0.4, 2.0],
            'm01 [s0]: j:j1': [0.8, 0.2],
            'm10 [s1]: j:j0': [0.2, 1.0],
            'm10 [s1]: j:j1': [0.6, 3.0],
            'm11 [s1]: j:j0': [0.3, 1.0],
            'm11 [s1]: j:j1': [0.7, 3.0],
        }
        for k in self.accuracy_expected:
            self.accuracy_expected[k] = [
                v/min_acc for v in self.accuracy_expected[k]]

        min_runtime = 1.0
        self.runtime_expected = {
            'm00 [s0]: j:j0': [np.inf, np.inf],
            'm00 [s0]: j:j1': [np.inf, np.inf],
            'm01 [s0]: j:j0': [13.0, 2.0],
            'm01 [s0]: j:j1': [1.0, 15.0],
            'm10 [s1]: j:j0': [15.0, 1.0],
            'm10 [s1]: j:j1': [11.0, 3.0],
            'm11 [s1]: j:j0': [14.0, 1.0],
            'm11 [s1]: j:j1': [10.0, 3.0],
        }
        for k in self.runtime_expected:
            self.runtime_expected[k] = [
                v/min_runtime for v in self.runtime_expected[k]]

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
        acc, runtime = performance_profiler.prepare_profile_data(self.results)

        for k, v in self.accuracy_expected.items():
            assert np.allclose(v, acc[k])
        for k, v in self.runtime_expected.items():
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
