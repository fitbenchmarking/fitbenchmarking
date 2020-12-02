"""
compare table
"""
import numpy as np
import os
from fitbenchmarking.results_processing.base_table import Table

GRAD_TOL = 1e-1
RES_TOL = 1e-8


class LocalMinTable(Table):
    """

    The local min results shows a ``True`` or ``False`` value together with
    :math:`\\frac{|| J^T r||}{||r||}`. The ``True`` or ``False`` indicates
    whether the software finds a minimum with respect to the following
    criteria:


    - :math:`||r|| \\leq` RES\\_TOL,
    - :math:`|| J^T r|| \\leq` GRAD\\_TOL,
    - :math:`\\frac{|| J^T r||}{||r||} \\leq` GRAD\\_TOL,

    where :math:`J` and :math:`r` are the Jacobian and residual of
    :math:`f(x, p)`, respectively. The tolerances can be found in the results
    object.

    """

    def __init__(self, results, best_results, options, group_dir,
                 pp_locations, table_name):
        """
        Initialise the local minimizer table which shows given the
        conditioners stated in the doc string whether the final parameters
        are a local minimum

        :param results: results nested array of objects
        :type results: list of list of
                       fitbenchmarking.utils.fitbm_result.FittingResult
        :param best_results: best result for each problem
        :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
        :param options: Options used in fitting
        :type options: utils.options.Options
        :param group_dir: path to the directory where group results should be
                          stored
        :type group_dir: str
        :param pp_locations: tuple containing the locations of the
                             performance profiles (acc then runtime)
        :type pp_locations: tuple(str,str)
        :param table_name: Name of the table
        :type table_name: str
        """
        self.name = 'local_min'
        super(LocalMinTable, self).__init__(results, best_results, options,
                                            group_dir, pp_locations,
                                            table_name)

        self.has_pp = True
        self.pp_filenames = \
                        [os.path.relpath(pp,group_dir) for pp in pp_locations]

    def get_values(self, results_dict):
        """
        Gets the main values to be reported in the tables

        :param results_dict: dictionary containing results where the keys
                             are the problem sets and the values are lists
                             of results objects
        :type results_dict: dictionary

        :return: a dictionary containing true or false values whether the
                 return parameters is a local minimizer and a dictionary
                 containing :math:`\\frac{|| J^T r||}{||r||}` values
        :rtype: tuple(dict, dict)
        """
        local_min = {}
        norm_rel = {}
        for key, value in results_dict.items():
            local_min[key] = []
            norm_rel[key] = []
            for i, v in enumerate(value):
                if v.params is None:
                    norm_rel[key].append(np.inf)
                    local_min[key].append("False")
                else:
                    res = v.problem.eval_r(
                        v.params, v.data_x, v.data_y, v.data_e)
                    jac = v.jac.eval(v.params, v.problem.eval_r,
                                     x=v.data_x, y=v.data_y, e=v.data_e)
                    min_test = np.matmul(res, jac)

                    norm_r = np.linalg.norm(res)
                    norm_min_test = np.linalg.norm(min_test)

                    norm_rel[key].append(norm_min_test / norm_r)

                    for r, m, n in zip([norm_r],
                                       [norm_min_test],
                                       [norm_rel[key][i]]):
                        if r <= RES_TOL or m <= GRAD_TOL or n <= GRAD_TOL:
                            local_min[key].append("True")
                        else:
                            local_min[key].append("False")

        return local_min, norm_rel

    def get_colour(self, results):
        """
        Uses the local minimizer dictionary values to set the HTML colour

        :param results: a dictionary containing true or false values whether
                        the return parameters is a local minimizer and a
                        dictionary containing
                        :math:`\\frac{|| J^T r||}{||r||}` values
        :type results: tuple

        :return: dictionary containing error codes from the minimizers
        :rtype: dict
        """
        local_min, _ = results
        colour = {key: [self.html_colours[0]
                        if v == "True" else self.html_colours[-1]
                        for v in value]
                  for key, value in local_min.items()}
        return colour

    def display_str(self, results):
        """
        Function that combines the True and False value from variable local_min
        with the normalised residual

        :param results: a dictionary containing true or false values whether
                        the return parameters is a local minimizer and a
                        dictionary containing
                        :math:`\\frac{|| J^T r||}{||r||}` values
        :type results: tuple

        :return: dictionary containing the string representation of the values
                 in the table.
        :rtype: dict
        """
        local_min, norm_rel = results
        template = self.output_string_type['abs']
        table_output = {}
        for key in local_min.keys():
            table_output[key] = [a + " (" + template.format(r) + ")"
                                 for a, r in zip(local_min[key],
                                                 norm_rel[key])]
        return table_output
