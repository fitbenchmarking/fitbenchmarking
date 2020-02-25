from __future__ import (absolute_import, division, print_function)

import os

import numpy as np

GRAD_TOL = 1e-1
RES_TOL = 1e-8


class FittingResult(object):
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(self, options, problem, initial_params, params,
                 name=None, chi_sq=None, runtime=None,
                 minimizer=None, error_flag=None, dataset_id=None):
        """
        Initialise the Fitting Result

        :param options: Options used in fitting
        :type options: utils.options.Options
        :param problem: The Problem definition for the fit
        :type problem: parsing.fitting_problem.FittingProblem
        :param initial_params: The starting parameters for the fit
        :type initial_params: list of float
        :param params: The parameters found by the fit
        :type params: list of float or list of list of float
        :param name: Name of the result, defaults to None
        :type name: str, optional
        :param chi_sq: The score for the fitting, defaults to None
        :type chi_sq: float or list of float, optional
        :param runtime: The average runtime of the fit, defaults to None
        :type runtime: float or list of float, optional
        :param minimizer: The name of the minimizer used, defaults to None
        :type minimizer: str, optional
        :param error_flag: [description], defaults to None
        :type error_flag: [type], optional
        :param dataset_id: The index of the dataset (Only used for MultiFit),
                           defaults to None
        :type dataset_id: int, optional
        """
        self.options = options
        self.problem = problem
        self.name = name if name is not None else \
            problem.name

        if dataset_id is None:
            self.data_x = problem.data_x
            self.data_y = problem.data_y
            self.data_e = problem.data_e
            self.sorted_index = problem.sorted_index

            self.params = params
            self.chi_sq = chi_sq

        else:
            self.data_x = problem.data_x[dataset_id]
            self.data_y = problem.data_y[dataset_id]
            self.data_e = problem.data_e[dataset_id]
            self.sorted_index = problem.sorted_index[dataset_id]

            self.params = params[dataset_id]
            self.chi_sq = chi_sq[dataset_id]

        self.runtime = runtime
        self._min_chi_sq = None
        self._min_runtime = None

        # Minimizer for a certain problem and its function definition
        self.minimizer = minimizer

        # String interpretaions of the params
        self.ini_function_params = self.problem.get_function_params(
            params=initial_params)
        self.fin_function_params = self.problem.get_function_params(
            params=self.params)

        # Controller error handling
        self.error_flag = error_flag

        self.value = None
        self.norm_value = None

        self.colour = None
        self.colour_runtime = None
        self.colour_acc = None

        # Defines the type of table to be produced
        self._table_type = None
        self.output_string_type = {"abs": '{:.4g}',
                                   "rel": '{:.4g}',
                                   "both": '{0:.4g} ({1:.4g})'}

        # Paths to various output files
        self.support_page_link = ''
        self.start_figure_link = ''
        self.figure_link = ''

        # Links will be displayed relative to this dir
        self.relative_dir = os.path.abspath(os.sep)

        # Error written to support page if plotting failed
        # Default can be overwritten with more information
        self.figure_error = 'Plotting Failed'

        # Print with html tag or not
        self.html_print = False

        # Marker to indicate this is the best fit for the problem
        # Used for the support pages
        self.is_best_fit = False

        # Boolean that checks return true or false depending whether
        # norm(J^T r), norm(J^T r)/norm(r) and/or norm(r) are smaller
        # than a set tolerance
        self._local_min = None

    @property
    def local_min(self):
        """
        Getter for local_min. This indicates if the result is a
        local minimum

        :return: Whether the result is a minimum or not
        :rtype: bool
        """
        if self.params is not None:
            r = self.problem.eval_r(self.params,
                                    x=self.data_x,
                                    y=self.data_y,
                                    e=self.data_e)
            j = self.problem.eval_j(self.params,
                                    x=self.data_x,
                                    y=self.data_y,
                                    e=self.data_e)
            min_test = np.matmul(j.T, r)
            norm_r = np.linalg.norm(r)
            norm_min_test = np.linalg.norm(min_test)
            self.norm_rel = norm_min_test / norm_r
            if norm_r <= RES_TOL or norm_min_test <= GRAD_TOL \
                    or self.norm_rel <= GRAD_TOL:
                self._local_min = "True"
            else:
                self._local_min = "False"
        else:
            self._local_min = "False"
            self.norm_rel = np.inf
        return self._local_min

    @local_min.setter
    def local_min(self, value):
        self._local_min = value

    def __str__(self):
        """
        The string representation of this is used to create the tables.
        This creates a correct representation for the table that has been set.

        :return: Table dependant string representation
        :rtype: str
        """
        if self.table_type is not None:
            output = self.table_output
            if self.html_print:
                link = os.path.relpath(path=self.support_page_link,
                                       start=self.relative_dir)
                if self.error_flag != 0:
                    output += "<sup>{}</sup>".format(self.error_flag)
                output = '<a href="{0}">{1}</a>'.format(link, output)
            elif self.error_flag != 0:
                output += "[{}]".format(self.error_flag)
        else:
            output = 'Fitting problem class: minimizer = {0}'.format(
                self.minimizer)
        return output

    @property
    def table_type(self):
        return self._table_type

    @table_type.setter
    def table_type(self, value):
        """
        Switch table types and setup needed values for creating string output

        :param value: The table to set up for
        :type value: str
        """
        self._table_type = value
        comp_mode = self.options.comparison_mode
        result_template = self.output_string_type[comp_mode]

        if value == "runtime":
            abs_value = [self.runtime]
            rel_value = [self.norm_runtime]
            self.colour = self.colour_runtime
        elif value == "acc":
            abs_value = [self.chi_sq]
            rel_value = [self.norm_acc]
            self.colour = self.colour_acc
        elif value == "compare":
            abs_value = [self.chi_sq, self.runtime]
            rel_value = [self.norm_acc, self.norm_runtime]
            self.colour = [self.colour_acc, self.colour_runtime]

        if value == "local_min":
            output = self.local_min
            self.table_output = output + " (" +\
                self.output_string_type['abs'].format(self.norm_rel) + ")"
            colour = [c[1] for c in self.options.colour_scale]
            self.colour = colour[0] if output == "True" else colour[-1]
        else:
            if comp_mode == "abs":
                self.table_output = \
                    '<br>'.join([result_template.format(v) for v in abs_value])
            elif comp_mode == "rel":
                self.table_output = \
                    '<br>'.join([result_template.format(v) for v in rel_value])
            elif comp_mode == "both":
                self.table_output = \
                    '<br>'.join([result_template.format(v1, v2)
                                 for v1, v2 in zip(abs_value, rel_value)])

    def set_colour_scale(self):
        """
        Utility function set colour rendering for html tables
        """
        colour_scale = self.options.colour_scale
        colour_bounds = [colour[0] for colour in colour_scale]
        # prepending 0 value for colour bound
        colour_bounds = [0] + colour_bounds
        html_colours = [colour[1] for colour in colour_scale]
        self.colour_runtime = colour_scale[-1]
        self.colour_acc = colour_scale[-1]
        for i in range(len(colour_bounds) - 1):
            if colour_bounds[i] < self.norm_runtime <= colour_bounds[i + 1]:
                self.colour_runtime = html_colours[i]
            if colour_bounds[i] < self.norm_acc <= colour_bounds[i + 1]:
                self.colour_acc = html_colours[i]

    @property
    def min_chi_sq(self):
        return self._min_chi_sq

    @min_chi_sq.setter
    def min_chi_sq(self, value):
        """
        Stores the min chi squared and updates the normalised value

        :param value: New value for min_chi_sq
        :type value: float
        """
        self._min_chi_sq = value
        if not self.chi_sq > 0:
            self.chi_sq = np.inf
        self.norm_acc = self.chi_sq / self.min_chi_sq

    @property
    def min_runtime(self):
        return self._min_runtime

    @min_runtime.setter
    def min_runtime(self, value):
        """
        Stores the min runtime and updates the normalised value

        :param value: New value for min_runtime
        :type value: float
        """
        self._min_runtime = value
        self.norm_runtime = self.runtime / self.min_runtime

    @property
    def sanitised_name(self):
        """
        Sanitise the problem name ito one which can be used as a filename.

        :return: sanitised name
        :rtype: str
        """
        return self.name.replace(',', '').replace(' ', '_')

    @sanitised_name.setter
    def sanitised_name(self, value):
        raise RuntimeError('sanitised_name can not be edited')
