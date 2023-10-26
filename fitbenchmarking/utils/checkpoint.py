"""
This file implements a checkpointclass to save results as they are
generated.
This is also used to read in checkpointed data.
"""

import json
import os
import pickle
from base64 import a85decode, a85encode
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from fitbenchmarking.utils.exceptions import CheckpointError
from fitbenchmarking.utils.fitbm_result import FittingResult

if TYPE_CHECKING:
    from fitbenchmarking.utils.options import Options


class Checkpoint:
    """
    A class to build a checkpoint file.
    Each run can be added to the file as they finish.
    This class must be finalised to create the checkpoint.
    """

    def __init__(self, options: 'Options'):
        """
        Set up a new Checkpoint class
        """
        # Labels for all finalised groups
        self.finalised_labels: 'list[str]' = []
        # Flag for if the file has been locked post writing
        self.finalised: bool = False

        # True if next result is the first in a group
        self.first_result = True
        # Problems that have been written already in the current group
        self.problem_names: 'list[str]' = []

        # Options to define behavior
        self.options = options

        # File paths for temp files
        self.dir: 'TemporaryDirectory[str] | None' = None
        self.problems_file: 'str | None' = None
        self.results_file: 'str | None' = None

        # The persistent checkpoint file
        self.cp_file: str = os.path.join(self.options.results_dir,
                                         self.options.checkpoint_filename)

    def add_result(self, result: 'FittingResult'):
        """
        Add the result to the checkpoint file.

        :param result: The result to add.
        :type result: FittingResult
        """
        if self.finalised:
            raise RuntimeError(
                "Cannot add to checkpoint - checkpoint has been finalised.")

        if self.first_result:
            if not self.finalised_labels:
                if not os.path.exists(self.options.results_dir):
                    os.makedirs(self.options.results_dir)
                with open(self.cp_file, 'w', encoding='utf-8') as f:
                    f.write('{\n')

            # pylint: disable=consider-using-with
            self.dir = TemporaryDirectory()
            self.problems_file = os.path.join(
                self.dir.name, 'problems_tmp.txt')
            self.results_file = os.path.join(self.dir.name, 'results_tmp.txt')
            with open(self.results_file, 'w', encoding='utf-8') as f:
                f.write('[\n')
            with open(self.problems_file, 'w', encoding='utf-8') as f:
                f.write('{\n')

        self._add_problem(result)

        as_dict = {
            'name': result.name,
            'fin_params': _compress(result.params),
            'fin_params_str': result.fin_function_params,
            'accuracy': result.accuracy,
            'runtime': result.runtime,
            'runtimes': result.runtimes,
            'emissions': result.emissions,
            'flag': result.error_flag,
            'params_pdfs': result.params_pdfs,
            'software': result.software,
            'minimizer': result.minimizer,
            'jacobian': result.jac,
            'hessian': result.hess,
            'software_tag': result.software_tag,
            'minimizer_tag': result.minimizer_tag,
            'jacobian_tag': result.jacobian_tag,
            'hessian_tag': result.hessian_tag,
            'costfun_tag': result.costfun_tag,
            'r': _compress(result.r_x),
            'J': _compress(result.jac_x),
            'fin_y': _compress(result.fin_y),
            'tags': result.algorithm_type,
        }

        with open(self.results_file, 'a', encoding='utf-8') as f:
            if not self.first_result:
                f.write(',\n')
            f.write('      {\n')
            f.write(json.dumps(as_dict, indent=8)[2:-2])
            f.write('\n      }')

        self.first_result = False

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
            'ini_params': _compress(result.initial_params),
            'ini_params_str': result.ini_function_params,
            'ini_y': _compress(result.ini_y),
            'x': _compress(result.data_x),
            'y': _compress(result.data_y),
            'e': _compress(result.data_e),
            'sorted_idx': _compress(result.sorted_index),
            'problem_tag': result.problem_tag,
            'problem_desc': result.problem_desc,
            'equation': result.equation,
            'plot_scale': result.plot_scale,
        }

        with open(self.problems_file, 'a', encoding='utf-8') as f:
            if self.problem_names:
                f.write(',\n')
            f.write(f'      "{result.name}": {{\n'
                    f'{json.dumps(as_dict, indent=8)[2:-2]}\n      }}')

        self.problem_names.append(result.name)

    def finalise_group(self, label='benchmark', failed_problems=None,
                       unselected_minimizers=None):
        """
        Combine the problem and results file into the main checkpoint file.
        """
        if label in self.finalised_labels or self.first_result:
            return

        if failed_problems is None:
            failed_problems = []
        if unselected_minimizers is None:
            unselected_minimizers = {}

        with open(self.cp_file, 'a', encoding='utf-8') as f:
            if self.finalised_labels:
                f.write(',\n')
            f.write(f'  "{label}": {{\n    "problems": ')
            if self.problems_file is not None:
                with open(self.problems_file, 'r', encoding='utf-8') as tmp:
                    f.write(tmp.read())
            else:
                f.write('    {')
            f.write('\n    },\n    "results": ')
            if self.results_file is not None:
                with open(self.results_file, 'r', encoding='utf-8') as tmp:
                    f.write(tmp.read())
            else:
                f.write('    [')
            f.write('\n    ],\n    ')
            f.write(json.dumps(
                {'failed_problems': failed_problems,
                 'unselected_minimizers': unselected_minimizers},
                indent=4)[6:-1])
            f.write('  }')

        self.finalised_labels.append(label)
        self.first_result = True
        self.problem_names = []

    def finalise(self):
        """
        Add the trailing bracket to validate the json.
        """
        # Has the file already been finalised?
        if self.finalised:
            return

        # Has the file been started?
        if not self.finalised_labels and self.first_result:
            return

        # Has the last group been finalised?
        if not self.first_result:
            self.finalise_group(label='incomplete_group')

        with open(self.cp_file, 'a', encoding='utf-8') as f:
            f.write('\n}')
        self.finalised = True

    def load(self):
        """
        Load fitting results from a checkpoint file along with
        failed problems and unselected minimizers.

        :return: Instantiated fitting results,
                 unselected minimisers, failed problems
        :rtype: Tuple[ dict[str, list[FittingResult]],
                       dict,
                       dict[str, list[str]]]
        """
        output: 'dict[str,list[FittingResult]]' = {}
        unselected_minimizers: 'dict[str, list[str]]' = {}
        failed_problems: 'dict[str, list[str]]' = {}

        for f in [self.options.checkpoint_filename,
                  os.path.join(self.options.results_dir,
                               self.options.checkpoint_filename)]:
            if os.path.isfile(f):
                filename: str = f
                break
        else:
            raise CheckpointError('Could not find checkpoint file.')

        with open(filename, 'r', encoding='utf-8') as f:
            tmp = json.load(f)

        for label, group in tmp.items():
            output[label] = []

            problems = group['problems']
            results = group['results']
            unselected_minimizers[label] = group['unselected_minimizers']
            failed_problems[label] = group['failed_problems']

            # Unpickle problems so that we use 1 shared object for all results
            # per array
            for p in problems.values():
                p['ini_y'] = _decompress(p['ini_y'])
                p['x'] = _decompress(p['x'])
                p['y'] = _decompress(p['y'])
                p['e'] = _decompress(p['e'])
                p['sorted_idx'] = _decompress(p['sorted_idx'])
                p['ini_params'] = _decompress(p['ini_params'])

            for r in results:
                new_result = FittingResult.__new__(FittingResult)
                new_result.init_blank()

                new_result.params = _decompress(r['fin_params'])
                new_result.fin_function_params = r['fin_params_str']
                new_result.accuracy = r['accuracy']
                new_result.runtime = r['runtime']
                new_result.runtimes = r['runtimes']
                new_result.emissions = r['emissions']
                new_result.error_flag = r['flag']
                new_result.params_pdfs = r['params_pdfs']
                new_result.software = r['software']
                new_result.minimizer = r['minimizer']
                new_result.jac = r['jacobian']
                new_result.hess = r['hessian']
                new_result.software_tag = r['software_tag']
                new_result.minimizer_tag = r['minimizer_tag']
                new_result.jacobian_tag = r['jacobian_tag']
                new_result.hessian_tag = r['hessian_tag']
                new_result.costfun_tag = r['costfun_tag']
                new_result.fin_y = _decompress(r['fin_y'])
                new_result.r_x = _decompress(r['r'])
                new_result.jac_x = _decompress(r['J'])
                new_result.algorithm_type = r['tags']

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
                new_result.problem_desc = p['problem_desc']
                new_result.equation = p['equation']
                new_result.plot_scale = p['plot_scale']

                output[label].append(new_result)

        return output, unselected_minimizers, failed_problems


def _compress(value):
    """
    Compress a python object into an ascii string

    :param value: The value to compress
    :type value: List
    :return: The compressed string ready for writing to json file
    :rtype: str
    """
    return a85encode(pickle.dumps(value)).decode('ascii')


def _decompress(value: str):
    """
    Decompress a compressed string value

    :param value: The string to decompress
    :type value: str
    :return: The decompressed value
    :rtype: List
    """
    return pickle.loads(a85decode(value.encode('ascii')))
