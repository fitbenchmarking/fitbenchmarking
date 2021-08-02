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
        :param best_results: best result for each problem split by cost func
        :type best_results:
            list[dict[str:fitbenchmarking.utils.fitbm_result.FittingResult]]
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

        self.create_results_dict()

    def create_results_dict(self):
        """
        Generates a dictionary used to create HTML and txt tables.
        This is stored in self.sorted_results
        """
        sort_order = (['problem'],
                      ['costfun', 'minimizer', 'jacobian'])

        sets = {
            'problem': set(),
            'minimizer': set(),
            'jacobian': set(),
            'costfun': set(),
        }

        for r in self.results:
            for k, s in sets.items():
                s.add(getattr(r, k))

        lookups = {k: {i: v
                       for i, v in enumerate(sorted(s))}
                   for k, s in sets.items()}

        columns = ['']
        for sort_pos in sort_order[1]:
            columns = [f'{stub}_{suff}'
                       for stub in columns
                       for suff in lookups[sort_pos].values()]
        cols_dict = {k.strip(':'): i
                     for i, k in enumerate(columns)}

        rows = ['']
        for sort_pos in sort_order[0]:
            rows = [f'{stub}:{suff}'
                    for stub in rows
                    for suff in lookups[sort_pos].values()
                    ]

        sorted_results = {r.strip(':'): [None for _ in columns]
                          for r in rows}

        for r in self.results:
            row = ''
            col = ''
            for sort_pos in reversed(sort_order[0]):
                row += f':{getattr(r, sort_pos)}'
            row = row.strip(':')
            for sort_pos in reversed(sort_order[1]):
                col += f':{getattr(r, sort_pos)}'
            col = cols_dict[col.strip(':')]

            sorted_results[row][col] = r

        self.sorted_results = sorted_results

    def get_str_dict(self, html=False):
        """
        Create a dictionary of with the table values as strings for display.

        :return: The dictionary of values for the table
        :rtype: dict[list[str]]
        """
        return {k: [self.get_str_result(v, html) for v in values]
                for k, values in self.sorted_results.items()}

    def get_str_result(self, result, html=False):
        if html:
            val = self.get_value(result)
            val_str = self.display_str(val)
            val_str += self.get_error_str(result, error_template="<sup>{}</sup>")
            val_str = f'<a href="{self.get_link_str(result)}" style="background-colour:{self.get_colour_str(val)}">{val_str}</a>'
        else:
            val_str = self.display_str(self.get_value(result))
            val_str += self.get_error_str(result, error_template='[{}]')
        return val_str

    @abstractmethod
    def get_value(self, result):
        """
        Gets the main value to be reported in the tables for a given result

        :param result: The result to generate the values for.
        :type result: FittingResult

        :return: The value to convert to a string for the tables
        :rtype: tuple(float)
        """
        raise NotImplementedError

    def display_str(self, value):
        """
        Converts the a results value generated by
        :meth:`~fitbenchmarking.results_processing.base_table.Table.get_values()`
        into a string respresentation to be used in the tables.
        Base class implementation takes
        the absolute and relative values and uses ``self.output_string_type``
        as a template for the string format. This can be overwritten to
        adequately display the results.

        :param value: tuple containing absolute and relative values
        :type value: tuple

        :return: string representation of the value for display in the table.
        :rtype: str
        """
        abs_value, rel_value = value
        comp_mode = self.options.comparison_mode
        result_template = self.output_string_type[self.options.comparison_mode]
        if comp_mode == "abs":
            return result_template.format(abs_value)
        elif comp_mode == "rel":
            return result_template.format(rel_value)
        # comp_mode == "both"
        return result_template.format(abs_value, rel_value)

    def get_colour_str(self, value):
        """
        Get the colour as a string for the given value in the table.
        The base class implementation, for example,
        uses the relative results and
        ``colour_map``, ``colour_ulim`` and ``cmap_range`` within
        :class:`~fitbenchmarking.utils.options.Options`.

        :param result: tuple containing absolute and relative values
        :type result: tuple[float]
        :return: The colour to use for the cell
        :rtype: str
        """
        cmap_name = self.options.colour_map
        cmap = plt.get_cmap(cmap_name)
        cmap_ulim = self.options.colour_ulim
        cmap_range = self.options.cmap_range
        log_ulim = np.log10(cmap_ulim)  # colour map used with log spacing
        log_llim = np.log10(???)
        _, rel_value = value
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

    def create_pandas_data_frame(self, html=False):
        """
        Creates a pandas data frame of results

        :return: pandas data frame with from results
        :rtype: Pandas DataFrame
        """
        str_results = self.get_str_dict(html)
        table = pd.DataFrame.from_dict(str_results, orient='index')
        minimizers_list = [(s, m) for s in self.options.software
                           for m in self.options.minimizers[s]]
        columns = pd.MultiIndex.from_tuples(minimizers_list)
        table.columns = columns
        return table

    def to_html(self):
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
        table = self.create_pandas_data_frame(html=True)
        link_template = '<a href="https://fitbenchmarking.readthedocs.io/'\
                        'en/latest/users/options/minimizer_option.html#'\
                        '{0}-{0}" target="_blank">{0}</a>'
        minimizer_template = '<span title="{0}">{1}</span>'

        minimizers_list = [(link_template.format(s.replace("_", "-")),
                           minimizer_template.format(
                               self.options.minimizer_alg_type[m], m))
                           for s in self.options.software
                           for m in self.options.minimizers[s]]
        columns = pd.MultiIndex.from_tuples(minimizers_list)
        table.columns = columns

        index = []
        for b, i in zip(self.best_results, table.index):
            rel_path = os.path.relpath(
                path=b.values()[0].problem_summary_page_link,
                start=self.group_dir)
            index.append('<a href="{0}">{1}</a>'.format(rel_path, i))
        table.index = index
        table_style = table.style.apply(
            lambda x: self.colour_highlight(x, colour), axis=1)

        return table_style.render()
    
    def to_txt(self):
        table = self.create_pandas_data_frame(html=False)
        return table.to_string()

    def get_link_str(self, result):
        """
        Get the link as a string for the result

        :param result: The result to get the link for
        :type result: FittingResult

        :return: The link to go to when the cell is selectedddd
        :rtype: string
        """
        return result.support_page_link

    def get_error_str(self, result, error_template='[{}]'):
        """
        Get the error string for a result based on error_template

        :param result: The result to get the error string for
        :type result: FittingResult

        :return: A string representation of the error for the html tables
        :rtype: str
        """
        error_code = result.error_flag
        if error_code == 0:
            return ''

        return error_template.format(error_code)

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
