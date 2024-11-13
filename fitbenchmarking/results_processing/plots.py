"""
Higher level functions that are used for plotting the fit plot and a starting
guess plot.
"""

import os

import numpy as np
import plotly.colors as ptly_colors
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.misc import get_js


class Plot:
    """
    Class providing plotting functionality.
    """

    _data_marker = {"symbol": "x", "color": "black"}
    _best_fit_line = {"dash": "dot", "color": "#6699ff"}
    _legend_options = {
        "yanchor": "top",
        "y": 0.99,
        "xanchor": "left",
        "x": 0.01,
        "bgcolor": "rgba(0,0,0,0.1)",
    }
    _summary_best_plot_line = {"width": 2}
    _summary_plot_line = {"width": 1}
    _error_dict = {"type": "data", "array": None, "thickness": 1, "width": 4}

    def __init__(self, best_result, options, figures_dir):
        self.result = best_result
        self.plots_failed = False

        if self.result.multivariate:
            self.plots_failed = True
            raise PlottingError(
                "Plots cannot be generated for multivariate problems"
            )
        if self.result.problem_format == "horace":
            self.plots_failed = True
            raise PlottingError(
                "Plots cannot be generated for Horace problems"
            )
        if self.result.problem_format == "bal":
            self.plots_failed = True
            raise PlottingError("Plots cannot be generated for BAL problems")

        self.options = options
        self.figures_dir = figures_dir

    @staticmethod
    def write_html_with_link_plotlyjs(fig, figures_dir, htmlfile, options):
        """
        Writes an html file for the figure passed as input and
        includes link to the relevant plotly.js file.

        :param fig: Figure to be saved
        :type fig: plotly.graph_objs._figure.Figure
        :param figures_dir: The directory to save the figures in
        :type figures_dir: str
        :param htmlfile: Name of the figure
        :type htmlfile: str
        :param options: The options for the run
        :type options: utils.options.Options

        :return: None
        """
        plotly_path = get_js(options, figures_dir).get("plotly")
        html_file_name = os.path.join(figures_dir, htmlfile)
        fig.write_html(html_file_name, include_plotlyjs=plotly_path)

    def plot_initial_guess(self, df):
        """
        Plots the initial guess along with the data and stores in a file

        :param df: A dataframe holding the data
        :type df: Pandas dataframe

        :return: path to the saved file
        :rtype: str
        """

        # Plotly implementation below
        fig = px.line(
            df[df["minimizer"] == "Starting Guess"],
            x="x",
            y="y",
            color="minimizer",
            title=self.result.name,
            markers=True,
        )
        self._error_dict["array"] = df["e"][df["minimizer"] == "Data"]
        # add the raw data as a scatter plot
        fig.add_trace(
            go.Scatter(
                x=df["x"][df["minimizer"] == "Data"],
                y=df["y"][df["minimizer"] == "Data"],
                error_y=self._error_dict,
                mode="markers",
                name="Data",
                marker=self._data_marker,
            )
        )
        fig.update_layout(legend=self._legend_options)

        if self.result.plot_scale in ["loglog", "logx"]:
            fig.update_xaxes(type="log")
        if self.result.plot_scale in ["loglog", "logy"]:
            fig.update_yaxes(type="log")

        htmlfile = f"start_for_{self.result.sanitised_name}.html"

        self.write_html_with_link_plotlyjs(
            fig, self.figures_dir, htmlfile, self.options
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
        htmlfile = (
            f"{result.sanitised_min_name(True)}_fit_for_"
            f"{result.costfun_tag}_{result.sanitised_name}.html"
        )
        return htmlfile

    def plotly_fit(self, df):
        """
        Uses plotly to plot the calculated fit, along with the best fit.
        Stores the plot in a file

        :param df: A dataframe holding the data
        :type df: Pandas dataframe

        :return: A dictionary of paths to the saved files
        :rtype: dict[str, str]
        """
        # Plotly implementation below
        htmlfiles = {}
        x_best = df["x"][df["best"]]
        y_best = df["y"][df["best"]]
        x_data = df["x"][df["minimizer"] == "Data"]
        y_data = df["y"][df["minimizer"] == "Data"]
        self._error_dict["array"] = df["e"][df["minimizer"] == "Data"]

        for minimizer in df["minimizer"].unique():
            if minimizer not in ["Data", "Starting Guess"]:
                fig = px.line(
                    df[df["minimizer"] == minimizer],
                    x="x",
                    y="y",
                    color="minimizer",
                    title=self.result.name,
                    markers=True,
                )
                if not df["best"][df["minimizer"] == minimizer].iloc[0]:
                    # add the best plot
                    name = f"Best Fit ({df['minimizer'][df['best']].iloc[0]})"
                    fig.add_trace(
                        go.Scatter(
                            x=x_best,
                            y=y_best,
                            mode="lines",
                            name=name,
                            line=self._best_fit_line,
                        )
                    )
                # add the raw data as a scatter plot
                fig.add_trace(
                    go.Scatter(
                        x=x_data,
                        y=y_data,
                        error_y=self._error_dict,
                        mode="markers",
                        name="Data",
                        marker=self._data_marker,
                    )
                )
                fig.update_layout(legend=self._legend_options)

                if self.result.plot_scale in ["loglog", "logx"]:
                    fig.update_xaxes(type="log")
                if self.result.plot_scale in ["loglog", "logy"]:
                    fig.update_yaxes(type="log")

                htmlfile = (
                    f"{minimizer}_fit_for_{self.result.costfun_tag}"
                    f"_{self.result.sanitised_name}.html"
                )

                self.write_html_with_link_plotlyjs(
                    fig, self.figures_dir, htmlfile, self.options
                )

                htmlfiles[minimizer] = htmlfile

        return htmlfiles

    def plot_posteriors(self, result):
        """
        Use Plotly to plot estimated posterior pdfs.

        :param result: The result to plot
        :type result: FittingResult

        :return: path to the saved file
        :rtype: str
        """

        par_names = self.result.param_names

        fig = make_subplots(
            rows=len(par_names), cols=1, subplot_titles=par_names
        )

        for i, name in enumerate(par_names):
            fig.append_trace(
                go.Histogram(
                    x=result.params_pdfs[name], histnorm="probability density"
                ),
                row=i + 1,
                col=1,
            )

        if result.params_pdfs["scipy_pfit"] is not None:
            scipy_fit = result.params_pdfs["scipy_pfit"]
            scipy_err = result.params_pdfs["scipy_perr"]

            for i, name in enumerate(par_names):
                fig.add_vline(
                    x=scipy_fit[i], row=i + 1, col=1, line_color="red"
                )
                fig.add_vline(
                    x=scipy_fit[i] - 2 * scipy_err[i],
                    row=i + 1,
                    col=1,
                    line_color="red",
                    line_dash="dash",
                )
                fig.add_vline(
                    x=scipy_fit[i] + 2 * scipy_err[i],
                    row=i + 1,
                    col=1,
                    line_color="red",
                    line_dash="dash",
                )

        fig.update_layout(showlegend=False)

        html_fname = (
            f"{result.sanitised_min_name(True)}_posterior_"
            f"pdf_plot_for_{result.sanitised_name}.html"
        )
        self.write_html_with_link_plotlyjs(
            fig, self.figures_dir, html_fname, self.options
        )
        return html_fname

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
            ptly_colors.sequential.Rainbow, samplepoints=col_vals
        )

        first_result = next(iter(categories.values()))[0]

        plotlyfig = go.Figure()

        # Plot data
        if "weighted_nlls" in options.cost_func_type:
            error_y = {
                "type": "data",
                "array": first_result.data_e,
                "color": "rgb(0,0,0,0.8)",
                "thickness": 1,
                "visible": True,
            }
        else:
            error_y = None
        plotlyfig.add_trace(
            go.Scatter(
                x=first_result.data_x,
                y=first_result.data_y,
                error_y=error_y,
                mode="markers",
                name="Data",
                marker=cls._data_marker,
            )
        )

        for (key, results), colour in zip(categories.items(), plotly_colours):
            # Plot category
            for result in results:
                if result.params is not None:
                    line = (
                        cls._summary_best_plot_line
                        if result.is_best_fit
                        else cls._summary_plot_line
                    )

                    line["color"] = colour
                    label = key if result.is_best_fit else ""
                    if result.is_best_fit:
                        line = cls._summary_best_plot_line
                        line["color"] = colour
                    else:
                        line = cls._summary_plot_line
                        transparency = 0.5
                        line["color"] = (
                            "rgba"
                            + colour[3:-1]
                            + ", "
                            + str(transparency)
                            + ")"
                        )

                    plotlyfig.add_trace(
                        go.Scatter(
                            x=result.data_x[result.sorted_index],
                            y=result.fin_y[result.sorted_index],
                            mode="lines",
                            name=label,
                            line=line,
                            showlegend=result.is_best_fit,
                        )
                    )

                    plotlyfig.update_layout(title=title)

                if result.plot_scale in ["loglog", "logx"]:
                    plotlyfig.update_xaxes(type="log")
                if result.plot_scale in ["loglog", "logy"]:
                    plotlyfig.update_yaxes(type="log")

        html_fname = f"summary_plot_for_{first_result.sanitised_name}.html"

        cls.write_html_with_link_plotlyjs(
            plotlyfig, figures_dir, html_fname, options
        )

        return html_fname
