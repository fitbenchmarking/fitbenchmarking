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
    from fitbenchmarking.utils.options import Options


class Checkpoint:
    """
    A class to build a checkpoint file.
    Each run can be added to the file as they finish.
    This class must be finalised to create the checkpoint.
    """
    # The single instance of Checkpoint
    instance = None

    def __new__(cls):
        """
        Ensure new calls to checkpoint use the same state (temporary files)
        """
        if cls.instance is not None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, options: 'Options', filename: str = "checkpoint"):
        """
        Set up a new Checkpoint class
        """
        self.finalised: bool = False
        self.filename = filename
        self.options = options
        self.dir: 'TemporaryDirectory[str]' = TemporaryDirectory()
        self.problems_file = os.path.join(
            self.dir.name, 'problems_tmp.txt')
        self.results_file = os.path.join(self.dir.name, 'results_tmp.txt')
        self.problem_names: 'list[str]' = []
        with open(self.results_file, 'w', encoding='utf-8') as f:
            f.write('[\n')
        with open(self.problems_file, 'w', encoding='utf-8') as f:
            f.write('[\n')

    def add_result(self, result: 'FittingResult'):
        """
        Add the result to the checkpoint file.

        :param result: The result to add.
        :type result: FittingResult
        """
        if self.finalised:
            raise RuntimeError(
                "Cannot add to checkpoint - checkpoint has been finalised.")

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
            'cost_func': result.costfun_tag,
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
        }

        with open(self.problems_file, 'a', encoding='utf-8') as f:
            if self.problem_names:
                f.write(',\n')
            f.write(f'"{result.name}": {json.dumps(as_dict, indent=2)}')

        self.problem_names.append(result.name)

    def finalise(self):
        """
        Combine the problem and results file and save somewhere non temporary.
        """
        if self.finalised:
            return

        filename = os.path.join(self.options.results_dir, self.filename)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('{"problems": {')
            with open(self.problems_file, 'r', encoding='utf-8') as tmp:
                f.write(tmp.read())
            f.write('\n },\n "results":[')
            with open(self.results_file, 'r', encoding='utf-8') as tmp:
                f.write(tmp.read())
            f.write(' ]}')

    @classmethod
    def load(cls, filename: str) -> 'list[FittingResult]':
        """
        Load a list of fitting results from a checkpoint file

        :param filename: The file to load
        :type filename: str
        :return: Instantiated fitting results
        :rtype: list[FittingProblem]
        """
        with open(filename, 'r', encoding='utf-8') as f:
            tmp = json.load(f)

        problems = tmp['problems']
        results = tmp['results']

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

            output.append(new_result)

        return output
