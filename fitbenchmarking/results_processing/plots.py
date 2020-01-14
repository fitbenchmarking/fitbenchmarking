"""
Higher level functions that are used for plotting the best fit plot and a starting guess plot.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


class Plot(object):
    """
    Class providing plotting functionality.
    """

    def __init__(self, problem, options, count, figures_dir):
        self.problem = problem
        self.options = options
        self.count = count
        self.figures_dir = figures_dir

        self.legend_location = "upper left"
        self.title_size = 10
        self.default_plot_options = {"linewidth": 3}
        self.data_plot_options = {"label": "Data",
                                  "zorder": 0,
                                  "color": "black",
                                  "marker": "x",
                                  "linestyle": ''}
        self.ini_guess_plot_options = {"label": "Starting Guess",
                                       "zorder": 1,
                                       "color": "#ff6699",
                                       "marker": "",
                                       "linestyle": '-'}
        self.best_fit_plot_options = {"zorder": 3,
                                      "color": '#6699ff',
                                      "marker": "",
                                      "linestyle": ':'}
        self.fit_plot_options = {"zorder": 2,
                                 "color": "#99ff66",
                                 "marker": "",
                                 "linestyle": '-'}

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.line_plot = None
        self.plot_data(self.options.use_errors,
                       self.data_plot_options)
        # reset line_plot as base data won't need updating
        self.line_plot = None

    def __del__(self):
        plt.close(self.fig)

    def format_plot(self):
        """
        Performs post plot processing to annotate the plot correctly
        """
        self.ax.set_xlabel(r"Time ($\mu s$)")
        self.ax.set_ylabel("Arbitrary units")
        self.ax.set_title(self.problem.name + " " + str(self.count),
                          fontsize=self.title_size)
        self.ax.legend(loc=self.legend_location)
        self.fig.set_tight_layout(True)

    def plot_data(self, errors, specific_options, x=None, y=None):
        """
        Plots the data given

        :param errors: boolean to say whether fit minimizer uses errors
        :type errors: bool
        :param default_options: dictionary containing default plot options
        :type default_options: dict
        :param specific_options: dictionary containing specific plot options,
                                 for example for the data plot
        :type specific_options: dict
        :param x: x values to be plotted
        :type x: np.array
        :param y: y values to be plotted
        :type y: np.array
        """
        if x is None:
            x = self.problem.data_x
        if y is None:
            y = self.problem.data_y
        temp_options = {}
        temp_options.update(self.default_plot_options)
        temp_options.update(specific_options)
        if errors:
            # Plot with errors
            self.ax.clear()
            self.ax.errorbar(x, y, yerr=self.problem.data_e,
                             **temp_options)
        else:
            # Plot without errors
            if self.line_plot is None:
                self.line_plot = self.ax.plot(x, y, **temp_options)[0]
            else:
                # Update line instead of recreating
                self.line_plot.set_data(x, y)
                # Update style
                for k, v in temp_options.items():
                    try:
                        getattr(self.line_plot, 'set_{}'.format(k))(v)
                    except AttributeError:
                        pass

                self.fig.canvas.draw()

    def plot_initial_guess(self):
        """
        Plots the initial guess along with the data
        """
        ini_guess = self.problem.starting_values[self.count - 1].values()
        self.plot_data(False,
                       self.ini_guess_plot_options,
                       y=self.problem.eval_f(ini_guess))
        self.format_plot()
        file = "start_for_{0}_{1}.png".format(self.problem.name, self.count)
        file_name = os.path.join(self.figures_dir, file)
        self.fig.savefig(file_name)
        return file

    def plot_best(self, minimizer, params):
        """
        Plots the fit along with the data using the "best_fit" style

        :param minimizer: name of the best fit minimizer
        :type minimizer: str
        :param params: fit parameters returned from the best fit minimizer
        :type params: list
        """
        plot_options_dict = self.best_fit_plot_options.copy()
        plot_options_dict['label'] = 'Best Fit ({})'.format(minimizer)
        line = self.line_plot
        self.line_plot = None
        self.plot_data(False,
                       plot_options_dict,
                       y=self.problem.eval_f(params))
        self.line_plot = line

    def plot_fit(self, minimizer, params):
        """
        Plots the fit along with the data

        :param minimizer: name of the fit minimizer
        :type minimizer: str
        :param params: fit parameters returned from the best fit minimizer
        :type params: list
        """
        plot_options_dict = self.fit_plot_options.copy()
        plot_options_dict['label'] = minimizer
        self.plot_data(False,
                       plot_options_dict,
                       y=self.problem.eval_f(params))
        self.format_plot()
        file = "{}_fit_for_{}_{}.png".format(
            minimizer, self.problem.name, self.count)
        file_name = os.path.join(self.figures_dir, file)
        self.fig.savefig(file_name)
        return file
