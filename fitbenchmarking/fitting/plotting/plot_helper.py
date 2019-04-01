"""
Utility classes and methods used for plotting the figures used in
the fitbenchmarking tool.
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
# File change history is stored at: <https://github.com/mantidproject/mantid>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>
from __future__ import (absolute_import, division, print_function)

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import copy
from utils.logging_setup import logger


class data:
    """
    Holds all the data that is used in the plotting process.
    """

    def __init__(self, name=None, x=[], y=[], E=[]):
        """
        Creates a data object.
        @param x :: the x data
        @param y :: the y data
        @param E :: the (y) errors
        """

        if name is not None:
            self.name = name
            self.x = copy.copy(x)
            self.y = copy.copy(y)
        else:
            self.name ='none'
            self.x = [0.0,0.0,0.0]
            self.y = [0.0,0.0,0.0]
        if(len(E) == 0):
            self.E = np.zeros(len(self.x))
        else:
            self.E = copy.copy(E)
        self.showError = False
        self.markers = "x"
        self.colour = "k"
        self.linestyle = '--'
        self.z_order = 1
        self.linewidth = 1


    def order_data(self):
        """
        Ensures that the data is in ascending order in x.
        Prevents line plots looping back on themselves.
        """

        xData=self.x
        yData=self.y
        eData=self.E

        for j in range(0,len(yData)):
            for k in range(0,len(xData)-1):
                if xData[k] > xData[k+1]:
                    xData[k+1], xData[k] = xData[k], xData[k+1]
                    yData[k+1], yData[k] = yData[k], yData[k+1]
                    eData[k+1], eData[k] = eData[k], eData[k+1]


class plot(data):
    """
    Class holding the information required for a scatter plot
    of some provided.
    """

    def __init__(self):
        self.data = []
        self.labels = {'x':"xlabel", 'y':'ylabel', "title":"title"}
        self.legend = "upper left"
        self.insert = None
        self.title_size=20


    def add_data(self,inputData):
        """
        Adds the data to the main plot.
        @param inputData :: the data to add to the plot
        """
        self.data.append(inputData)


    def make_scatter_plot(self,save=""):
        """
        Creates a scatter plot.
        @param save:: the name of the file to save to
                      the default is not to save
        """

        plt.figure()
        self.set_plot_misc()
        for data in self.data:
            self.check_and_make_plot(data)

        self.save_plot(save)

    def set_plot_misc(self):
        """
        Add the title, x/y labels and legend to the plot.
        """
        plt.xlabel(self.labels["x"])
        plt.ylabel(self.labels["y"])
        plt.title(self.labels["title"], fontsize=self.title_size)
        plt.legend(loc=self.legend)

        # Customize the layout of the plot.
        plt.tight_layout()

    def check_and_make_plot(self, data):
        """
        Check if the data used for plotting is legitimate and
        do the plotting.

        @param data :: object that holds all the relevant data
        """
        if len(data.x) == len(data.y):
            self.make_plot(data)
        else:
            logger.error("Data " + data.name + " contains data" +
                         " of unequal lengths ", len(data.x), len(data.y))

    @staticmethod
    def make_plot(data):
        """
        Make a plot of the data, with or without errors,
        as specified.

        @param data :: object that holds all the relevant data
        """

        if data.showError:
            # Plot with errors
            plt.errorbar(data.x, data.y, yerr=data.E, label=data.name,
                         marker=data.markers, color=data.colour,
                         linestyle=data.linestyle, markersize=8,
                         zorder=data.z_order, linewidth=data.linewidth)
        else:
            # Plot without errors
            plt.plot(data.x, data.y, label=data.name,
                     marker=data.markers, color=data.colour,
                     linestyle=data.linestyle, markersize=8,
                     zorder=data.z_order, linewidth=data.linewidth)

    @staticmethod
    def save_plot(save):
        """
        Save the plot to a .png file or just display it in the
        console if that option is available.
        """
        if save=="":
            plt.show()
        else:
            output_file = save.replace(",", "")
            logger.info("saving to " + output_file.replace(" ", "_"))
        plt.savefig(output_file.replace(" ", "_"))

