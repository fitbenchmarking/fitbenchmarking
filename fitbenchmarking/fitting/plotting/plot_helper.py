"""
Utility classes and methods used for plotting the figures used in
the fitbenchmarking tool.
"""

from __future__ import (absolute_import, division, print_function)

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import copy
from fitbenchmarking.utils.logging_setup import logger


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
            self.name = 'none'
            self.x = [0.0, 0.0, 0.0]
            self.y = [0.0, 0.0, 0.0]
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


class plot(data):
    """
    Class holding the information required for a scatter plot
    of some provided.
    """

    def __init__(self):
        self.data = []
        self.labels = {"x": "xlabel", "y": "ylabel", "title": "title"}
        self.legend = "upper left"
        self.insert = None
        self.title_size = 20

    def add_data(self, inputData):
        """
        Adds the data to the main plot.
        @param inputData :: the data to add to the plot
        """
        self.data.append(inputData)

    def make_scatter_plot(self, save=""):
        """
        Creates a scatter plot.
        @param save:: the name of the file to save to
                      the default is not to save
        """

        plt.figure()
        for data in self.data:
            self.check_and_make_plot(data)

        self.set_plot_misc()
        self.save_plot(save)


        plt.close()

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
        if save == "":
            plt.show()
        else:
            output_file = save.replace(",", "")
            output_file = output_file.replace(" ", "_")
            logger.info("Saved " + os.path.basename(output_file) + " to " +
                        output_file[output_file.find("fitbenchmarking"):])
        plt.savefig(output_file.replace(" ", "_"))
