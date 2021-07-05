"""
Implements the base class for the tables.
"""
from abc import ABCMeta, abstractmethod
import os
import docutils.core
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from fitbenchmarking.utils.misc import get_js

FORMAT_DESCRIPTION = \
    {'abs': 'Absolute values are displayed in the table.',
     'rel': 'Relative values are displayed in the table.',
     'both': 'Absolute and relative values are displayed in '
             'the table in the format ``abs (rel)``'}

# The use of Pandas maps means that certain functions do not require use
# of self
# pylint: disable=no-self-use


class Table:
    """
    Base class for the FitBenchmarking HTML and text output tables.
    """
    __metaclass__ = ABCMeta

    def __init__(self, results, best_results, options, group_dir,
                 pp_locations, table_name):
        """
        Initialise the class.

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
        self.results = results
        self.options = options
        self.best_results = best_results
        self.group_dir = group_dir
        self.pp_locations = pp_locations
        self.table_name = table_name
        self.name = None

        self.output_string_type = {"abs": '{:.4g}',
                                   "rel": '{:.4g}',
                                   "both": '{0:.4g} ({1:.4g})'}
        self.has_pp = False
        self.pp_location = ''
        self._table_title = None
        self._file_path = None

    def create_results_dict(self):
        """
        Generates a dictionary used to create HTML and txt tables.

        :return: dictionary containing results where the keys
                 are the problem sets and the values are lists
                 of results objects
        :rtype: dictionary
        """
        results_dict = {}
        for prob_results in self.results:
            name = prob_results[0].name
            results_dict[name] = prob_results
        return results_dict

    @abstractmethod
    def get_values(self, results_dict):
        """
        Gets the main values to be reported in the tables

        :param results_dict: dictionary containing results where the keys
                             are the problem sets and the values are lists
                             of results objects
        :type results_dict: dictionary

        :return: tuple of dictionaries which contain the main values in the
                 tables
        :rtype: tuple
        """
        raise NotImplementedError

    def display_str(self, results):
        """
        Function which converts the results from
        :meth:`~fitbenchmarking.results_processing.base_table.Table.get_values()`
        into a string respresentation to be used in the tables.
        Base class implementation takes
        the absolute and relative values and uses ``self.output_string_type``
        as a template for the string format. This can be overwritten to
        adequately display the results.

        :param results: tuple containing absolute and relative values
        :type results: tuple

        :return: dictionary containing the string representation of the values
                 in the table.
        :rtype: dict
        """
        abs_results, rel_results = results
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

    def get_colour(self, results):
        """
        Converts the result from
        :meth:`~fitbenchmarking.results_processing.base_table.Table.get_values()`
        into the HTML colours used in the tables. The base class
        implementation, for example, uses the relative results and
        ``colour_map``, ``colour_ulim`` and ``cmap_range`` within
        :class:`~fitbenchmarking.utils.options.Options`.
        :param results: tuple containing absolute and relative values
        :type results: tuple
        :return: dictionary containing HTML colours for the table
        :rtype: dict
        """
        cmap_name = self.options.colour_map
        cmap = plt.get_cmap(cmap_name)
        cmap_ulim = self.options.colour_ulim
        cmap_range = self.options.cmap_range
        log_ulim = np.log10(cmap_ulim)  # colour map used with log spacing
        _, rel_value = results
        colour = {}
        for key, value in rel_value.items():
            if not all(isinstance(elem, list) for elem in value):
                hex_strs = self._vals_to_colour(value, cmap,
                                                cmap_range, log_ulim)
                colour[key] = hex_strs
            else:
                colour[key] = []
                for v in value:
                    hex_strs = self._vals_to_colour(v, cmap,
                                                    cmap_range, log_ulim)
                    colour[key].append(hex_strs)
        return colour

    @abstractmethod
    def get_cbar(self, fig_dir):
        """
        Plots colourbar figure to figure directory and returns the
        path to the figure.

        :param fig_dir: figure directory
        :type fig_dir: str

        :return fig_path: path to colourbar figure
        :rtype fig_path: str
        """
        raise NotImplementedError()

    def get_links(self, results_dict):
        """
        Pulls out links to the individual support pages from the results
        object

        :param results: tuple containing absolute and relative values
        :type results: tuple

        :return: dictionary containing links to the support pages
        :rtype: dict
        """
        links = {key: [v.support_page_link for v in value]
                 for key, value in results_dict.items()}
        return links

    def get_error(self, results_dict):
        """
        Pulls out error code from the results object

        :param results: tuple containing absolute and relative values
        :type results: tuple

        :return: dictionary containing error codes from the minimizers
        :rtype: dict
        """
        error = {key: [v.error_flag for v in value]
                 for key, value in results_dict.items()}
        return error

    def create_pandas_data_frame(self, str_results):
        """
        Converts dictionary of results into a pandas data frame

        :param str_results: dictionary containing the string representation of
                            the values in the table.
        :type str_results: dict

        :return: pandas data frame with from results
        :rtype: Pandas DataFrame
        """
        table = pd.DataFrame.from_dict(str_results, orient='index')
        minimizers_list = [(s, m) for s in self.options.software
                           for m in self.options.minimizers[s]]
        columns = pd.MultiIndex.from_tuples(minimizers_list)
        table.columns = columns
        return table

    def to_html(self, table, colour, links, error):
        """
        Takes Pandas data frame and converts it into the HTML table output

        :param table: pandas data frame with from results
        :type table: Pandas DataFrame
        :param colour: dictionary containing error codes from the minimizers
        :type colour: dict
        :param links: dictionary containing links to the support pages
        :type links: dict
        :param error: dictionary containing error codes from the minimizers
        :type error: dict

        :return: HTLM table output
        :rtype: str
        """
        link_template = '<a href="https://fitbenchmarking.readthedocs.io/'\
                        'en/latest/users/options/minimizer_option.html#'\
                        '{0}-{0}" target="_blank">{0}</a>'
        minimizer_template = '<span title="{0}">{1}</span>'
        table.apply(lambda x: self.enable_error(x, error, "<sup>{}</sup>"),
                    axis=1, result_type='expand')
        table.apply(lambda x: self.enable_link(x, links), axis=1,
                    result_type='expand')

        minimizers_list = [(link_template.format(s.replace("_", "-")),
                           minimizer_template.format(
                               self.options.minimizer_alg_type[m], m))
                           for s in self.options.software
                           for m in self.options.minimizers[s]]
        columns = pd.MultiIndex.from_tuples(minimizers_list)
        table.columns = columns

        index = []
        for b, i in zip(self.best_results, table.index):
            rel_path = os.path.relpath(path=b.support_page_link,
                                       start=self.group_dir)
            index.append('<a href="{0}">{1}</a>'.format(rel_path, i))
        table.index = index
        table_style = table.style.apply(
            lambda x: self.colour_highlight(x, colour), axis=1)

        return table_style.render()

    def to_txt(self, table, error):
        """
        Takes Pandas data frame and converts it into the plain text table
        output

        :param table: pandas data frame with from results
        :type table: Pandas DataFrame
        :param error: dictionary containing error codes from the minimizers
        :type error: dict

        :return: plain text table output
        :rtype: str
        """
        table.apply(lambda x: self.enable_error(x, error, "[{}]"),
                    axis=1, result_type='expand')
        return table.to_string()

    def enable_link(self, value, links):
        """
        Enable HTML links in values

        :param value: Row data from the pandas array
        :type value: pandas.core.series.Series
        :param links: dictionary containing links to the support pages
        :type links: dict

        :return: Row data from the pandas array with links enabled
        :rtype: pandas.core.series.Series
        """
        name = value.name
        support_page_link = links[name]
        i = 0
        for page_path, v in zip(support_page_link, value.array):
            tmp_link = os.path.relpath(path=page_path,
                                       start=self.group_dir)
            value.array[i] = '<a href="{0}">{1}</a>'.format(tmp_link, v)
            i += 1
        return value

    def enable_error(self, value, error, template):
        """
        Enable error codes in table

        :param value: Row data from the pandas array
        :type value: pandas.core.series.Series
        :param error: dictionary containing error codes from the minimizers
        :type error: dict

        :return: Row data from the pandas array with error codes enabled
        :rtype: pandas.core.series.Series
        """
        name = value.name
        error_code = [template.format(e) if e != 0 else ""
                      for e in error[name]]
        i = 0
        for v, e in zip(value, error_code):
            value.array[i] = v + e
            i += 1
        return value

    def colour_highlight(self, value, colour):
        """
        Takes the HTML colour values from
        :meth:`~fitbenchmarking.results_processing.base_table.Table.get_colour`
        and maps it over the HTML table using the Pandas style mapper.

        :param value: Row data from the pandas array
        :type value: pandas.core.series.Series
        :param colour: dictionary containing error codes from the minimizers
        :type colour: dict

        :return: list of HTML colours
        :rtype: list
        """
        color_template = 'background-color: {0}'
        name = value.name.split('"')[2].replace("</a>", "")[1:]
        colour_style = colour[name]
        output_colour = []
        for c in colour_style:
            output_colour.append(color_template.format(c))
        return output_colour

    def get_description(self, html_description):
        """
        Generates table description from class docstrings and converts them
        into html

        :param html_description: Dictionary containing table descriptions
        :type html_description: dict

        :return: Dictionary containing table descriptions
        :rtype: dict
        """
        FORMAT_DESCRIPTION[self.name] = self.__doc__
        for name in [self.name, self.options.comparison_mode]:
            descrip = FORMAT_DESCRIPTION[name]
            descrip = descrip.replace(':ref:', '')
            js = get_js(self.options, self.group_dir)
            docsettings = {
                'math_output': 'MathJax '+js['mathjax']
            }
            description_page = docutils.core.publish_parts(
                descrip,
                writer_name='html',
                settings_overrides=docsettings)
            html_description[name] = description_page['body']
            html_description[name] = html_description[name].replace(
                '<blockquote>\n', '')
        return html_description

    @property
    def table_title(self):
        """
        Getter function for table name if self._table_title is None

        :return: name of table
        :rtype: str
        """
        if self._table_title is None:
            self._table_title = "FitBenchmarking: {0} table".format(self.name)
        return self._table_title

    @table_title.setter
    def table_title(self, value):
        """
        Setting function to set the name of the table

        :param value: name of table
        :type value: str
        """
        self._table_title = value

    @property
    def file_path(self):
        """
        Getter function for the path to the table

        :return: path to table
        :rtype: str
        """
        if self._file_path is None:
            self._file_path = os.path.join(self.group_dir, self.table_name)
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        """
        Setting function to set the path to the table

        :param value: path to table
        :type value: str
        """
        self._file_path = value

    @staticmethod
    def _vals_to_colour(vals, cmap, cmap_range, log_ulim):
        """
        Converts an array of values to a list of hexadecimal colour
        strings using logarithmic sampling from a matplotlib colourmap
        according to relative value.

        :param vals: values in the range [0, 1] to convert to colour strings
        :type vals: list[float]

        :param cmap: matplotlib colourmap
        :type cmap: matplotlib colourmap object

        :param cmap_range: values in range [0, 1] for colourmap cropping
        :type cmap_range: list[float], 2 elements

        :param log_ulim: log10 of worst shading cutoff value
        :type log_ulim: float

        :return: colours as hex strings for each input value
        :rtype: list[str]
        """
        log_vals = np.log10(vals)
        norm_vals = (log_vals - min(log_vals)) /\
            (log_ulim - min(log_vals))
        norm_vals[norm_vals > 1] = 1  # applying upper cutoff
        # trimming colour map according to default/user input
        norm_vals = cmap_range[0] + \
            norm_vals*(cmap_range[1] - cmap_range[0])
        rgba = cmap(norm_vals)
        hex_strs = [mpl.colors.rgb2hex(colour) for colour in rgba]

        return hex_strs

    @staticmethod
    def _save_colourbar(fig_path, cmap_name, cmap_range, title, left_label,
                        right_label, n_divs=100, sz_in=(3, 0.8)):
        """
        Generates a png of a labelled colourbar using matplotlib.

        :param fig_path: path to figure save location
        :type fig_path: str
        :param cmap_name: matplotlib colourmap name
        :type cmap: str
        :param cmap_range: range used to crop colourmap
        :type cmap_range: list[float] - 2 elements
        :param title: table-specifc text above colourbar
        :type title: str
        :param left_label: table-specifc text to left of colourbar
        :type left_label: str
        :param right_label: table-specific text to right of colourbar
        :type right_label: str
        :param n_divs: number of divisions of shading in colourbar
        :type n_divs: int
        :param sz_in: dimensions of png in inches [width, height]
        :type sz_in: list[float] - 2 elements
        """
        figh = 0.77
        fig, ax = plt.subplots(nrows=1, figsize=(6.4, figh))
        fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0.15 / figh,
                            left=0.3, right=0.7, hspace=1)
        gradient = np.linspace(cmap_range[0], cmap_range[1], n_divs)
        gradient = np.vstack((gradient, gradient))
        ax.imshow(gradient, aspect='auto',
                  cmap=plt.get_cmap(cmap_name), vmin=0, vmax=1)
        ax.text(-0.02, 0.5, left_label,
                va='center', ha='right', fontsize=6,
                transform=ax.transAxes)
        ax.text(1.02, 0.5, right_label,
                va='center', ha='left', fontsize=6,
                transform=ax.transAxes)
        ax.set_title(title, fontsize=6)
        ax.set_axis_off()
        fig.set_size_inches(sz_in[0], sz_in[1])

        plt.savefig(fig_path, dpi=150)
