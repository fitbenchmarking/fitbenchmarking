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
    problems = [os.path.join(data_dir, data)
                for data in test_data
                if not data.endswith('META.txt')]
    problems.sort()
    for problem in problems:
        logger.info(problem)

    return problems


def combine_files(output_file, *files):
    """
    Creates a combined file, used in joining HTML style sheet to HTML templates

    :param output_file : path to output file
    :type output_file : str
    :param files : paths to input files which will be joined together
    :type files : tuple(str, str, ...)
    """

    if not isinstance(output_file, str):
        raise TypeError("Path to output file is required to be a string.")

    if len(files) < 1:
        raise IndexError("Need to provide multiple input files to join, "
                         "currently none are given.")
    for filesnames in files:
        if not isinstance(filesnames, str):
            raise TypeError("Path to file is required to be a string")
        elif not os.path.isfile(filesnames):
            raise RuntimeError("File does not exist")

    with open(output_file, 'wb') as newf:
        for filename in files:
            with open(filename, 'rb') as hf:
                newf.write(hf.read())
