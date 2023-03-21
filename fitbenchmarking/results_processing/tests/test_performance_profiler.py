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


<< << << < HEAD
== == == =
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
                minimizer = f'min_{j}'
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

>>>>>> > master
    def test_correct_prepare_profile_data(self):
        """
        Test that prepare profile data gives the correct result
        """
        acc, runtime = performance_profiler.prepare_profile_data(self.results)
<< << << < HEAD

        for k, v in self.accuracy_expected.items():
== == == =
        acc_expected = np.array(self.acc_expected).T
        runtime_expected = np.array(self.runtime_expected).T
        acc_dict = {}
        runtime_dict = {}
        for j in range(self.num_minimizers):
            acc_dict[f'min_{j} [s1]: j:j1'] = acc_expected[j]
            runtime_dict[f'min_{j} [s1]: j:j1'] = runtime_expected[j]
        for k, v in acc_dict.items():
>>>>>> > master
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
