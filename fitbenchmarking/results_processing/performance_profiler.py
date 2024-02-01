"""
Set up performance profiles for both accuracy and runtime tables
"""
import itertools
import os
import random

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc

from fitbenchmarking.results_processing.plots import Plot


def profile(results, fig_dir, options):
    """
    Function that generates profiler plots

    :param results: The sorted results grouped by row and category
    :type results: dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]
    :param fig_dir: path to directory containing the figures
    :type fig_dir: str
    :param options: The options for the run
    :type options: utils.options.Options

    :return: Path to performance profile graphs,
             data for plotting the performance profiles
    :rtype: dict[str, str], dict[str, pandas.DataFrame]
    """
    bounds = prepare_profile_data(results)

    pp_dfs = {}
    for pp_name, pp_dict in bounds.items():
        pp_dfs[pp_name] = pd.DataFrame.from_dict(pp_dict, orient='columns')

    plot_paths = get_plot_path(bounds,
                               fig_dir,
                               options)
    return plot_paths, pp_dfs


def prepare_profile_data(results):
    """
    Helper function which generates dictionaries for each metric containing
    names of solvers as the keys and a list of floats (one for each problem)
    as the values.

    :param results: The sorted results grouped by row and category
    :type results: dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]

    :return: dictionary containing number of occurrences
    :rtype: dict[str, dict[str, list[float]]]
    """
    pp_data = {
        'acc': {},
        'runtime': {},
        'emissions': {}
    }
    minimizers = []
    to_remove = set()

    for row in results.values():
        for cat in row.values():
            for i, result in enumerate(cat):
                key = result.modified_minimizer_name(with_software=True)
                if len(minimizers) <= i:
                    minimizers.append(key)
                    for pp in pp_data.values():
                        pp[key] = []
                elif len(key) > len(minimizers[i]):
                    to_remove.add(minimizers[i])
                    for pp in pp_data.values():
                        pp[key] = pp[minimizers[i]].copy()
                    minimizers[i] = key
                pp_data['acc'][minimizers[i]].append(result.norm_acc)
                pp_data['runtime'][minimizers[i]].append(result.norm_runtime)
                pp_data['emissions'][minimizers[i]].append(
                    result.norm_emissions)

    for key in to_remove:
        for pp in pp_data.values():
            del pp[key]

    return pp_data


def compute_step_values(profile_plot):
    """
    Function that creates the step values for plotting
    performance profiles.

    :param profile_plot: dictionary with accuracy or runtime data
    :type profile_plot: dict[str, list[float]]

    :retur: acc or runtime values to plot,
            maximum x value (acc or runtime)
    :rtype: list[float], float
    """
    step_values = []
    max_value = 0.0
    for value in profile_plot.values():
        value = np.array(value)
        sorted_list = np.sort(_remove_nans(value))
        max_in_list = np.max(sorted_list) if len(sorted_list) > 0 else 0.0
        if max_in_list > max_value:
            max_value = max_in_list
        step_values.append(np.insert(sorted_list, 0, 0.0))

    return step_values, max_value


def get_plot_path(bounds, fig_dir, options):
    """
    Function that generates profiler plots

    :param bounds: For each metric, a dictionary of solver names and the list
                   of values (one for each problem)
    :type bounds: dict[str, dict[str, list[float]]]
    :param fig_dir: path to directory containing the figures
    :type fig_dir: str
    :param options: The options for the run
    :type options: utils.options.Options

    :return: path to profile graphs for each metric
    :rtype: dict[str, str]
    """
    figure_paths = {}

    for name, profile_plot in bounds.items():
        this_filename_html = os.path.join(fig_dir, f"{name}_profile.html")

        figure_paths[name] = this_filename_html
        step_values, max_value = compute_step_values(profile_plot)

        linear_upper_limit = 10

        use_log_plot = True
        if max_value < linear_upper_limit:
            use_log_plot = False

        log_upper_limit = min(max_value+1, 10000)

        # Plot linear performance profile
        solvers = profile_plot.keys()

        max_n_solvers_offline = 15
        if len(solvers) < max_n_solvers_offline:
            fig = create_plot(step_values=step_values,
                              solvers=solvers)
            fig = update_fig(fig, name, use_log_plot,
                             log_upper_limit)

            Plot.write_html_with_link_plotlyjs(fig, fig_dir,
                                               this_filename_html,
                                               options)
        else:
            warning = '<div style="font-size: 14px !important; '\
                      'color: #ff0000; font-family: verdana"}><body>The '\
                      'number of solvers is too large '\
                      f'(> {max_n_solvers_offline}) to be displayed in '\
                      'a static offline plot. Please run Dash and use '\
                      'the online version instead. </body></div>'

            with open(this_filename_html, "w") as file:
                file.write(warning)

    return figure_paths

def update_fig(fig: go.Figure, name: str, use_log_plot: bool,
               log_upper_limit: int) -> go.Figure:
    """
    Update layout of plotly (or Dash) plot.

    :param fig: The performance profile plot
    :type fig: plotly.graph_objects.Figure
    :param name: The name of the graph
    :type name: str
    :param use_log_plot: Whether to use a log x axis or not
    :type use_log_plot: boolean
    :param log_upper_limit: The upper limit for the x axis (when log)
    :type log_upper_limit: int

    :return: Updated plot
    :rtype: plotly.graph_objects.Figure

    """
    linear_upper_limit = 10
    x_ticks = [1, 2, 5, 10, 100, 1000, 10000]
    x_ticks_labels = ["1", "2", "5", "10", "10<sup>2</sup>",
                      "10<sup>3</sup>", "10<sup>4</sup>"]
    if use_log_plot is True:
        x_limits = (1, log_upper_limit)
        fig.update_xaxes(type="log",
                         range=[np.log10(i) for i in x_limits],
                         tickvals=x_ticks,
                         ticktext=x_ticks_labels)
    else:
        x_limits = (1, linear_upper_limit)
        fig.update_xaxes(range=x_limits,
                         tickvals=x_ticks,
                         ticktext=x_ticks_labels)

    # Update appearance of graph
    graph_title = f"Performance profile - {name}"

    fig.update_layout(
        autosize=True,
        title={
            'text': graph_title,
            'y': 0.96,
            'x': 0.4,
            'xanchor': 'center'
        },
        xaxis_title='f',
        yaxis_title="fraction for which solver within f of best",
        legend={
            'font': {'size': 13},
            'y': 0.1
        },
        plot_bgcolor='white',
        font_family='verdana',
        font_color='#454545',
        margin={'t': 50, 'b': 70},
    )

    # Update both axis to show the grid
    fig.update_xaxes(
        showgrid=True,
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    fig.update_yaxes(
        showgrid=True,
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        range=(0, 1.05)
    )

    return fig


def _remove_nans(values: np.ndarray) -> np.ndarray:
    """
    Removes all the nan values from the provided numpy array.
    """
    return values[~np.isnan(values)]


def adjust_values_to_plot(step_values: 'list[np.ndarray]',
                          solvers: 'list[str]'):
    """
    Function to prepare values to plot

    :param step_values: A sorted list of the values of the metric
                        being profiled
    :type step_values: list[np.array[float]]
    :param solvers: A list of the labels for the different solvers
    :type solvers: list[str]

    :return: Data to plot
    :rtype: dict[str[list[float]]]
    """

    huge = 1.0e20  # set a large value as a proxy for infinity

    all_solvers = []
    all_labels = []
    all_solver_values = []
    all_plot_points = []

    for solver, solver_values in zip(solvers, step_values):
        solver = f"{solver}"
        label = f"{solver}"
        plot_points = np.linspace(0.0, 1.0, solver_values.size)
        plot_points = np.append(plot_points, 1.0)
        inf_indices = np.where(solver_values > huge)
        solver_values[inf_indices] = huge
        if inf_indices[0].size > 0:
            plural_ending = "s"
            if inf_indices[0].size == 1:
                plural_ending = ""
            label = f"{solver} ({len(inf_indices[0])} failure{plural_ending})"
        solver_values = np.append(solver_values, huge)

        all_labels.append(label)
        all_solvers.append(solver)
        all_solver_values.append(solver_values)
        all_plot_points.append(plot_points)

    values_for_plotting = {
        'solvers': all_solvers,
        'labels': all_labels,
        'solver_vals': all_solver_values,
        'plot_points': all_plot_points
    }

    return values_for_plotting


def create_plot(step_values: 'list[np.ndarray]',
                solvers: 'list[str]'):
    """
    Function to draw plot in plotly.

    :param step_values: A sorted list of the values of the metric
                        being profiled
    :type step_values: list of np.array[float]
    :param solvers: A list of the labels for the different solvers
    :type solvers: list of strings

    :return: The perfomance profile graph
    :rtype: plotly.graph_objects.Figure
    """

    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    # Use only 3 of the possible 5 linestyles, because 5 is a factor
    # of 10 (number of colours) and using 10 colours + 5 linestyles
    # would not give enough line/colour combinations
    linestyles = ['solid', 'dash', 'dashdot']

    data_dict = adjust_values_to_plot(
        step_values=step_values,
        solvers=solvers
    )

    for i, (solver, solver_vals, plot_points) in enumerate(zip(
                                                    data_dict['solvers'],
                                                    data_dict['solver_vals'],
                                                    data_dict['plot_points']
                                                    )):

        fig.add_trace(
            go.Scatter(x=solver_vals,
                       y=plot_points,
                       mode='lines',
                       line={"shape": 'hv',
                             "dash": linestyles[(i % len(linestyles))],
                             "color": colors[(i % len(colors))]},
                       name=solver,
                       type='scatter'
                       )
            )

    return fig


def create_df(solvers: 'list[str]', labels: 'list[str]',
              solver_values: 'list[np.ndarray]',
              plot_points: 'list[np.ndarray]') -> pd.DataFrame:
    """
    Creates a df with performance profile data.

    :param solvers: The names of the solvers
    :type solvers: list[str]
    :param labels: The labels for the solvers (showing n failures)
    :type labels: list[str]
    :param solver_values: The solver values (x values) for each solver
    :type solver_values: list[numpy.array]
    :param plot_points: The y values for each solver
    :type plot_points: list[numpy.array]

    :return: Performance profile data
    :rtype: pandas.DataFrame
    """

    # Prepare data to save
    if len(solvers) == 0:
        data_dict = {
            'solver': [],
            'label': [],
            'x': [],
            'y': []
        }

    else:
        solvers_repeated = np.repeat(solvers, len(plot_points[0]))
        labels_repeated = np.repeat(labels, len(plot_points[0]))
        solver_values = list(np.concatenate(solver_values))
        plot_points = list(np.concatenate(plot_points))

        data_dict = {
            'solver': solvers_repeated,
            'label': labels_repeated,
            'x': solver_values,
            'y': plot_points
        }

    pp_df = pd.DataFrame.from_dict(data_dict)
    return pp_df

class DashPerfProfile():

    """General class for creating performance profiles."""

    def __init__(self, profile_name, pp_df, group_label):
        """
        Initialises a performance profile graph.

        :param profile_name: The name of the profile (e.g. runtime)
        :type profile_name: str
        :param pp_df: The data for creating the graph
        :type pp_df: pandas.DataFrame
        :param group_label: The group directory the plot belongs to
        :type group_label: str
        """

        self.data = pp_df
        self.profile_name = profile_name
        self.group_label = group_label
        self.identif = self.group_label + '-' + self.profile_name

        self.default_opt = []
        for solver in self.data.columns:
            self.default_opt.append({
                "value": solver,
                "label": solver
            })

        self.linestyling = {}
        self.avail_styles = {}

        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                       '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        self.linestyles = ['solid', 'dash', 'dashdot']

        for comb in list(itertools.product(self.linestyles, self.colors)):
            comb_id = comb[0]+comb[1]
            self.avail_styles[comb_id] = comb

        self.layout()
        self.set_callbacks()

    def layout(self):
        """
        Creates and returns the dash plot for the performance profile,
        which is used in fitbenchmarking/core/results_output, in the
        function "display_page".

        :return: Dash plot for the performance profile.
        :rtype: dcc.Graph
        """

        return dcc.Graph(id=f"visual {self.identif}")

    def set_callbacks(self):
        """Calls callbacks on the function that creates the dash graph."""

        dash.callback(
            Output(f"visual {self.identif}", "figure"),
            [Input("Log axis toggle", "value"),
             Input("dropdown", "value")]
        )(self.create_graph)

    def update_linestyles(self, solvers) -> None:
        """
        Function to determine a linestyle for each solver.

        :param solvers: Solvers to be selected, max 15
        :type solvers: list[str]
        """
        previous_solvers = list(self.linestyling.keys())

        # If this is the first time executing the code
        if len(previous_solvers) == 0:
            for i, solver in enumerate(solvers):
                linestyle = self.linestyles[(i % len(self.linestyles))]
                linecolor = self.colors[(i % len(self.colors))]
                self.linestyling[solver] = {
                    'linestyle': linestyle,
                    'linecolor': linecolor,
                }
                comb_id = linestyle+linecolor
                del self.avail_styles[comb_id]

        # If a solver has been added
        elif len(solvers) > len(previous_solvers):

            newly_added_solvers = set(solvers).difference(previous_solvers)

            for solver in newly_added_solvers:
                chosen_style = list(self.avail_styles.values())[-1]
                self.linestyling[solver] = {
                    'linestyle': chosen_style[0],
                    'linecolor': chosen_style[1],
                }
                comb_id = chosen_style[0]+chosen_style[1]
                del self.avail_styles[comb_id]

        # If a solver has been removed
        elif len(solvers) < len(previous_solvers):

            solvers_to_remove = set(previous_solvers).difference(solvers)

            for solver in solvers_to_remove:
                linestyle = self.linestyling[solver]['linestyle']
                linecolor = self.linestyling[solver]['linecolor']
                self.avail_styles[linestyle+linecolor] = (linestyle, linecolor)
                self.linestyling.pop(solver)

    def get_data(self, solvers):
        """
        Function to prepare values for plotting performance profiles.

        :param solvers: Solvers to be selected, max 15
        :type solvers: list[str]

        :return: Performance profile data
        :rtype: pandas.DataFrame
        """

        df_chosen_solvers = self.data.loc[:, solvers]
        df_chosen_solvers['min'] = df_chosen_solvers.min(axis=1)
        df_chosen_solvers['min'].replace(to_replace=np.inf, value=1.0,
                                         inplace=True)
        df_chosen_solvers = df_chosen_solvers.divide(df_chosen_solvers['min'],
                                                     axis="rows")
        df_chosen_solvers.drop(columns=['min'])
        new_dict = df_chosen_solvers.to_dict('list')

        step_values, _ = compute_step_values(new_dict)

        data_dict = adjust_values_to_plot(
            step_values=step_values,
            solvers=solvers
        )

        output_df = create_df(data_dict['solvers'],
                              data_dict['labels'],
                              data_dict['solver_vals'],
                              data_dict['plot_points'])
        return output_df

    def create_graph(self, x_axis_scale, solvers):
        """
        Creates the dash plot.

        :param x_axis_scale: Can be either "Log x-axis" or "Linear x-axis"
        :type x_axis_scale: str
        :param solvers: The solvers to show in the graph
        :type solvers: list[str]

        :return: Figure for the Dash plot
        :rtype: plotly.graph_objects.Figure
        """

        fig = go.Figure()

        df_selected_solvers = self.get_data(solvers)
        self.update_linestyles(df_selected_solvers['solver'].unique())

        max_value = 0

        # Setting sort to False ensures the color for each solver
        # in the dash plot is the same as in the offline plot
        grouped_data = df_selected_solvers.groupby('solver', sort=False)

        for solver, data_one_solver in grouped_data:

            solver_values = data_one_solver['x']
            plot_points = data_one_solver['y']
            solver_label = list(data_one_solver['label'])[0]

            temp_max_value = max(list(solver_values))
            if temp_max_value > max_value:
                max_value = temp_max_value

            fig.add_trace(
                go.Scatter(
                    x=solver_values,
                    y=plot_points,
                    mode='lines',
                    line={
                        "shape": 'hv',
                        "dash": self.linestyling[solver]['linestyle'],
                        "color": self.linestyling[solver]['linecolor'],
                    },
                    name=solver_label,
                    type='scatter'))

        log_upper_limit = min(max_value+1, 10000)
        use_log_plot = (x_axis_scale == 'Log x-axis')

        fig = update_fig(fig, self.profile_name, use_log_plot,
                         log_upper_limit)

        return fig
