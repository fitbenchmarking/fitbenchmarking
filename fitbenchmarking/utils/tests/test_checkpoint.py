"""
Tests for checkpoint.py
"""
import inspect
import pathlib
import pprint
from tempfile import TemporaryDirectory
from unittest import TestCase

import numpy as np

from fitbenchmarking import test_files
from fitbenchmarking.controllers.scipy_controller import ScipyController
from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.jacobian.default_jacobian import \
    Default as DefaultJacobian
from fitbenchmarking.jacobian.scipy_jacobian import Scipy as ScipyJacobian
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.checkpoint import Checkpoint, _compress, _decompress
from fitbenchmarking.utils.exceptions import CheckpointError
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


def generate_results():
    # pylint:disable=too-many-statements
    """
    Create a predictable set of results.
    :return: Set of manually generated results
    :rtype: dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]
    """
    options = Options()
    results = {}

    data_x = np.array([[1, 4, 5], [2, 1, 5]])
    data_y = np.array([[1, 2, 1], [2, 2, 2]])
    data_e = np.array([[1, 1, 1], [1, 2, 1]])
    func = [lambda d, x1, x2: x1 * np.sin(x2), lambda d, x1, x2: x1 * x2]
    name = ['prob_0', 'prob_1']
    problems = [FittingProblem(options), FittingProblem(options)]
    starting_values = [{"a": 0.3, "b": 0.11}, {"a": 0, "b": 0}]
    for p, x, y, e, f, n, s in zip(problems, data_x, data_y, data_e,
                                   func, name, starting_values):
        p.data_x = x
        p.data_y = y
        p.data_e = e
        p.function = f
        p.name = n
        p.starting_values = [s]
        p.description = f'Description for: {n}'
        p.equation = f'Equation for: {n}'
        p.plot_scale = 'logy'
        p.format = f'Format: {n}'

    for i, key in enumerate(['set1', 'set2']):
        jac = [DefaultJacobian(problems[i]),
               ScipyJacobian(problem=problems[i])]
        jac[1].method = '2-point'

        results[key] = []
        cost_func = WeightedNLLSCostFunc(problems[0])
        cost_func.jacobian = jac[0]
        controller = ScipyController(cost_func)
        controller.parameter_set = 0
        controller.minimizer = 'Powell'
        controller.prepare()
        controller.final_params = [0.1+i, 0.2+i]
        controller.iteration_count = 10
        controller.count_type = 'iterations'
        controller.flag = 0
        results[key].append(FittingResult(controller=controller,
                                          accuracy=0.02+i,
                                          runtimes=[0.15+i]))
        controller.minimizer = 'CG'
        controller.final_params = [0.3+i, 0.4+i]
        controller.flag = 2
        results[key].append(FittingResult(controller=controller,
                                          accuracy=0.3+i, runtimes=[0.01+i]))
        cost_func.jacobian = jac[1]
        controller = ScipyController(cost_func)
        controller.parameter_set = 0
        controller.minimizer = 'CG'
        controller.prepare()
        controller.final_params = [0.5+i, 0.6+i]
        controller.iteration_count = 10
        controller.count_type = 'iterations'
        controller.flag = 0
        results[key].append(FittingResult(controller=controller,
                                          accuracy=0.4, runtimes=[13]))
        cost_func = WeightedNLLSCostFunc(problems[1])
        jac[1].method = '3-point'
        cost_func.jacobian = jac[0]
        controller = ScipyController(cost_func)
        controller.parameter_set = 0
        controller.minimizer = 'Powell'
        controller.prepare()
        controller.final_params = [0.7+i, 0.8+i]
        controller.iteration_count = 10
        controller.count_type = 'iterations'
        controller.flag = 0
        results[key].append(FittingResult(controller=controller,
                                          accuracy=1.2, runtimes=[0.15]))
        controller.minimizer = 'CG'
        controller.final_params = [0.9+i, 0.01+i]
        controller.flag = 0
        results[key].append(FittingResult(controller=controller,
                                          accuracy=1.3, runtimes=[0.14]))
        cost_func.jacobian = jac[1]
        controller = ScipyController(cost_func)
        controller.parameter_set = 0
        controller.minimizer = 'CG'
        controller.prepare()
        controller.final_params = [0.11+i, 0.21+i]
        controller.iteration_count = 10
        controller.count_type = 'iterations'
        controller.flag = 0
        results[key].append(FittingResult(controller=controller,
                                          accuracy=1.4, runtimes=[0.13]))
    return results


class CheckpointTests(TestCase):
    """
    Tests for the Checkpoint class.
    """

    def test_write_read(self):
        """
        Test that results are the same before and after a write then read.
        """
        with TemporaryDirectory() as temp_dir:
            cp_file = pathlib.Path(temp_dir, "cp.json")
            options = Options(additional_options={
                'checkpoint_filename': cp_file})
            cp = Checkpoint(options)
            # Generate fake results
            expected_res = generate_results()
            expected_uns = {'set1': ['min1', 'min2'],
                            'set2': []}
            expected_fail = {'set1': [],
                             'set2': ['min1']}
            for label, results in expected_res.items():
                for res in results:
                    cp.add_result(res)
                cp.finalise_group(label,
                                  unselected_minimizers=expected_uns[label],
                                  failed_problems=expected_fail[label])
            cp.finalise()

            loaded, unselected, failed = cp.load()

        self.assertDictEqual(unselected, expected_uns)
        self.assertDictEqual(failed, expected_fail)

        for key, expected in expected_res.items():
            for a, e in zip(loaded[key], expected):
                self.assertEqual(a, e,
                                 f'\n\nactual: {pprint.pformat(a.__dict__)}\n'
                                 f'\n\nexpected: {pprint.pformat(e.__dict__)}')

    def test_read_write(self):
        """
        Test that the checkpointing file is the same before and after a read
        then write.
        """
        cp_dir = pathlib.Path(inspect.getfile(test_files)).parent
        cp_file = cp_dir / 'checkpoint.json'

        expected = cp_file.read_text(encoding='utf8').splitlines()

        options = Options(additional_options={
            'checkpoint_filename': str(cp_file)})
        cp = Checkpoint(options)

        res, unselected, failed = cp.load()

        with TemporaryDirectory() as temp_dir:
            cp_file = pathlib.Path(temp_dir, "cp.json")
            options = Options(additional_options={
                'checkpoint_filename': cp_file})
            cp = Checkpoint(options)
            for key, set_results in res.items():
                for r in set_results:
                    cp.add_result(r)
                cp.finalise_group(key,
                                  failed_problems=failed[key],
                                  unselected_minimizers=unselected[key])
            cp.finalise()

            actual = cp_file.read_text(encoding='utf8').splitlines()

        # parameters which are compressed and decompressed
        params = ['fin_y', 'r_x', 'jac_x', 'params', 'ini_y',
                  'x', 'y', 'e', 'sorted_idx', 'ini_params']
        for e, a in zip(expected, actual):
            if any(param in a for param in params):
                continue
            self.assertEqual(a, e)

    def test_no_file(self):
        """
        Test correct exception for missing file.
        """
        options = Options(additional_options={
            'checkpoint_filename': 'not_a_file'})
        cp = Checkpoint(options=options)

        with self.assertRaises(CheckpointError):
            cp.load()


class CompressTests(TestCase):
    """
    Tests for the _compress and _decompress methods.
    """

    def test_compress_decompress(self):
        """
        Test that compress/decompress works as expected.
        """
        expected = [2.0, [1.0, 2.0], np.array([1.0, 2.0, 3.0])]
        for exp in expected:
            try:
                self.assertEqual(exp, _decompress(_compress(exp)),
                                 f"Failed to compress/decompress {exp}")
            except ValueError:
                self.assertTrue((exp == _decompress(_compress(exp))).all(),
                                f"Failed to compress/decompress {exp}")
