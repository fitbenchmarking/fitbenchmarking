"""
Higher level functions that are used for plotting the fit plot and a starting
guess plot.
"""
import os

import numpy as np
import plotly.colors as ptly_colors
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot as offline_plot

from fitbenchmarking.utils.exceptions import PlottingError


class Plot:
    """
    Class providing plotting functionality.
    """
    data_marker = {"symbol": "x",
                   "color": "black"}
    best_fit_line = {"dash": "dot",
                     "color": '#6699ff'}
    legend_options = {"yanchor": "top",
                      "y": 0.99,
                      "xanchor": "left",
                      "x": 0.01,
                      "bgcolor": 'rgba(0,0,0,0.1)'}
    summary_best_plot_line = {"width": 2}
    summary_plot_line = {"width": 1}

    def __init__(self, best_result, options, figures_dir):
        self.result = best_result

        self.plots_failed = True
        if self.result.multivariate:
            raise PlottingError(
                'Plots cannot be generated for multivariate problems')
        if self.result.problem_format == 'horace':
            raise PlottingError(
                'Plots cannot be generated for Horace problems')
        self.plots_failed = False

        self.options = options

        self.figures_dir = figures_dir

    def plot_initial_guess(self, df):
        """
        Plots the initial guess along with the data and stores in a file

        :param df: A dataframe holding the data
        :type df: Pandas dataframe

        :return: path to the saved file
        :rtype: str
        """

        # Plotly implementation below
        fig = px.line(df[df["minimizer"] == 'Starting Guess'],
                      x="x",
                      y="y",
                      color="minimizer",
                      title=self.result.name,
                      markers=True)
        # add the raw data as a scatter plot
        fig.add_trace(go.Scatter(
            x=df[df["minimizer"] == 'Data']["x"].to_list(),
            y=df[df["minimizer"] == 'Data']["y"].to_list(),
            mode='markers',
            name='Data',
            marker=self.data_marker))
        fig.update_layout(legend=self.legend_options)

        if self.result.plot_scale in ["loglog", "logx"]:
            fig.update_xaxes(type="log")
        if self.result.plot_scale in ["loglog", "logy"]:
            fig.update_yaxes(type="log")

        htmlfile = f"start_for_{self.result.sanitised_name}.html"
        html_file_name = os.path.join(self.figures_dir, htmlfile)

        offline_plot(
            fig,
            filename=html_file_name,
            auto_open=False
        )

        return htmlfile

    @staticmethod
    def best_filename(result):
        """
        Returns the filename of the best fit plot.

        :param result: The result to plot
        :type result: FittingResult

        :return: path to the saved file
        :rtype: str
        """
        htmlfile = f"{result.sanitised_min_name(True)}_fit_for_"\
            f"{result.costfun_tag}_{result.sanitised_name}.html"
        return htmlfile

    def plotly_fit(self, df):
        """
        Uses plotly to plot the calculated fit, along with the best fit.
        Stores the plot in a file

        :param df: A dataframe holding the data
        :type df: Pandas dataframe

        :return: path to the saved file
        :rtype: str
        """
        # Plotly implementation below
        htmlfiles = {}
        x_best = df[df["best"]]["x"].to_list()
        y_best = df[df["best"]]["y"].to_list()
        x_data = df[df["minimizer"] == 'Data']["x"].to_list()
        y_data = df[df["minimizer"] == 'Data']["y"].to_list()

        for minimizer in df['minimizer'].unique():
            if minimizer not in ["Data", "Starting Guess"]:
                fig = px.line(df[df["minimizer"] == minimizer],
                              x="x",
                              y="y",
                              color="minimizer",
                              title=self.result.name,
                              markers=True)
                if not df[df["minimizer"] == minimizer]["best"].any():
                    # add the best plot
                    name = 'Best Fit (' + \
                        f'{df[df["best"]]["minimizer"].unique()[0]})'
                    fig.add_trace(
                        go.Scatter(x=x_best,
                                   y=y_best,
                                   mode='lines',
                                   name=name,
                                   line=self.best_fit_line))
                # add the raw data as a scatter plot
                fig.add_trace(
                    go.Scatter(
                        x=x_data,
                        y=y_data,
                        mode='markers',
                        name='Data',
                        marker=self.data_marker))
                fig.update_layout(legend=self.legend_options)

                if self.result.plot_scale in ["loglog", "logx"]:
                    fig.update_xaxes(type="log")
                if self.result.plot_scale in ["loglog", "logy"]:
                    fig.update_yaxes(type="log")

                htmlfile = f"{minimizer}_fit_for_{self.result.costfun_tag}" \
                    f"_{self.result.sanitised_name}.html"

                html_file_name = os.path.join(self.figures_dir, htmlfile)

                offline_plot(
                    fig,
                    filename=html_file_name,
                    auto_open=False
                )
                htmlfiles[minimizer] = htmlfile

        return htmlfiles

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

        col_vals = np.linspace(0, 1, len(categories))
        plotly_colours = ptly_colors.sample_colorscale(
            ptly_colors.sequential.Rainbow,
            samplepoints=col_vals)

        first_result = next(iter(categories.values()))[0]

        plotlyfig = go.Figure()

#        # Plot data
        if "weighted_nlls" in options.cost_func_type:
            error_y = dict(
                type='data',
                array=first_result.data_e,
                color='rgb(0,0,0,0.8)',
                thickness=1,
                visible=True)
        else:
            error_y = None
        plotlyfig.add_trace(go.Scatter(x=first_result.data_x,
                                       y=first_result.data_y,
                                       error_y=error_y,
                                       mode='markers',
                                       name='Data',
                                       marker=cls.data_marker))

        for (key, results), colour in zip(categories.items(), plotly_colours):
            # Plot category
            for result in results:
                if result.params is not None:
                    line = cls.summary_best_plot_line \
                        if result.is_best_fit else cls.summary_plot_line

                    line["color"] = colour
                    label = key if result.is_best_fit else ''
                    if result.is_best_fit:
                        line = cls.summary_best_plot_line
                        line["color"] = colour
                    else:
                        line = cls.summary_plot_line
                        transparency = 0.5
                        line["color"] = 'rgba' + colour[3:-1] + ', ' + \
                            str(transparency) + ')'

                    plotlyfig.add_trace(go.Scatter(
                        x=result.data_x[result.sorted_index],
                        y=result.fin_y[result.sorted_index],
                        mode='lines',
                        name=label,
                        line=line,
                        showlegend=result.is_best_fit
                    ))

                    plotlyfig.update_layout(
                        title=title
                        )

                if result.plot_scale in ["loglog", "logx"]:
                    plotlyfig.update_xaxes(type="log")
                if result.plot_scale in ["loglog", "logy"]:
                    plotlyfig.update_yaxes(type="log")

        html_fname = f'summary_plot_for_{first_result.sanitised_name}.html'
        offline_plot(
            plotlyfig,
            filename=os.path.join(figures_dir, html_fname),
            auto_open=False
        )
        return html_fname
