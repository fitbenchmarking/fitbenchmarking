"""
Set up performance profiles for both accuracy and runtime tables
"""
import os

import matplotlib
import numpy as np
import plotly
import plotly.graph_objects as go

matplotlib.use('Agg')


def profile(results, fig_dir):
    """
    Function that generates profiler plots

    :param results: The sorted results grouped by row and category
    :type results: dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]
    :param fig_dir: path to directory containing the figures
    :type fig_dir: str

    :return: path to acc and runtime profile graphs
    :rtype: tuple(str, str)
    """
    acc_bound, runtime_bound = prepare_profile_data(results)
    plot_path = plot(acc_bound, runtime_bound, fig_dir)
    return plot_path


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


def plot(acc, runtime, fig_dir):
    """
    Function that generates profiler plots

    :param acc: acc dictionary containing number of occurrences
    :type acc: dict
    :param runtime: runtime dictionary containing number of occurrences
    :type runtime: dict
    :param fig_dir: path to directory containing the figures
    :type fig_dir: str

    :return: path to acc and runtime profile graphs
    :rtype: tuple(str, str)
    """
    figure_path = []
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

        # Get second largest value and use it to set an x limit on the graph
        all_vals = set([elem for sublist in step_values for elem in sublist])
        all_vals.remove(max_value)
        all_vals = list(all_vals)
        x_upper_limit = max(all_vals)

        # Plot linear performance profile
        keys = profile_plot.keys()
        fig = create_plot(step_values, keys)

        # Change x axis to log, if needed, and set x limits
        x_ticks = [1, 2, 5, 10, 100, 1000, 10000]
        x_limits = (1, x_upper_limit)

        if use_log_plot is True:
            fig.update_xaxes(type="log",
                             range=[np.log10(i) for i in x_limits],
                             tickvals=x_ticks
                             )
        else:
            fig.update_xaxes(range=x_limits,
                             tickvals=x_ticks
                             )

        # Update appearance of graph
        fig.update_layout(autosize=True,
                          title={'text': f"Performance profile - {name}",
                                  'y': 0.9,
                                  'x': 0.5,
                                  'xanchor': 'center'
                                  },
                          xaxis_title='f',
                          yaxis_title="fraction for which solver"
                                      "within f of best",
                          legend={'font': {'size': 13},
                                  'y': 0.1
                                  }
                          )

        # Create html file
        plotly.offline.plot(fig, filename=this_filename_html)

    return figure_path


def _remove_nans(values: np.ndarray) -> np.ndarray:
    """
    Removes all the nan values from the provided numpy array.
    """
    return values[~np.isnan(values)]


def create_plot(step_values: 'list[np.ndarray]', solvers: 'list[str]'):

    """
    Function to draw the profile in plotly

    :param step_values: A sorted list of the values of the metric
                        being profiled
    :type step_values: list of np.array[float]
    :param solvers: A list of the labels for the different solvers
    :type solvers: list of strings

    :return: The perfomance profile graph
    :rtype: plotly.graph_objs._figure.Figure
    """

    fig = go.Figure()
    new_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    linestyles = ['solid', 'dash', 'dashdot']

    huge = 1.0e20  # set a large value as a proxy for infinity

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

        fig.add_trace(
            go.Scatter(x=solver_values,
                       y=plot_points,
                       mode='lines',
                       line={"shape": 'hv',
                             "dash": linestyles[(i % len(linestyles))],
                             "color": new_colors[(i % len(new_colors))]},
                       name=solver,
                       type='scatter'
                       )
            )

    return fig
