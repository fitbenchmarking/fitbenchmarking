from __future__ import (absolute_import, division, print_function)


class UserInput(object):
    """
    Structure to hold all the user inputted data.
    """

    def __init__(self, software, minimizers, group_name, results_dir, use_errors):
        # The software that is benchmarked e.g. scipy, mantid etc.
        self.software = software
        # The minimizers inside that certain software that are
        # being benchmarked
        self.minimizers = minimizers
        # The name of the problem group to be analysed e.g. neutron
        self.group_name = group_name
        # Director path in which to put the results for each problem group
        self.group_results_dir = results_dir
        # Whether or not to consider error bars in the fitting process
        self.use_errors = use_errors
