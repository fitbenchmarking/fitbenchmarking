"""
This file implements a singleton class to checkpoint results as they are
generated.
This is also used to read in checkpointed data.
"""

import json
import os
import pickle
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from fitbenchmarking.utils.fitbm_result import FittingResult

if TYPE_CHECKING:
    from typing import Tuple

    from fitbenchmarking.utils.options import Options


class Checkpoint:
    """
    A class to build a checkpoint file.
    Each run can be added to the file as they finish.
    This class must be finalised to create the checkpoint.
    """
    # The single instance of Checkpoint
    instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure new calls to checkpoint use the same state (temporary files)
        """
        if cls.instance is not None:
            cls.instance = object.__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, options: 'Options'):
        """
        Set up a new Checkpoint class
        """
        self.writing: bool = False
        self.finalised: bool = False
        self.options = options

        self.dir: 'TemporaryDirectory[str] | None' = None
        self.problems_file: 'str | None' = None
        self.results_file: 'str | None' = None
        self.problem_names: 'list[str]' = []

    def add_result(self, result: 'FittingResult'):
        """
        Add the result to the checkpoint file.

        :param result: The result to add.
        :type result: FittingResult
        """
        if self.finalised:
            raise RuntimeError(
                "Cannot add to checkpoint - checkpoint has been finalised.")

        if not self.writing:
            self.dir = TemporaryDirectory()
            self.problems_file = os.path.join(
                self.dir.name, 'problems_tmp.txt')
            self.results_file = os.path.join(self.dir.name, 'results_tmp.txt')
            with open(self.results_file, 'w', encoding='utf-8') as f:
                f.write('[\n')
            with open(self.problems_file, 'w', encoding='utf-8') as f:
                f.write('[\n')
            self.writing = True

        self._add_problem(result)

        as_dict = {
            'name': result.name,
            'fin_params': result.params,
            'fin_params_str': result.fin_function_params,
            'accuracy': result.accuracy,
            'runtime': result.runtime,
            'flag': result.error_flag,
            'software': result.software,
            'minimizer': result.minimizer,
            'jacobian': result.jac,
            'hessian': result.hess,
            'software_tag': result.software_tag,
            'minimizer_tag': result.minimizer_tag,
            'jacobian_tag': result.jacobian_tag,
            'hessian_tag': result.hessian_tag,
            'costfun_tag': result.costfun_tag,
            'r': pickle.dumps(result.r_x),
            'J': pickle.dumps(result.jac_x),
            'fin_y': pickle.dumps(result.fin_y),
            'tags': [],
        }

        with open(self.results_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(as_dict, indent=2))

    def _add_problem(self, result: 'FittingResult'):
        """
        Add a problem to the problem file if it hasn't already been added.
        (assumes problems have unique names)

        :param result: The result data to take the problem from
        :type result: FittingResult
        """
        if self.finalised:
            raise RuntimeError(
                "Cannot add to checkpoint - checkpoint has been finalised.")

        if result.name in self.problem_names:
            return

        as_dict = {
            'name': result.name,
            'multivar': result.multivariate,
            'format': result.problem_format,
            'ini_params': result.initial_params,
            'ini_params_str': result.ini_function_params,
            'ini_y': pickle.dumps(result.ini_y),
            'x': pickle.dumps(result.data_x),
            'y': pickle.dumps(result.data_y),
            'e': pickle.dumps(result.data_e),
            'sorted_idx': pickle.dumps(result.sorted_index),
            'problem_tag': result.problem_tag,
        }

        with open(self.problems_file, 'a', encoding='utf-8') as f:
            if self.problem_names:
                f.write(',\n')
            f.write(f'"{result.name}": {json.dumps(as_dict, indent=2)}')

        self.problem_names.append(result.name)

    def finalise(self, label='benchmark', failed_problems=None,
                 unselected_minimizers=None):
        """
        Combine the problem and results file and save somewhere non temporary.
        """
        if self.finalised:
            return

        if failed_problems is None:
            failed_problems = []
        if unselected_minimizers is None:
            unselected_minimizers = {}

        filename = os.path.join(self.options.results_dir,
                                self.options.checkpoint_filename)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'{{"label": {label},\n "problems": {{\n')
            with open(self.problems_file, 'r', encoding='utf-8') as tmp:
                f.write(tmp.read())
            f.write('\n },\n "results":[\n')
            with open(self.results_file, 'r', encoding='utf-8') as tmp:
                f.write(tmp.read())
            f.write(' ],\n')
            f.write(json.dumps({'failed_problems': failed_problems,
                                'unselected_minimizers': unselected_minimizers}))
            f.write('}')

        self.finalised = True
        self.writing = False

    def load(self) -> 'Tuple[str, list[FittingResult], dict, list[str]]':
        """
        Load a list of fitting results from a checkpoint file along with
        failed problems and unselected minimizers.

        :return: Dataset name, Instantiated fitting results,
                 unselected minimisers, failed problems
        :rtype: Tuple[str, list[FittingResult], dict, list[str]]
        """
        for f in [self.options.checkpoint_filename,
                  os.path.join(self.options.results_dir,
                               self.options.checkpoint_filename)]:
            if os.path.isfile(f):
                filename: str = f
                break
        else:
            raise FileNotFoundError('Could not find checkpoint file.')

        with open(filename, 'r', encoding='utf-8') as f:
            tmp = json.load(f)

        label = tmp['label']
        problems = tmp['problems']
        results = tmp['results']
        unselected_minimizers = tmp['unselected_minimizers']
        failed_problems = tmp['failed_problems']

        output: 'list[FittingResult]' = []

        # Unpickle problems so that we use 1 shared object for all results per
        # array
        for p in problems:
            p['ini_y'] = pickle.loads(p['ini_y'])
            p['x'] = pickle.loads(p['x'])
            p['y'] = pickle.loads(p['y'])
            p['e'] = pickle.loads(p['e'])
            p['sorted_idx'] = pickle.loads(p['sorted_idx'])

        for r in results:
            new_result = FittingResult.__new__(FittingResult)

            new_result.params = r['fin_params']
            new_result.fin_function_params = r['fin_params_str']
            new_result.accuracy = r['accuracy']
            new_result.runtime = r['runtime']
            new_result.error_flag = r['flag']
            new_result.software = r['software']
            new_result.minimizer = r['minimizer']
            new_result.jac = r['jacobian']
            new_result.hess = r['hessian']
            new_result.software_tag = r['software_tag']
            new_result.minimizer_tag = r['minimizer_tag']
            new_result.jacobian_tag = r['jacobian_tag']
            new_result.hessian_tag = r['hessian_tag']
            new_result.costfun_tag = r['cost_func']
            new_result.fin_y = pickle.loads(r['fin_y'])
            new_result.r_x = pickle.loads(r['r'])
            new_result.jac_x = pickle.loads(r['J'])
            # new_result.? = r['tags']

            new_result.name = r['name']
            p = problems[new_result.name]
            new_result.multivariate = p['multivar']
            new_result.problem_format = p['format']
            new_result.initial_params = p['ini_params']
            new_result.ini_function_params = p['ini_params_str']
            new_result.data_x = p['x']
            new_result.data_y = p['y']
            new_result.data_e = p['e']
            new_result.sorted_index = p['sorted_idx']
            new_result.ini_y = p['ini_y']
            new_result.problem_tag = p['problem_tag']

            output.append(new_result)

        return label, output, unselected_minimizers, failed_problems
