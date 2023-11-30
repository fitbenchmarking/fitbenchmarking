"""
Set up performance profiles for both accuracy and runtime tables
"""
import os

import numpy as np
import plotly.graph_objects as go
import pandas as pd
import dash
from dash import html, dcc, Input, Output


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

    :return: Path to acc and runtime profile graphs;
             dictionary of dataframes for plotting the graphs
    :rtype: (str, str); dict[str, pandas.DataFrame]
    """
    acc_bound, runtime_bound = prepare_profile_data(results)
    plot_path, data_dfs = get_plot_path_and_data(acc_bound,
                                                 runtime_bound,
                                                 fig_dir,
                                                 options)
    return plot_path, data_dfs


def prepare_profile_data(results):
    """
    Helper function which generates acc and runtime dictionaries which
    contain the values for each minimizer.

    :param results: The sorted results grouped by row and category
    :type results: dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]

    :return: dictionary containing number of occurrences
    :rtype: tuple(dict, dict)
    """
    acc_dict = {}
    runtime_dict = {}
    minimizers = []
    to_remove = set()

    for row in results.values():
        for cat in row.values():
            for i, result in enumerate(cat):
                key = result.modified_minimizer_name(with_software=True)
                if len(minimizers) <= i:
                    minimizers.append(key)
                    acc_dict[key] = []
                    runtime_dict[key] = []
                elif len(key) > len(minimizers[i]):
                    to_remove.add(minimizers[i])
                    acc_dict[key] = acc_dict[minimizers[i]].copy()
                    runtime_dict[key] = runtime_dict[minimizers[i]].copy()
                    minimizers[i] = key
                acc_dict[minimizers[i]].append(result.norm_acc)
                runtime_dict[minimizers[i]].append(result.norm_runtime)

    for key in to_remove:
        del acc_dict[key]
        del runtime_dict[key]

    return acc_dict, runtime_dict


def get_plot_path_and_data(acc, runtime, fig_dir, options):
    """
    Function that generates profiler plots

    :param acc: acc dictionary containing number of occurrences
    :type acc: dict
    :param runtime: runtime dictionary containing number of occurrences
    :type runtime: dict
    :param fig_dir: path to directory containing the figures
    :type fig_dir: str
    :param options: The options for the run
    :type options: utils.options.Options

    :return: path to acc and runtime profile graphs;
             dictionary with dataframes for plotting the graphs
    :rtype: list[str]; dict[str, pandas.DataFrame]
    """
    figure_path = []
    data_dfs = {}
    for profile_plot, name in zip([acc, runtime], ["acc", "runtime"]):
        this_filename_html = os.path.join(fig_dir, f"{name}_profile.html")

        figure_path.append(this_filename_html)

        step_values = []
        max_value = 0.0
        for value in profile_plot.values():
            value = np.array(value)
            sorted_list = np.sort(_remove_nans(value))
            max_in_list = np.max(sorted_list) if len(sorted_list) > 0 else 0.0
            if max_in_list > max_value:
                max_value = max_in_list
            step_values.append(np.insert(sorted_list, 0, 0.0))

        linear_upper_limit = 10

        use_log_plot = True
        if max_value < linear_upper_limit:
            use_log_plot = False

        log_upper_limit = min(max_value+1, 10000)

        # Plot linear performance profile
        keys = profile_plot.keys()
        fig, data_df = create_plot_and_df(step_values=step_values,
                                          solvers=keys)

        data_dfs[name] = data_df

        fig = update_fig(fig, name, use_log_plot,
                         log_upper_limit)

        Plot.write_html_with_link_plotlyjs(fig,
                                           fig_dir,
                                           this_filename_html,
                                           options)

    return figure_path, data_dfs


def update_fig(fig, name, use_log_plot, log_upper_limit):

    """Update layout of plotly (or Dash) plot.

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
            'y': 0.85,
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


def create_plot_and_df(step_values: 'list[np.ndarray]',
                       solvers: 'list[str]'):

    """
    Function to draw the profile in plotly

    :param step_values: A sorted list of the values of the metric
                        being profiled
    :type step_values: list of np.array[float]
    :param solvers: A list of the labels for the different solvers
    :type solvers: list of strings

    :return: The perfomance profile graph; the data for plotting the graph
    :rtype: plotly.graph_objects.Figure; pandas.DataFrame
    """

    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    # Use only 3 of the possible 5 linestyles, because 5 is a factor
    # of 10 (number of colours) and using 10 colours + 5 linestyles
    # would not give enough line/colour combinations
    linestyles = ['solid', 'dash', 'dashdot']

    huge = 1.0e20  # set a large value as a proxy for infinity

    all_solvers = []
    all_solver_values = []
    all_plot_points = []

    for i, (solver, solver_values) in enumerate(zip(solvers, step_values)):
        plot_points = np.linspace(0.0, 1.0, solver_values.size)
        plot_points = np.append(plot_points, 1.0)
        inf_indices = np.where(solver_values > huge)
        solver_values[inf_indices] = huge
        if inf_indices[0].size > 0:
            plural_ending = "s"
            if inf_indices[0].size == 1:
                plural_ending = ""
            solver = f"{solver} ({len(inf_indices[0])} failure{plural_ending})"
        solver_values = np.append(solver_values, huge)

        all_solvers.append(solver)
        all_solver_values.append(solver_values)
        all_plot_points.append(plot_points)

        fig.add_trace(
            go.Scatter(x=solver_values,
                       y=plot_points,
                       mode='lines',
                       line={"shape": 'hv',
                             "dash": linestyles[(i % len(linestyles))],
                             "color": colors[(i % len(colors))]},
                       name=solver,
                       type='scatter'
                       )
            )

    data_df = create_df(all_solvers,
                        all_solver_values,
                        all_plot_points)

    return fig, data_df


def create_df(solvers, solver_values, plot_points):
    """
    Creates a df with performance profile data.

    :param solvers: The list of solvers
    :type solvers: list[str]
    :param solver_values: The solver values (x values) for each solver
    :type solver_values: list[numpy.array]
    :param plot_points: The y values for each solver
    :type plot_points: list[numpy.array]

    :return: Dataframe with performance profile data
    :rtype: pd.DataFrame
    """

    solvers_repeated = np.repeat(solvers, len(plot_points[0]))

    def flatten(list_i):
        return [item for sublist in list_i for item in sublist]

    solver_values = flatten(solver_values)
    plot_points = flatten(plot_points)

    data_dict = {}
    data_dict['solver'] = solvers_repeated
    data_dict['x'] = solver_values
    data_dict['y'] = plot_points

    data_df = pd.DataFrame.from_dict(data_dict)
    return data_df


class DashPerfProfile():

    """General class for creating performance profiles."""

    def __init__(self, profile_name, data_df, group_label):

        """Initialises a performance profile graph.

        :param profile_name: the name of the profile (e.g. runtime)
        :type profile_name: str
        :param data_df: the data for creating the graph
        :type data_df: pandas.DataFrame
        :param group_label: the group_dir this plot refers to
        :type group_label: str
        """

        self.data = data_df
        self.profile_name = profile_name
        self.group_label = group_label
        self.identif = self.group_label + '-' + self.profile_name
        self.layout()
        self.set_callbacks()

    def layout(self):

        """Creates and returns the layout for the performance profile."""

        layout = html.Div([
            dcc.RadioItems(
                id=f"Log axis toggle {self.identif}",
                options=["Log x-axis", "Linear x-axis"],
                value="Log x-axis",
                labelStyle={"margin-top": "1rem",
                            "margin-left": "1rem",
                            "margin-right": "1rem",
                            "margin-bottom": "0rem"},
                style={"display": "flex",
                       "font-family": "verdana",
                       "color": '#454545',
                       "font-size": "15px"}
            ),
            dcc.Graph(id=f"visual {self.identif}")
            ],
        )
        return layout

    def set_callbacks(self):

        """Calls callbacks on the function that creates the dash graph."""

        dash.callback(
            Output(f"visual {self.identif}", "figure"),
            Input(f"Log axis toggle {self.identif}", "value")
            )(self.create_graph)

    def create_graph(self, x_axis_scale):

        """Creates the dash plot.

        :param x_axis_scale: can be either "Log x-axis" or "Linear x-axis"
        :type x_axis_scale: str

        :return: figure for the Dash plot
        :rtype: plotly.graph_objects.Figure
        """

        fig = go.Figure()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        linestyles = ['solid', 'dash', 'dashdot']

        i = 1
        max_value = 0
        for solver, data_one_solver in self.data.groupby('solver'):

            solver_values = data_one_solver['x']
            plot_points = data_one_solver['y']

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
                        "dash": linestyles[(i % len(linestyles))],
                        "color": colors[(i % len(colors))]
                    },
                    name=solver,
                    type='scatter'))
            i = i+1

        log_upper_limit = min(max_value+1, 10000)
        use_log_plot = (x_axis_scale == 'Log x-axis')

        fig = update_fig(fig, self.profile_name, use_log_plot,
                         log_upper_limit)
        return fig
