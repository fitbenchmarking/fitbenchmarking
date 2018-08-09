"""
Functions for plotting the fits.
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

import mantid.simpleapi as msapi
from plotHelper import *


def make_plots(prob, wks, function, best_fit, previous_name, count,
              group_results_dir):
    """
    """

    setup_dirs(group_results_dir)
    previous_name, count = problem_count(prob, previous_name, count)

    raw_data = get_data_points(wks)
    make_data_plot(prob.name, raw_data, count, figures_dir)
    make_best_fit_plot(prob.name, raw_data, best_fit, count, figures_dir)
    make_starting_guess_plot(raw_data, function, wks, prob, count,
                             figures_dir)

    return previous_name, count


def get_data_points(wks):
    """
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
    """

    if prob.name == previous_name:
        count += 1
    else:
        count = 1
        previous_name = prob.name

    return previous_name, count


def setup_dirs(visuals_dir):
    """
    """

    support_pages_dir = os.path.join(visuals_dir, "tables", "support_pages")
    if not os.path.exists(support_pages_dir):
            os.makedirs(support_pages_dir)
    figures_dir = os.path.join(support_pages_dir, "figures")
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)
