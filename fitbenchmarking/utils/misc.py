"""
Miscellaneous functions and utilities used in fitting benchmarking.
"""

from __future__ import absolute_import, division, print_function

import glob
import os

from fitbenchmarking.utils.logging_setup import logger


def get_problem_files(data_dir):
    """
    Gets all the problem definition files from the specified problem
    set directory.

    @param data_dir :: directory containing the problems

    @returns :: array containing of paths to the problems
                e.g. In NIST we would have
                [low_difficulty/file1.txt, ..., ...]
    """

    test_data = glob.glob(data_dir + '/*.*')
    if test_data == []:
        raise ValueError('"{}" not recognised as a dataset. '
                         'Check that it contains problem files '
                         'and try again.'.format(data_dir))
    problems = [os.path.join(data_dir, data) for data in test_data]
    problems.sort()
    for problem in problems:
        logger.info(problem)

    return problems
