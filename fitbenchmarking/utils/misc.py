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

def get_css(options,working_directory):
    """
    Returns the path of the local css folder
    
    :param working_directory: location of current directory
    :type working_directory: string
    
    :return: A dictionary containing relative links to the local css directory
    :rtype: dict of strings
    """
    local_css_dir = os.path.join(options.results_dir,"css")
    css_path = os.path.relpath(local_css_dir,working_directory)
    css_dict = {
        'main'   : os.path.join(css_path,'main_style.css'),
        'table'  : os.path.join(css_path,'table_style.css'),
        'custom' : os.path.join(css_path,'custom_style.css')
    }
    
    return css_dict

def get_js(options,working_directory):
    """
    Returns the path of the local js folder
    
    :param working_directory: location of current directory
    :type working_directory: string
    
    :return: A dictionary containing relative links to the local js directory
    :rtype: dict of strings
    """
    local_js_dir = os.path.join(options.results_dir,"js")
    js_path = os.path.relpath(local_js_dir,working_directory)
    js_dict = {
        'mathjax'   : os.path.join(js_path,'tex-mml-chtml.js'),
    }
    
    return js_dict
