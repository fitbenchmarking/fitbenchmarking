"""
Miscellaneous functions and utilities used in fitting benchmarking.
"""

from __future__ import absolute_import, division, print_function

import glob
import os

from fitbenchmarking.utils.exceptions import NoDataError
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()

def get_problem_files(data_dir):
    """
    Gets all the problem definition files from the specified problem
    set directory.

    :param data_dir: directory containing the problems
    :type data_dir: str 

    :return: array containing of paths to the problems
             e.g. In NIST we would have
             [low_difficulty/file1.txt, ..., ...]
    :rtype: list of str
    """

    test_data = glob.glob(data_dir + '/*.*')
    if test_data == []:
        raise NoDataError('"{}" not recognised as a dataset. '
                          'Check that it contains problem files '
                          'and try again.'.format(data_dir))
    problems = [os.path.join(data_dir, data)
                for data in test_data
                if not data.endswith('META.txt')]
    problems.sort()
    for problem in problems:
        LOGGER.debug(problem)

    return problems

def get_local_css_path(options,working_directory):
    """
    Returns the path of the local css folder
    
    :param working_directory: location of current directory
    :type working_directory: string
    
    :return: relative link to local css directory
    :rtype: str
    """
    local_css_dir = os.path.join(options.results_dir,"css")
    css_path = os.path.relpath(local_css_dir,working_directory)
    
    return css_path
