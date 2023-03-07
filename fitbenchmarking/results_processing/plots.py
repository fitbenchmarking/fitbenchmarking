"""
Higher level functions that are used for plotting the fit plot and a starting
guess plot.
"""
import os

import matplotlib
import numpy as np

from fitbenchmarking.utils.exceptions import PlottingError

matplotlib.use('Agg')
# pylint: disable=ungrouped-imports,wrong-import-position,wrong-import-order
import matplotlib.pyplot as plt  # noqa: E402


class Plot:
    """
    Class providing plotting functionality.
    """
    # These define the styles of the 4 types of plot
    data_plot_options = {"label": "Data",
                         "zorder": 0,
                         "color": "black",
                         "marker": "x",
                         "linestyle": '',
                         "linewidth": 1}
    ini_guess_plot_options = {"label": "Starting Guess",
                              "zorder": 1,
                              "color": "#ff6699",
                              "marker": "",
                              "linestyle": '-',
                              "linewidth": 3}
    best_fit_plot_options = {"zorder": 3,
                             "color": '#6699ff',
                             "marker": "",
                             "linestyle": ':',
                             "linewidth": 3}
    fit_plot_options = {"zorder": 2,
                        "color": "#99ff66",
                        "marker": "",
                        "linestyle": '-',
                        "linewidth": 3}
    summary_best_plot_options = {"zorder": 2,
                                 "marker": "",
                                 "linestyle": '-',
                                 "linewidth": 2}
    summary_plot_options = {"zorder": 1,
                            "marker": "",
                            "linestyle": '-',
                            "linewidth": 1,
                            "alpha": 0.5, }

    def __init__(self, best_result, options, figures_dir):
        self.plots_failed = True
        self.result = best_result

        if self.result.multivariate:
            raise PlottingError(
                'Plots cannot be generated for multivariate problems')

        if self.result.problem_format == 'horace':
            raise PlottingError(
                'Plots cannot be generated for Horace problems')
        self.plots_failed = False

        self.options = options

        self.figures_dir = figures_dir

        self.legend_location = "upper left"
        self.title_size = 10

        # Create a single reusable plot containing the problem data.
        # We store a line here, which is updated to change the graph where we
        # know the rest of the graph is untouched between plots.
        # This is more efficient that the alternative of creating a new graph
        # every time.
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.line_plot = None

        use_errors = bool(self.options.cost_func_type == "weighted_nlls")
        # Plot the data that functions were fitted to
        self.plot_data(use_errors,
                       self.data_plot_options)
        # reset line_plot as base data won't need updating
        self.line_plot = None

        # Store sorted x values for plotting
        self.x = self.result.data_x[self.result.sorted_index]

    def __del__(self):
        """
        Close the matplotlib figure
        """
        if not self.plots_failed:
            plt.close(self.fig)

    def format_plot(self):
        """
        Performs post plot processing to annotate the plot correctly
        """
        # log scale
        if self.result.plot_scale == "loglog":
            self.ax.set_xscale("log", nonpositive='clip')
            self.ax.set_yscale("log", nonpositive='clip')
        elif self.result.plot_scale == "logy":
            self.ax.set_yscale("log", nonpositive='clip')
        elif self.result.plot_scale == "logx":
            self.ax.set_xscale("log", nonpositive='clip')

        # linear scale if otherwise
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
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
                        getattr(self.line_plot, f'set_{k}')(v)
                    except AttributeError:
                        pass

                self.fig.canvas.draw()

    def plot_initial_guess(self):
        """
        Plots the initial guess along with the data and stores in a file

        :return: path to the saved file
        :rtype: str
        """
        self.plot_data(errors=False,
                       plot_options=self.ini_guess_plot_options,
                       x=self.x,
                       y=self.result.ini_y[self.result.sorted_index])
        self.format_plot()
        file = "start_for_{0}.png".format(self.result.sanitised_name)
        file_name = os.path.join(self.figures_dir, file)
        self.fig.savefig(file_name)
        return file

    def plot_best(self, result):
        """
        Plots the fit along with the data using the "best_fit" style
        and saves to a file

        :param result: The result to plot
        :type result: FittingResult

        :return: path to the saved file
        :rtype: str
        """
        label = f'Best Fit ({result.modified_minimizer_name(True)})'

        # Plot line and save.
        # This should have the style of fit plot options and the colour of
        # best fit plot options.
        # Then the plot should be saved and updated to use only best fit style
        # for future plots.
        plot_options_dict = self.fit_plot_options.copy()
        plot_options_dict['label'] = label
        plot_options_dict['color'] = self.best_fit_plot_options['color']

        y = result.fin_y[result.sorted_index]
        self.plot_data(errors=False,
                       plot_options=plot_options_dict,
                       y=y)
        self.format_plot()
        file = f"{result.sanitised_min_name(True)}_fit_for_" \
               f"{self.result.costfun_tag}_{self.result.sanitised_name}.png"
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

    def plot_fit(self, result):
        """
        Updates self.line to show the fit using the passed in params.
        If self.line is empty it will create a new line.
        Stores the plot in a file

        :param result: The result to plot
        :type result: FittingResult

        :return: path to the saved file
        :rtype: str
        """
        plot_options_dict = self.fit_plot_options.copy()
        plot_options_dict['label'] = result.modified_minimizer_name(True)

        self.plot_data(errors=False,
                       plot_options=plot_options_dict,
                       x=self.x,
                       y=result.fin_y[result.sorted_index])
        self.format_plot()
        file = f"{result.sanitised_min_name(True)}_fit_for_"\
               f"{self.result.costfun_tag}_{self.result.sanitised_name}.png"
        file_name = os.path.join(self.figures_dir, file)
        self.fig.savefig(file_name)
        return file

    @classmethod
    def plot_summary(cls, categories, title, options, figures_dir):
        """
        Create a comparison plot showing all fits from the results with the
        best for each category highlighted.

        :param categories: The results to plot sorted into colour groups
        :type categories: dict[str, list[FittingResults]]
        :param title: A title for the graph
        :type title: str
        :param options: The options for the run
        :type options: utils.options.Options
        :param figures_dir: The directory to save the figures in
        :type figures_dir: str

        :return: The path to the new plot
        :rtype: str
        """
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        # Get a colour for each category
        cmap = plt.cm.get_cmap('rainbow')
        col_vals = np.linspace(0, 1, len(categories))
        colours = iter(cmap(col_vals))

        first_result = next(iter(categories.values()))[0]

        # Plot data
        if "weighted_nlls" in options.cost_func_type:
            ax.errorbar(first_result.data_x,
                        first_result.data_y,
                        yerr=first_result.data_e,
                        **cls.data_plot_options)
        else:
            ax.plot(first_result.data_x,
                    first_result.data_y,
                    **cls.data_plot_options)

        # Setup x for rest of plots
        x = first_result.data_x
        x = first_result.data_x[first_result.sorted_index]

        for (key, results), colour in zip(categories.items(), colours):
            # Plot category
            for result in results:
                if result.params is not None:
                    y = result.fin_y[result.sorted_index]
                    plot_options = cls.summary_best_plot_options \
                        if result.is_best_fit else cls.summary_plot_options
                    plot_options['color'] = colour
                    plot_options['label'] = key if result.is_best_fit else ''

                    ax.plot(x, y, **plot_options)
                    # log scale
                    if result.plot_scale == "loglog":
                        ax.set_xscale("log", nonpositive='clip')
                        ax.set_yscale("log", nonpositive='clip')
                    elif result.plot_scale == "logy":
                        ax.set_yscale("log", nonpositive='clip')
                    elif result.plot_scale == "logx":
                        ax.set_xscale("log", nonpositive='clip')
                    ax.set_xlabel("X")
                    ax.set_ylabel("Y")
                    ax.set_title(title,
                                 fontsize=10)
                    ax.legend(loc="upper left")
                    fig.set_tight_layout(True)

        fname = f'summary_plot_for_{first_result.sanitised_name}.png'
        fig.savefig(os.path.join(figures_dir, fname))
        plt.close(fig)
        return fname
