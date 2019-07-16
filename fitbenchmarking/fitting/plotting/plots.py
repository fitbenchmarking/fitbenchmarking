"""
Higher level functions that are used for plotting the raw data of a
problem, a best fit plot and a starting guess plot.
"""
# Copyright &copy; 2016 ISIS Rutherford Appleton Laboratory, NScD
# Oak Ridge National Laboratory & European Spallation Source
#
# This file is part of Mantid.
# Mantid is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Mantid is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# File change history is stored at:
# <https://github.com/mantidproject/fitbenchmarking>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>

from __future__ import (absolute_import, division, print_function)

import os
from fitting.plotting.plot_helper import *
from utils import create_dirs


def make_plots(software, problem, data_struct, function, best_fit,
               previous_name, count, group_results_dir):
    """
    Makes plots of the raw data, best fit and starting guess.

    @param prob :: object holding the problem information
    @param data_struct :: a structure in which the data to be fitted is
                          stored, can be e.g. mantid workspace, np array etc.
    @param function :: the fitted function
    @param best_fit :: data of the best fit (defined by lowest chisq)
    @param previous_name :: name of the previous problem
    @param count :: number of times prob problem was passed through
    @param group_results_dir :: dir where results for the current group
                                are stored

    @returns :: the previous_name (str) and the count (int), plots are
                saved to /group_results_dir/support_pages/figures
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

    data_fig=plot()
    data_fig.add_data(raw_data)
    data_fig.labels['y'] = "Arbitrary units"
    data_fig.labels['x'] = "Time ($\mu s$)"
    data_fig.labels['title'] = name + " " + str(count)
    data_fig.title_size=10
    data_fig.make_scatter_plot(figures_dir + os.sep + "Data Plot " + name +
                               " " + str(count)+".png")


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

    fig=plot()
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
    fig.title_size=10
    figure_name = (figures_dir + os.sep + "Fit for " + name + " " +
                   str(count) + ".png")
    fig.make_scatter_plot(figure_name)


def make_starting_guess_plot(software, raw_data, function, data_struct,
                             problem, count, figures_dir):
    """
    Creates a scatter plot of the raw data with the starting guess
    superimposed. The starting guess is obtained by setting the
    MaxIterations option of the mantid fit software to 0.

    @param raw_data :: the raw data stored into an object
    @param function :: string holding the function that was fitted
    @param data_struct :: mantid workspace containing problem data
    @param problem :: object holding the problem information
    @param count :: number of times same name was passed through
    @param figures_dir :: dir where figures are stored

    @returns :: a figure of the raw data with the starting guess
                superimposed, saved as a .png file.
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

    @param software ::
    """

    if software == 'mantid':
        return get_mantid_starting_guess_data(data_struct, function, problem)
    elif software == 'scipy':
        return get_scipy_starting_guess_data(data_struct, function)
    else:
        raise NameError("Sorry, that software is not supported.")

def get_scipy_starting_guess_data(data_struct, function):
    """
    Gets the scipy starting guess data

    @param data_struct :: data structure containing data for the problem
    @param function :: the fitted function

    @returns :: data describing the starting guess obtained by passing
                the x values to the fitted function
    """

    xData = data_struct[0]
    initial_params = function[1]

    yData = function[0](xData,*initial_params)
    return xData, yData


def get_mantid_starting_guess_data(wks_created, function, problem):
    """
    Gets the mantid starting guess data.

    @param wks_created :: mantid workspace that holds the data for the problem
    @param function :: the fitted function
    @param problem :: object holding the problem information

    @returns :: data describing the starting guess obtained by using the
                fitting software inside mantid
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
