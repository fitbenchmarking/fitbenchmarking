"""
Implements the base class for the tables.
"""
from abc import ABCMeta, abstractmethod
import docutils.core
import pandas as pd
import os

# from fitbenchmarking.utils.exceptions import ControllerAttributeError


class Table:
    """
    Base class for the tables.
    """

    __metaclass__ = ABCMeta

    def __init__(self, results, best_results, options, group_dir,
                 pp_locations):
        """
        Initialise the class.
        """
        self.results = results
        self.options = options
        self.best_results = best_results
        self.group_dir = group_dir
        self.pp_locations = pp_locations

        self.results_dict = self.create_results_dict()
        colour_scale = self.options.colour_scale

        self.colour_bounds = [colour[0] for colour in colour_scale]
        self.html_colours = [colour[1] for colour in colour_scale]

        self.output_string_type = {"abs": '{:.4g}',
                                   "rel": '{:.4g}',
                                   "both": '{0:.4g} ({1:.4g})'}
        self.has_pp = False
        self.pp_location = ''
        self.rst_description = \
            {'abs': 'Absolute values are displayed in the table.',
             'rel': 'Relative values are displayed in the table.',
             'both': 'Absolute and relative values are displayed in '
             'the table in the format ``abs (rel)``'}
        self._table_title = None

    def create_results_dict(self):
        """
        Generates a dictionary used to create HTML and txt tables.
        """
        results_dict = {}
        name_count = {}
        for prob_results in self.results:
            name = prob_results[0].problem.name
            name_count[name] = 1 + name_count.get(name, 0)
            count = name_count[name]

            prob_name = name + ' ' + str(count)
            results_dict[prob_name] = prob_results
        return results_dict

    @abstractmethod
    def get_values(self):
        """
        This function to return a four dictionaries:
            1. absolute values
            2. relative values
            3. HTML colours
            4. links to supporting page
        where the key of the dictionary is the problem data name and the
        values is a list.
        """
        raise NotImplementedError

    def display_str(self, abs_results, rel_results):
        comp_mode = self.options.comparison_mode
        result_template = self.output_string_type[self.options.comparison_mode]
        table_output = {}
        for key in abs_results.keys():
            if comp_mode == "abs":
                table_output[key] = [result_template.format(v)
                                     for v in abs_results[key]]
            elif comp_mode == "rel":
                table_output[key] = [result_template.format(v)
                                     for v in rel_results[key]]
            elif comp_mode == "both":
                table_output[key] = [result_template.format(v1, v2)
                                     for v1, v2 in zip(abs_results[key],
                                                       rel_results[key])]
        return table_output

    def create_data_frame(self):
        abs_results, rel_results, self.colour, self.links = self.get_values()
        str_results = self.display_str(abs_results, rel_results)
        self.tbl = pd.DataFrame.from_dict(str_results, orient='index')
        minimizers_list = [self.options.minimizers[soft]
                           for soft in self.options.software]
        minimizers = [val for sublist in minimizers_list for val in sublist]
        self.tbl.columns = minimizers

    def to_html(self):
        self.tbl.apply(self.enable_link, axis=1)
        index = []
        for b, i in zip(self.best_results, self.tbl.index):
            rel_path = os.path.relpath(path=b.support_page_link,
                                       start=self.group_dir)
            index.append('<a href="{0}">{1}</a>'.format(rel_path, i))
        self.tbl.index = index
        table_style = self.tbl.style.apply(self.colour_highlight, axis=1)

        return table_style.render()

    def to_txt(self):
        return self.tbl.to_string()

    def enable_link(self, value):
        name = value.name
        support_page_link = self.links[name]
        i = 0
        for l, v in zip(support_page_link, value.array):
            tmp_link = os.path.relpath(path=l,
                                       start=self.group_dir)
            value.array[i] = '<a href="{0}">{1}</a>'.format(tmp_link, v)
            i += 1
        return value

    def colour_highlight(self, value):
        color_template = 'background-color: {0}'
        name = value.name.split('>')[1].split('<')[0]
        colour_style = self.colour[name]
        output_colour = []
        for c in colour_style:
            output_colour.append(color_template.format(c))
        return output_colour

    def get_description(self, html_description):
        self.rst_description[self.name] = self.__doc__
        for name in [self.name, self.options.comparison_mode]:
            descrip = self.rst_description[name]
            descrip = descrip.replace(':ref:', '')
            description_page = docutils.core.publish_parts(
                descrip, writer_name='html')
            html_description[name] = description_page['body']
            html_description[name] = \
                html_description[name].replace('<blockquote>\n', '')
        return html_description

    @property
    def table_title(self):
        if self._table_title is None:
            self._table_title = "FitBenchmarking: {0} table".format(self.name)
        return self._table_title

    @table_title.setter
    def table_title(self, value):
        self._table_title = value
