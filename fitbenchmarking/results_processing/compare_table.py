"""
compare table
"""
import numpy as np
from fitbenchmarking.results_processing.base_table import Table


class CompareTable(Table):
    """

    The combined results show the accuracy in the first line of the cell and the runtime on the second line of the cell.

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
        self.name = 'compare'
        super(CompareTable, self).__init__(
            results, best_results, options, group_dir, pp_locations)

        self.has_pp = True
        self.pp_filenames = pp_locations

    def get_values(self):
        colour = {}
        abs_value = {}
        rel_value = {}
        links = {}
        for key, value in self.results_dict.items():
            acc_abs_value = [v.chi_sq for v in value]
            acc_min_value = np.min(acc_abs_value)
            acc_rel_value = [v.chi_sq / acc_min_value for v in value]
            acc_colour_index = np.searchsorted(self.colour_bounds,
                                               acc_rel_value)
            acc_colour = [self.html_colours[i] for i in acc_colour_index]

            runtime_abs_value = [v.runtime for v in value]
            runtime_min_value = np.min(runtime_abs_value)
            runtime_rel_value = [v.runtime / runtime_min_value for v in value]
            runtime_colour_index = np.searchsorted(self.colour_bounds,
                                                   runtime_rel_value)
            runtime_colour = [self.html_colours[i]
                              for i in runtime_colour_index]

            abs_value[key] = [acc_abs_value, runtime_abs_value]
            rel_value[key] = [acc_rel_value, runtime_rel_value]
            colour[key] = [acc_colour, runtime_colour]
            links[key] = [v.support_page_link for v in value]

        return abs_value, rel_value, colour, links

    def display_str(self, abs_results, rel_results):
        comp_mode = self.options.comparison_mode
        result_template = self.output_string_type[self.options.comparison_mode]
        table_output = {}
        for key in abs_results.keys():
            acc_abs, runtime_abs = abs_results[key]
            acc_rel, runtime_rel = rel_results[key]
            if comp_mode == "abs":
                table_output[key] = \
                    [result_template.format(acc) + '<br>'
                     + result_template.format(runtime)
                     for acc, runtime in zip(acc_abs, runtime_abs)]
            elif comp_mode == "rel":
                table_output[key] = \
                    [result_template.format(acc) + '<br>'
                     + result_template.format(runtime)
                     for acc, runtime in zip(acc_rel, runtime_rel)]
            elif comp_mode == "both":
                table_output[key] = \
                    [result_template.format(acc_a, acc_r) + '<br>'
                     + result_template.format(runtime_a, runtime_r)
                     for acc_a, acc_r, runtime_a, runtime_r in
                     zip(acc_abs, acc_rel, runtime_abs, runtime_rel)]
        return table_output

    def colour_highlight(self, value):
        color_template = 'background-image: linear-gradient({0},{0},{1},{1})'
        name = value.name.split('>')[1].split('<')[0]
        output_colour = []
        acc_colour, runtime_colour = self.colour[name]
        for acc, runtime in zip(acc_colour, runtime_colour):
            output_colour.append(color_template.format(acc, runtime))
        return output_colour
