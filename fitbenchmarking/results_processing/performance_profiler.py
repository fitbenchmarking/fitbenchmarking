"""
Set up performance profiles for both accuracy and runtime tables
"""
from collections import OrderedDict
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def profile(results, fig_dir):
    """
    Function that generates profiler plots

    :param results : results nested array of objects
    :type results : list of list of
                    fitbenchmarking.utils.fitbm_result.FittingResult
    :param fig_dir : path to directory containing the figures
    :type fig_dir : str

    :return : path to acc and runtime profile graphs
    :rtype : tuple(str, str)
    """
    acc_bound, runtime_bound = prepare_profile_data(results)
    acc_plot_path, runtime_plot_path = plot(
        acc_bound, runtime_bound, fig_dir)
    return acc_plot_path, runtime_plot_path


def prepare_profile_data(results):
    """
    Helper function which generates acc and runtime dictionaries which
    contain number of occurrences that the minimizer produces a normalised
    result which is less than the bounds in PROFILER_BOUNDS

    :param results : results nested array of objects
    :type results : list of list of
                    fitbenchmarking.utils.fitbm_result.FittingResult

    :return : dictionary containing number of occurrences
    :rtype : tuple(dict, dict)
    """
    out_acc = []
    out_runtime = []
    for res in results:
        out_acc.append([r.norm_acc for r in res])
        out_runtime.append([r.norm_runtime for r in res])
    minimizers = [r.minimizer for r in results[0]]

    acc_array = np.array(out_acc).T
    runtime_array = np.array(out_runtime).T
    acc_dict = OrderedDict()
    runtime_dict = OrderedDict()

    for i, m in enumerate(minimizers):
        acc_dict[m] = acc_array[i][:]
        runtime_dict[m] = runtime_array[i][:]
    return acc_dict, runtime_dict


def plot(acc, runtime, fig_dir):
    """
    Function that generates profiler plots

    :param acc : acc dictionary containing number of occurrences
    :type acc : dict
    :param runtime : runtime dictionary containing number of occurrences
    :type runtime : dict
    :param fig_dir : path to directory containing the figures
    :type fig_dir : str

    :return : path to acc and runtime profile graphs
    :rtype : tuple(str, str)
    """
    name_template = "{}_profile.png"
    figure_path = []
    for profile_plot, name in zip([acc, runtime], ["acc", "runtime"]):
        figure_path.append(os.path.join(fig_dir, name_template.format(name)))
        max_value = np.max([np.max(v) for v in profile_plot.values()])
        bins = np.logspace(np.log10(1), np.log10(max_value), 1000)
        hist_values = [value for value in profile_plot.values()]
        names = [key for key in acc.keys()]
        fig = plt.figure()
        n, bins, patches = plt.hist(hist_values, bins=bins, density=True,
                                    cumulative=True, histtype="step",
                                    label=names)
        plt.title(name)
        plt.legend()
        plt.gca().set_xscale("log")

    return figure_path[0], figure_path[1]
