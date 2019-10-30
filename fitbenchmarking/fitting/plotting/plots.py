"""
Higher level functions that are used for plotting the raw data of a
problem, a best fit plot and a starting guess plot.
"""

from __future__ import (absolute_import, division, print_function)

import os
from fitbenchmarking.fitting.plotting.plot_helper import data, plot
from fitbenchmarking.utils import create_dirs


def make_plots(problem, best_fit, count, group_results_dir):
    """
    Makes plots of the raw data, best fit and starting guess.

    @param prob :: object holding the problem information
    @param best_fit :: data of the best fit (defined by lowest chisq)
    @param count :: number of times prob problem was passed through
    @param group_results_dir :: dir where results for the current group
                                are stored

    @returns :: None, plots are saved to /group_results_dir/support_pages/figures
    """

    figures_dir = create_dirs.figures(group_results_dir)

    raw_data = get_data_points(problem)
    make_data_plot(problem.name, raw_data, count, figures_dir)
    make_best_fit_plot(problem.name, raw_data, best_fit, count, figures_dir)
    make_starting_guess_plot(raw_data=raw_data,
                             problem=problem,
                             count=count,
                             figures_dir=figures_dir)



def get_data_points(problem):
    """
    Reads a mantid workspace and creates arrays of the x,y and error data.

    @param problem :: object holding the problem information

    @returns :: data object for plotting
    """

    xData = problem.data_x
    yData = problem.data_y
    eData = problem.data_e
    raw_data = data("Data", xData, yData, eData)
    raw_data.showError = True
    raw_data.linestyle = ''

    return raw_data


def make_data_plot(name, raw_data, count, figures_dir):
    """
    Creates a scatter plot of the raw data.

    @param name :: name of the problem related to the data
    @param raw_data :: the raw data stored into an object
    @param count :: number of times same name was passed through
    @param figures_dir :: dir where figures are stored

    @returns :: a figure of the raw data saved as a .png file
    """

    data_fig = plot()
    data_fig.add_data(raw_data)
    data_fig.labels['y'] = "Arbitrary units"
    data_fig.labels['x'] = "Time ($\mu s$)"
    data_fig.labels['title'] = name + " " + str(count)
    data_fig.title_size = 10
    data_fig.make_scatter_plot(figures_dir + os.sep + "Data Plot " + name +
                               " " + str(count) + ".png")


def make_best_fit_plot(name, raw_data, best_fit, count, figures_dir):
    """
    Creates a scatter plot of the raw data with the best fit
    superimposed.

    @param name :: name of the problem related to the data
    @param raw_data :: the raw data stored into an object
    @best_fit :: the best_fit data stored into a matrix
    @param count :: number of times same name was passed through
    @param figures_dir :: dir where figures are stored

    @returns :: a figure of the raw data with the best fit
                superimposed, saved as a .png file
    """

    fig = plot()
    fig.add_data(raw_data)
    best_fit.markers = ''
    best_fit.linestyle = '-'
    best_fit.colour = 'lime'
    best_fit.zorder = 2
    best_fit.linewidth = 1.5
    fig.add_data(best_fit)
    fig.labels['y'] = "Arbitrary units"
    fig.labels['x'] = "Time ($\mu s$)"
    fig.labels['title'] = name + " " + str(count)
    fig.title_size = 10
    figure_name = (figures_dir + os.sep + "Fit for " + name + " " +
                   str(count) + ".png")
    fig.make_scatter_plot(figure_name)


def make_starting_guess_plot(raw_data, problem, count, figures_dir):
    """
    Creates a scatter plot of the raw data with the starting guess
    superimposed. The starting guess is obtained by setting the
    MaxIterations option of the mantid fit software to 0.

    @param raw_data :: the raw data stored into an object
    @param problem :: object holding the problem information
    @param count :: number of times same name was passed through
    @param figures_dir :: dir where figures are stored

    @returns :: a figure of the raw data with the starting guess
                superimposed, saved as a .png file.
    """
    xData = problem.data_x
    yData = problem.eval_starting_params(0)
    startData = data("Start Guess", xData, yData)
    startData.colour = "red"
    startData.markers = ''
    startData.linestyle = "-"
    startData.linewidth = 1.5
    start_fig = plot()
    start_fig.add_data(raw_data)
    start_fig.add_data(startData)
    start_fig.labels['x'] = "Time ($\mu s$)"
    start_fig.labels['y'] = "Arbitrary units"
    start_fig.labels['title'] = problem.name + " " + str(count)
    start_fig.title_size = 10
    start_figure_name = (figures_dir + os.sep + "start for " + problem.name +
                         " " + str(count) + ".png")
    start_fig.make_scatter_plot(start_figure_name)
