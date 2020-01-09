"""
Utility functions for creating/deleting directories.
"""

import os
import shutil


def results(results_dir):
    """
    Creates the results folder in the working directory.

    :param results_dir: path to the results directory, results dir name
    :type results_dir: str

    :returns: proper path to the results directory
    :rtype: str
    """

    if not isinstance(results_dir, str):
        raise TypeError("results_dir must be a string!")

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    return results_dir


def group_results(results_dir, group_name):
    """
    Creates the results directory for a specific group.
    e.g. fitbenchmarking/results/Neutron/

    @param results_dir :: directory that holds all the results
    @param group_name :: string containing the name of the problem group

    @returns :: path to folder group specific results dir
    """

    if isinstance(group_name, str):
        group_dir = os.path.join(results_dir, group_name)
    else:
        raise TypeError('Type of variable group_name is required '
                        'to be a string, type(group_name) '
                        '= {}'.format(type(group_name)))
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)
    return group_dir


def support_pages(group_results_dir):
    """
    Creates the support_pages directory in the group results directory.

    @param group_results_dir :: path to the group results directory

    @returns :: path to the figures directory
    """
    support_pages_dir = \
        os.path.join(group_results_dir, "support_pages")
    if not os.path.exists(support_pages_dir):
        os.makedirs(support_pages_dir)

    return support_pages_dir


def figures(support_pages_dir):
    """
    Creates the figures directory inside the support_pages directory.

    @param group_results_dir :: path to the group results directory

    @returns :: path to the figures directory
    """
    figures_dir = os.path.join(support_pages_dir, "figures")
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)

    return figures_dir


def del_contents_of_dir(directory):
    """
    Delete contents of a directory, including other directories.

    @param directory :: the target directory
    """

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
