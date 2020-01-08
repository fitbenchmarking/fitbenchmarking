"""
Higher level functions that are used for plotting the best fit plot and a starting guess plot.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from fitbenchmarking.utils import create_dirs


class Plot(object):
    """
    Class providing plotting functionality.
    """

    def __init__(self, problem, options, count, group_results_dir):
        self.problem = problem
        self.options = options
        self.count = count
        self.group_results_dir = group_results_dir
        self.figures_dir = create_dirs.figures(group_results_dir)

        self.legend_location = "upper left"
        self.title_size = 10
        self.labels = None
        self.default_plot_options = \
            {"zorder": 2, "linewidth": 1.5}
        self.data_plot_options = \
            {"color": "black", "marker": "x", "linestyle": '--'}
        self.ini_guess_plot_options = \
            {"color": "red", "marker": "", "linestyle": '-'}
        self.best_fit_plot_options = \
            {"color": "lime", "marker": "", "linestyle": '-'}

    def format_plot(self):
        """
        Performs post plot processing to annotate the plot correctly
        """
        plt.xlabel("Time ($\mu s$)")
        plt.ylabel("Arbitrary units")
        plt.title(self.problem.name + " " + str(self.count),
                  fontsize=self.title_size)
        plt.legend(labels=self.labels, loc=self.legend_location)
        plt.tight_layout()

    def plot_data(self, errors, default_options, specific_options, x=None, y=None):
        """
        Plots the data given

        :param errors: boolean to say whether fit minimizer uses errors
        :type errors: bool
        :param x: x values to be plotted
        :type x: np.array
        :param y: y values to be plotted
        :type y: np.array
        """
        if x is None:
            x = self.problem.data_x
        if y is None:
            y = self.problem.data_y
        # print(default_options, specific_options)
        default_options.update(specific_options)
        if errors:
            # Plot with errors
            plt.errorbar(x, y, yerr=self.problem.data_e,
                         **default_options)
        else:
                # Plot without errors
            plt.plot(x, y, **default_options)

    def plot_initial_guess(self):
        """
        Plots the initial guess along with the data
        """
        self.labels = ["Starting Guess", "Data"]
        ini_guess = self.problem.starting_values[self.count - 1].values()
        self.plot_data(self.options.use_errors,
                       self.default_plot_options,
                       self.data_plot_options)
        self.plot_data(False, self.default_plot_options,
                       self.ini_guess_plot_options,
                       y=self.problem.eval_f(ini_guess))
        self.format_plot()
        file_name = "{0}/start_for_{1}_{2}.png".format(
            self.figures_dir, self.problem.name, self.count)
        plt.savefig(file_name)
        plt.close()

    def plot_best_fit(self, minimizer, params):
        """
        Plots the best fit along with the data

        :param best_fit: dictionary containing the 'name' and 'value' of
                         the best fit as the keys
        :type best_fit: dict
        """

        self.labels = [minimizer, "Data"]
        self.plot_data(self.options.use_errors,
                       self.default_plot_options,
                       self.data_plot_options)
        self.plot_data(False, self.default_plot_options,
                       self.best_fit_plot_options,
                       y=self.problem.eval_f(params))
        self.format_plot()
        file_name = "{0}/Fit_for_{1}_{2}.png".format(
            self.figures_dir, self.problem.name, self.count)
        plt.savefig(file_name)
        plt.close()
