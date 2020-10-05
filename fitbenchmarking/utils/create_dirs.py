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

    :return: proper path to the results directory
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

    :param results_dir: path to directory that holds all the results
    :type results_dir: str
    :param group_name: name of the problem group
    :type group_name: str

    :return: path to folder group specific results dir
    :rtype: str
    """

    if isinstance(group_name, str):
        group_dir = os.path.join(results_dir, group_name)
    else:
        raise TypeError('Type of variable group_name is required '
                        'to be a string, type(group_name) '
                        '= {}'.format(type(group_name)))
    if os.path.exists(group_dir):
        shutil.rmtree(group_dir)
    os.makedirs(group_dir)
    return group_dir


def support_pages(group_results_dir):
    """
    Creates the support_pages directory in the group results directory.

    :param group_results_dir: path to the group results directory
    :type group_results_dir: str

    :return: path to the figures directory
    :rtype: str
    """
    support_pages_dir = os.path.join(group_results_dir, "support_pages")
    if not os.path.exists(support_pages_dir):
        os.makedirs(support_pages_dir)

    return support_pages_dir


def figures(support_pages_dir):
    """
    Creates the figures directory inside the support_pages directory.

    :param support_pages_dir: path to the support pages directory
    :type support_pages_dir: str

    :return: path to the figures directory
    :rtype: str
    """
    figures_dir = os.path.join(support_pages_dir, "figures")
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)

    return figures_dir

def css(results_dir):
    """
    Creates a local css directory inside the results directory.

    :param support_pages_dir: path to the results directory
    :type support_pages_dir: str

    :return: path to the local css directory
    :rtype: str
    """
    local_css_dir = os.path.join(results_dir, "css")
    if not os.path.exists(local_css_dir):
        os.makedirs(local_css_dir)

    return local_css_dir


def del_contents_of_dir(directory):
    """
    Delete contents of a directory, including other directories.

    :param directory: the target directory
    :type directory: str
    """

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
