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

        step_values = []
        for value in profile_plot.values():
            sorted_list = np.sort(value)
            step_values.append(np.insert(sorted_list, 0, 0.0))

        no_failures = np.zeros(len(step_values),dtype=np.int8)
        huge = 1.0e20 # set a large value as a proxy for infinity
        for i,solver_values in enumerate(step_values):
            inf_indices = np.where(solver_values > huge)
            solver_values[inf_indices] = huge
            if inf_indices:
                no_failures[i] = len(inf_indices[0])
        
        uniform_steps = np.linspace(0.0, 1.0, step_values[0].size)

        labels = [key for key in acc.keys()]
        for i, solver in enumerate(labels):
            if no_failures[i]:
                labels[i] = "{} ({} failures)".format(solver,no_failures[i])
        fig = plt.figure()
        lines = [ "-", "-.", "--",":"]
        colors = ["g", "r", "b", "k", "c","m"]
        for s, step_value in enumerate(step_values):
            plt.step(step_value,
                     uniform_steps,
                     label=labels[s],
                     color=colors[(s % len(colors))],
                     linestyle=lines[(s % len(lines))],
                     lw=1.5,
                     where='post')
        plt.title("{}".format(name))
        plt.ylim(0.0,1.0)
        plt.ylabel("fractions for which solver within f of best")
        max_value = np.max([np.max(v)
                             for v in profile_plot.values()])
        plt.xlim(1,min(max_value+1,10))
        plt.xlabel("f")
        plt.legend(loc=4)
        #plt.gca().set_xscale("log")
        plt.savefig(name_template.format(name))
        
    return figure_path[0], figure_path[1]

