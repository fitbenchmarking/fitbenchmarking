"""
Higher level functions that are used for plotting the raw data of a
problem, a best fit plot and a starting guess plot.
"""

from __future__ import (absolute_import, division, print_function)

import os
from fitbenchmarking.fitting.plotting.plot_helper import data, plot
from fitbenchmarking.utils import create_dirs


def make_plots(software, problem, data_struct, function, best_fit,
               previous_name, count, group_results_dir):
    """
    Makes plots of the raw data, best fit and starting guess.

    :param prob: Object holding the problem information
    :type problem: object
    :param data_struct: A structure in which the data to be fitted is
                        stored, can be e.g. mantid workspace, np array etc.
    :type data_struct: object
    :param function: The fitted function
    :type function: string
    :param best_fit: Data of the best fit (defined by lowest chisq)
    :type best_fit: object
    :param previous_name: Name of the previous problem
    :type previous_name: string
    :param count: Number of times prob problem was passed through
    :type count: int
    :param group_results_dir: Dir where results for the current group
                              are stored
    :type group_results_dir: string

    :return: The previous_name (plots are saved to /group_results_dir/support_pages/figures)
    :rtype: string
    """

    figures_dir = create_dirs.figures(group_results_dir)

    raw_data = get_data_points(problem)
    make_data_plot(problem.name, raw_data, count, figures_dir)
    make_best_fit_plot(problem.name, raw_data, best_fit, count, figures_dir)
    make_starting_guess_plot(software, raw_data, function, data_struct,
                             problem, count, figures_dir)

    return previous_name


def get_data_points(problem):
    """
    Reads a mantid workspace and creates arrays of the x,y and error data.

    :param problem: Object holding the problem information
    :type problem: object

    :return: Data object for plotting
    :rtype: plot_helper.data
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

    :param name: Name of the problem related to the data
    :type name: string
    :param raw_data: The raw data stored into an object
    :type raw_data: plot_helper.data
    :param count: Number of times same name was passed through
    :type count: int
    :param figures_dir: Dir where figures are stored
    :type figures_dir: string
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

    :param name: Name of the problem related to the data
    :type name: string
    :param raw_data: The raw data stored into an object
    :type raw_data: plot_helper.data
    :param best_fit: The best_fit data stored into a matrix
    :type best_fit: plot_helper.data
    :param count: Number of times same name was passed through
    :type count: int
    :param figures_dir: Dir where figures are stored
    :type figures_dir: string
    """

    fig = plot()
    fig.add_data(raw_data)
    best_fit.markers = ''
    best_fit.linestyle = '-'
    best_fit.colour = 'lime'
    best_fit.zorder = 2
    best_fit.linewidth = 1.5
    best_fit.order_data()
    fig.add_data(best_fit)
    fig.labels['y'] = "Arbitrary units"
    fig.labels['x'] = "Time ($\mu s$)"
    fig.labels['title'] = name + " " + str(count)
    fig.title_size = 10
    figure_name = (figures_dir + os.sep + "Fit for " + name + " " +
                   str(count) + ".png")
    fig.make_scatter_plot(figure_name)


def make_starting_guess_plot(software, raw_data, function, data_struct,
                             problem, count, figures_dir):
    """
    Creates a scatter plot of the raw data with the starting guess
    superimposed. The starting guess is obtained by setting the
    MaxIterations option of the mantid fit software to 0.

    :param software: The software used in the fit
    :type software: string
    :param raw_data: The raw data stored into an object
    :type raw_data: plot_helper.data
    :param function: The function that was fitted
    :type function: string
    :param data_struct: Structure containing problem data 
                        (e.g. mantid workspace/np array)
    :type data_struct: object
    :param problem: Object holding the problem information
    :type problem: object
    :param count: Number of times same name was passed through
    :type count: int
    :param figures_dir: Dir where figures are stored
    :type figures_dir: string
    """

    xData, yData =\
    get_start_guess_data(software, data_struct, function, problem)
    startData = data("Start Guess", xData, yData)
    startData.order_data()
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


def get_start_guess_data(software, data_struct, function, problem):
    """
    Gets the starting guess data for various softwares.

    :param software: The software used in fitting
    :type software: string
    :param data_struct: Structure containing problem data 
                        (e.g. mantid workspace/np array)
    :type data_struct: object
    :param function: The function that was fitted
    :type function: string
    :param problem: Object holding the problem information
    :type problem: object

    :return: Data describing the starting guess
    :rtype: plot_helper.data
    """
    if software == 'mantid':
        return get_mantid_starting_guess_data(data_struct, function, problem)
    elif software == 'scipy':
        return get_scipy_starting_guess_data(data_struct, function)
    elif software == 'sasview':
        return get_sasview_starting_guess_data(data_struct, problem, function)
        # return [0,0,0], [0,0,0]
    else:
        raise NameError("Sorry, that software is not supported.")

def get_scipy_starting_guess_data(data_struct, function):
    """
    Gets the scipy starting guess data

    :param data_struct: Data structure containing data for the problem
    :type data_struct: plot_helper.data
    :param function: The fitted function
    :type function: string

    :return: x and y data for the starting guess from scipy
    :rtype: 1D np.array
    
    """

    xData = data_struct[0]
    initial_params = function[1]

    yData = function[0](xData, *initial_params)
    return xData, yData


def get_mantid_starting_guess_data(wks_created, function, problem):
    """
    Gets the mantid starting guess data.

    :param wks_created: Mantid workspace that holds the data for the problem
    :type wks_created: mantid workspace
    :param function: The fitted function
    :type function: string
    :param problem: Object holding the problem information
    :type problem: object

    :return: x and y data for the starting guess from mantid
    :rtype: 1D np.array
    """

    import mantid.simpleapi as msapi

    fit_result = msapi.Fit(function, wks_created, Output='ws_fitting_test',
                           Minimizer='Levenberg-Marquardt',
                           CostFunction='Least squares',
                           IgnoreInvalidData=True,
                           StartX=problem.start_x, EndX=problem.end_x,
                           MaxIterations=0)

    tmp = msapi.ConvertToPointData(fit_result.OutputWorkspace)
    xData = tmp.readX(1)
    yData = tmp.readY(1)

    return xData, yData


def get_sasview_starting_guess_data(data_struct, problem, function):
    """
    Gets the SasView starting guess data.

    :param data_struct: Data structure containing data for the problem
                        in the SasView 1D data format (sasmodels.data.Data1D)
    :type data_struct: object
    :param function: The fitted function
    :type function: string

    :return: x and y data for the starting guess from sasview
    :rtype: 1D np.array
    """
    yData = problem.eval_f(data_struct.x, function[1])

    return data_struct.x, yData
