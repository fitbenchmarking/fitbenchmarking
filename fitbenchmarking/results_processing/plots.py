"""
Higher level functions that are used for plotting the fit plot and a starting
guess plot.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


class Plot(object):
    """
    Class providing plotting functionality.
    """

    def __init__(self, best_result, options, figures_dir):
        self.problem = best_result.problem
        self.options = options

        self.result = best_result

        self.figures_dir = figures_dir

        self.legend_location = "upper left"
        self.title_size = 10

        # These define the styles of the 4 types of plot
        self.data_plot_options = {"label": "Data",
                                  "zorder": 0,
                                  "color": "black",
                                  "marker": "x",
                                  "linestyle": '',
                                  "linewidth": 1}
        self.ini_guess_plot_options = {"label": "Starting Guess",
                                       "zorder": 1,
                                       "color": "#ff6699",
                                       "marker": "",
                                       "linestyle": '-',
                                       "linewidth": 3}
        self.best_fit_plot_options = {"zorder": 3,
                                      "color": '#6699ff',
                                      "marker": "",
                                      "linestyle": ':',
                                      "linewidth": 3}
        self.fit_plot_options = {"zorder": 2,
                                 "color": "#99ff66",
                                 "marker": "",
                                 "linestyle": '-',
                                 "linewidth": 3}

        # Create a single reusable plot containing the problem data.
        # We store a line here, which is updated to change the graph where we
        # know the rest of the graph is untouched between plots.
        # This is more efficient that the alternative of creating a new graph
        # every time.
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.line_plot = None
        # Plot the data that functions were fitted to
        self.plot_data(self.options.use_errors,
                       self.data_plot_options)
        # reset line_plot as base data won't need updating
        self.line_plot = None

        # Store sorted x values for plotting
        self.x = self.result.data_x[self.result.sorted_index]

    def __del__(self):
        """
        Close the matplotlib figure
        """
        plt.close(self.fig)

    def format_plot(self):
        """
        Performs post plot processing to annotate the plot correctly
        """
        self.ax.set_xlabel(r"Time ($\mu s$)")
        self.ax.set_ylabel("Arbitrary units")
        self.ax.set_title(self.result.name,
                          fontsize=self.title_size)
        self.ax.legend(loc=self.legend_location)
        self.fig.set_tight_layout(True)

    def plot_data(self, errors, plot_options, x=None, y=None):
        """
        Plots the data given

        :param errors: whether fit minimizer uses errors
        :type errors: bool
        :param plot_options: Values for style of the data to plot,
                                 for example color and zorder
        :type plot_options: dict
        :param x: x values to be plotted
        :type x: np.array
        :param y: y values to be plotted
        :type y: np.array
        """
        if x is None:
            x = self.result.data_x
        if y is None:
            y = self.result.data_y
        if errors:
            # Plot with errors
            self.ax.clear()
            self.ax.errorbar(x, y, yerr=self.result.data_e,
                             **plot_options)
        else:
            # Plot without errors
            if self.line_plot is None:
                # Create a new line and store
                self.line_plot = self.ax.plot(x, y, **plot_options)[0]
            else:
                # Update line instead of recreating
                self.line_plot.set_data(x, y)
                # Update style
                for k, v in plot_options.items():
                    try:
                        getattr(self.line_plot, 'set_{}'.format(k))(v)
                    except AttributeError:
                        pass

                self.fig.canvas.draw()

    def plot_initial_guess(self):
        """
        Plots the initial guess along with the data and stores in a file

        :return: path to the saved file
        :rtype: str
        """
        # Parse which starting values to use from result name
        start_index = self.result.name.partition('Start')[2].split(',')[0]
        if start_index:
            start_index = int(start_index.strip())
        else:
            start_index = 1

        ini_guess = self.problem.starting_values[start_index - 1].values()
        self.plot_data(errors=False,
                       plot_options=self.ini_guess_plot_options,
                       x=self.x,
                       y=self.problem.eval_f(list(ini_guess), self.x))
        self.format_plot()
        file = "start_for_{0}.png".format(self.result.sanitised_name)
        file_name = os.path.join(self.figures_dir, file)
        self.fig.savefig(file_name)
        return file

    def plot_best(self, minimizer, params):
        """
        Plots the fit along with the data using the "best_fit" style
        and saves to a file

        :param minimizer: name of the best fit minimizer
        :type minimizer: str
        :param params: fit parameters returned from the best fit minimizer
        :type params: list

        :return: path to the saved file
        :rtype: str
        """
        label = 'Best Fit ({})'.format(minimizer)

        # Plot line and save.
        # This should have the style of fit plot options and the colour of
        # best fit plot options.
        # Then the plot should be saved and updated to use only best fit style
        # for future plots.
        plot_options_dict = self.fit_plot_options.copy()
        plot_options_dict['label'] = label
        plot_options_dict['color'] = self.best_fit_plot_options['color']

        y = self.problem.eval_f(params, self.x)
        self.plot_data(errors=False,
                       plot_options=plot_options_dict,
                       y=y)
        self.format_plot()
        file = "{}_fit_for_{}.png".format(self.result.sanitised_min_name,
                                          self.result.sanitised_name)
        file_name = os.path.join(self.figures_dir, file)
        self.fig.savefig(file_name)

        # Update to correct linestyle
        plot_options_dict = self.best_fit_plot_options.copy()
        plot_options_dict['label'] = label
        self.plot_data(errors=False,
                       plot_options=plot_options_dict,
                       x=self.x,
                       y=y)

        # Make sure line wont be replaced by resetting line_plot
        self.line_plot = None
        return file

    def plot_fit(self, minimizer, params):
        """
        Updates self.line to show the fit using the passed in params.
        If self.line is empty it will create a new line.
        Stores the plot in a file

        :param minimizer: name of the fit minimizer
        :type minimizer: str
        :param params: fit parameters returned from the best fit minimizer
        :type params: list

        :return: path to the saved file
        :rtype: str
        """
        plot_options_dict = self.fit_plot_options.copy()
        plot_options_dict['label'] = minimizer

        self.plot_data(errors=False,
                       plot_options=plot_options_dict,
                       x=self.x,
                       y=self.problem.eval_f(params, self.x))
        self.format_plot()
        file = "{}_fit_for_{}.png".format(self.result.sanitised_min_name,
                                          self.result.sanitised_name)
        file_name = os.path.join(self.figures_dir, file)
        self.fig.savefig(file_name)
        return file
