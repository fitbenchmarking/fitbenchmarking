"""
Higher level function that are used for plotting the raw data of a
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
import mantid.simpleapi as msapi
from plotHelper import *


def make_plots(prob, wks, function, best_fit, previous_name, count,
               group_results_dir):
    """
    Makes plots of the raw data, best fit and starting guess.

    @param prob :: object holding the problem information
    @param wks :: workspace holding the problem data
    @param function :: the fitted function
    @param best_fit :: data of the best fit (defined by lowest chisq)
    @param previous_name :: name of the previous problem
    @param count :: number of times prob problem was passed through
    @param group_results_dir :: dir where results for the current group
                                are stored

    @returns :: the previous_name and the count, plots are saved to
                /group_results_dir/support_pages/figures
    """

    figures_dir = setup_dirs(group_results_dir)
    previous_name, count = problem_count(prob, previous_name, count)

    raw_data = get_data_points(wks)
    make_data_plot(prob.name, raw_data, count, figures_dir)
    make_best_fit_plot(prob.name, raw_data, best_fit, count, figures_dir)
    make_starting_guess_plot(raw_data, function, wks, prob, count,
                             figures_dir)

    return previous_name, count


def get_data_points(wks):
    """
    Reads a mantid workspace and creates arrays of the x,y and error data.

    @param wks :: mantid workspace containing problem data

    @returns :: arrays of x,y and error data.
    """

    tmp = msapi.ConvertToPointData(wks)
    xData = tmp.readX(0)
    yData = tmp.readY(0)
    eData = tmp.readE(0)
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
    best_fit.markers=''
    best_fit.linestyle='-'
    best_fit.colour='green'
    best_fit.order_data()
    fig.add_data(best_fit)
    fig.labels['y'] = "Arbitrary units"
    fig.labels['x'] = "Time ($\mu s$)"
    fig.labels['title'] = name + " " + str(count)
    fig.title_size=10
    figure_name = (figures_dir + os.sep + "Fit for " + name + " " +
                   str(count) + ".png")
    fig.make_scatter_plot(figure_name)


def make_starting_guess_plot(raw_data, function, wks, prob, count,
                             figures_dir):
    """
    Creates a scatter plot of the raw data with the starting guess
    superimposed. The starting guess is obtained by setting the
    MaxIterations option of the mantid fit algorithm to 0.

    @param raw_data :: the raw data stored into an object
    @param function :: string holding the function that was fitted
    @param wks :: mantid workspace containing problem data
    @param prob :: object holding the problem information
    @param count :: number of times same name was passed through
    @param figures_dir :: dir where figures are stored

    @returns :: a figure of the raw data with the starting guess
                superimosed, saved as a .png file.
    """

    fit_result = msapi.Fit(function, wks, Output='ws_fitting_test',
                           Minimizer='Levenberg-Marquardt',
                           CostFunction='Least squares',IgnoreInvalidData=True,
                           StartX=prob.start_x, EndX=prob.end_x,
                           MaxIterations=0)

    tmp = msapi.ConvertToPointData(fit_result.OutputWorkspace)
    xData = tmp.readX(1)
    yData = tmp.readY(1)
    startData = data("Start Guess", xData, yData)
    startData.order_data()
    startData.colour = "blue"
    startData.markers = ''
    startData.linestyle = "-"
    start_fig = plot()
    start_fig.add_data(raw_data)
    start_fig.add_data(startData)
    start_fig.labels['x'] = "Time ($\mu s$)"
    start_fig.labels['y'] = "Arbitrary units"
    start_fig.labels['title'] = prob.name + " " + str(count)
    start_fig.title_size = 10
    start_figure_name = (figures_dir + os.sep + "start for " + prob.name +
                         " " + str(count) + ".png")
    start_fig.make_scatter_plot(start_figure_name)


def problem_count(prob, previous_name, count):
    """
    Helper function that counts how many times the name of the problem
    comes up consecutively.

    @param prob :: object holding the problem information
    @param previous_name :: name of the previous problem
    @param count :: number of times same name was passed through

    @returns :: the new/same previous name and the number of times it
                has seen that name in a row.
    """

    if prob.name == previous_name:
        count += 1
    else:
        count = 1
        previous_name = prob.name

    return previous_name, count


def setup_dirs(group_results_dir):
    """
    Sets up the directories in which the figures will go.

    @param group_results_dir :: dir where results for the current group
                                are stored

    @returns :: the path to the figures directory, of the form
                /group_results_dir/support_pages/figures
    """

    support_pages_dir = os.path.join(group_results_dir, "tables",
                                     "support_pages")
    if not os.path.exists(support_pages_dir):
            os.makedirs(support_pages_dir)
    figures_dir = os.path.join(support_pages_dir, "figures")
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)

    return figures_dir
