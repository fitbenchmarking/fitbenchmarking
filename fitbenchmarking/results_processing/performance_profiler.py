"""
Set up performance profiles for both accuracy and runtime tables
"""
import os
from textwrap import wrap

import matplotlib
import numpy as np

matplotlib.use('Agg')
# pylint: disable=wrong-import-position,ungrouped-imports
import matplotlib.pyplot as plt  # noqa: E402
# pylint: enable=wrong-import-position,ungrouped-imports


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
    for row in results.values():
        for cat in row.values():
            for i, result in enumerate(cat):
                key = result.modified_minimizer_name(with_software=True)
                if len(minimizers) <= i:
                    minimizers.append(key)
                    acc_dict[key] = []
                    runtime_dict[key] = []
                elif len(key) > len(minimizers[i]):
                    acc_dict[key] = acc_dict.pop(minimizers[i])
                    runtime_dict[key] = runtime_dict.pop(minimizers[i])
                    minimizers[i] = key
                acc_dict[minimizers[i]].append(result.norm_acc)
                runtime_dict[minimizers[i]].append(result.norm_runtime)

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
        this_filename = os.path.join(fig_dir, "{}_profile.png".format(name))
        figure_path.append(this_filename)

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
            # if we don't need a log plot, then don't print one
            fig, ax = plt.subplots(1, 2,
                                   gridspec_kw={
                                       'width_ratios': [30, 7.8],
                                       'wspace': 0.01})
            legend_ax = 1
            use_log_plot = False
        else:
            fig, ax = plt.subplots(1, 3,
                                   sharey=True,
                                   gridspec_kw={
                                       'width_ratios': [10, 20, 7.8],
                                       'wspace': 0.01})
            legend_ax = 2

        # Plot linear performance profile
        keys = profile_plot.keys()
        create_plot(ax[0], step_values, keys)
        ax[0].set_xlim(1, linear_upper_limit)
        ax[0].set_xticks([1, 2, 4, 6, 8, 10])
        ax[0].set_xticklabels(['$1$', '$2$', '$4$', '$6$', '$8$', '$10$'])
        ax[0].yaxis.set_ticks_position('left')

        if use_log_plot:
            # Plot log performance profile
            create_plot(ax[1], step_values, keys)
            ax[1].set_xlim(
                linear_upper_limit,
                min(max_value+1, 10000))
            ax[1].set_xscale('log')
            ax[1].set_xticks([100, 1000, 10000])
            ax[1].set_xticklabels(['$10^2$', '$10^3$', '$10^4$'])
            ax[1].yaxis.set_ticks_position('right')
            ax[1].tick_params(axis='y', labelcolor='white')

        # legend
        ax[legend_ax].axis('off')
        handles, labels = ax[0].get_legend_handles_labels()
        wrapped_labels = ['\n'.join(wrap(label, 22)) for label in labels]
        ax[legend_ax].legend(handles, wrapped_labels, loc=2, prop={'size': 7})

        # Common parts
        plt.ylim(0.0, 1.0)
        fig.suptitle("Performance profile - {}".format(name))

        # add a big axis, hide frame
        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axis
        plt.tick_params(labelcolor='none',
                        top=False,
                        bottom=False,
                        left=False,
                        right=False)
        # the xlabel has added white space to (empirically) make it look
        # centred under the plots (and not the legend)
        plt.xlabel("f                       ")
        plt.ylabel("fraction for which solver within f of best")
        ax[0].set_ylim(0.0, 1.05)

        plt.savefig(this_filename, dpi=150)

    return figure_path


def _remove_nans(values: np.ndarray) -> np.ndarray:
    """
    Removes all the nan values from the provided numpy array.
    """
    return values[~np.isnan(values)]


def create_plot(ax, step_values: 'list[np.ndarray]', solvers: 'list[str]'):
    """
    Function to draw the profile on a matplotlib axis

    :param ax: A matplotlib axis to be filled
    :type ax: an `.axes.SubplotBase` subclass of `~.axes.Axes`
              (or a subclass of `~.axes.Axes`)
    :param step_values: a sorted list of the values of the metric
                        being profiled
    :type step_values: list of np.array[float]
    :param solvers: A list of the labels for the different solvers
    :type solvers: list of strings
    """
    lines = ["-", "-.", "--", ":"]
    # use only 9 of matplotlib's colours, as this will give us
    # 9 * 4 = 36 line/colour combinations, as opposed to
    # 10 * 4 / 2 = 20 if we used all 10
    colors = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]

    huge = 1.0e20  # set a large value as a proxy for infinity
    plot_points = np.linspace(0.0, 1.0, step_values[0].size)
    plot_points = np.append(plot_points, 1.0)

    for i, (solver, solver_values) in enumerate(zip(solvers, step_values)):
        inf_indices = np.where(solver_values > huge)
        solver_values[inf_indices] = huge
        if inf_indices[0].size > 0:
            plural_ending = "s"
            if inf_indices[0].size == 1:
                plural_ending = ""
            solver = "{} ({} failure{})".format(solver,
                                                len(inf_indices[0]),
                                                plural_ending)
        solver_values = np.append(solver_values, huge)
        ax.step(solver_values,
                plot_points,
                label=solver,
                linestyle=lines[(i % len(lines))],
                color=colors[(i % len(colors))],
                lw=2.0,
                where='post')
