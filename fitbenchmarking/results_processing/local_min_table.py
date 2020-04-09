"""
compare table
"""
import numpy as np
from fitbenchmarking.results_processing.base_table import Table

GRAD_TOL = 1e-1
RES_TOL = 1e-8


class LocalMinTable(Table):
    """

    The local min results shows a ``True`` or ``False`` value together with :math:`\\frac{|| J^T r||}{||r||}`. The ``True`` or ``False`` indicates whether the software finds a minimum with respect to the following criteria:


    - :math:`||r|| \\leq \\mbox{RES\\_TOL}`,
    - :math:`|| J^T r|| \\leq \\mbox{GRAD\\_TOL}`,
    - :math:`\\frac{|| J^T r||}{||r||} \\leq \\mbox{GRAD\\_TOL}`,

    where :math:`J` and :math:`r` are the Jacobian and residual of :math:`f(x, p)`, respectively. The tolerances can be found in the results object.

    """

    def __init__(self, results, best_results, options, group_dir,
                 pp_locations):
        """
        Initialise runtime table class.

        :param results: dictionary containing results, i.e.,
                           {'prob1': [result1, result2, ...],
                            'prob2': [result1, result2, ...], ...}
        :type results: dict
        :param options: The options used in the fitting problem and plotting
        :type options: fitbenchmarking.utils.options.Options
        """
        self.name = 'local_min'
        super(LocalMinTable, self).__init__(
            results, best_results, options, group_dir, pp_locations)

        self.has_pp = True
        self.pp_filenames = pp_locations

    def get_values(self):
        colour = {}
        local_min = {}
        norm_rel = {}
        links = {}
        for key, value in self.results_dict.items():
            res = [v.problem.eval_r(v.params) for v in value]
            jac = [v.problem.eval_j(v.params).T for v in value]
            min_test = [np.matmul(j, r) for j, r in zip(jac, res)]

            norm_r = [np.linalg.norm(r) for r in res]
            norm_min_test = [np.linalg.norm(m) for m in min_test]

            norm_rel[key] = [m / r for m, r in zip(norm_min_test, norm_r)]
            local_min[key] = []
            colour[key] = []
            for r, m, n in zip(norm_r, norm_min_test, norm_rel[key]):
                if r <= RES_TOL or m <= GRAD_TOL or n <= GRAD_TOL:
                    local_min[key].append("True")
                    colour[key].append(self.html_colours[0])
                else:
                    local_min[key].append("False")
                    colour[key].append(self.html_colours[-1])

            links[key] = [v.support_page_link for v in value]

        return local_min, norm_rel, colour, links

    def display_str(self, abs_results, rel_results):
        template = self.output_string_type['abs']
        table_output = {}
        for key in abs_results.keys():
            table_output[key] = [a + " (" + template.format(r) + ")"
                                 for a, r in zip(abs_results[key],
                                                 rel_results[key])]
        return table_output
