"""
Higher level functions that are used for plotting the fit plot and a starting
guess plot.
"""

import os

import numpy as np
import plotly.colors as ptly_colors
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from fitbenchmarking.utils.exceptions import PlottingError
from fitbenchmarking.utils.misc import get_js


class Plot:
    """
    Class providing plotting functionality.
    """

    _data_marker = {"symbol": "x", "color": "black", "opacity": 0.3}
    _best_fit_line = {"dash": "dot", "color": "#6699ff"}
    _summary_best_plot_line = {"width": 2}
    _summary_plot_line = {"width": 1, "dash": "dash"}
    _starting_guess_plot_line = {"width": 1, "color": "#5F8575"}
    _subplots_line = {"width": 1, "color": "red"}
    _error_dict = {
        "type": "data",
        "array": None,
        "thickness": 1,
        "width": 4,
        "color": "rgba(0,0,0,0.4)",
    }
    _SpinW_ax_titles = {"x": "Energy (meV)", "y": "Intensity"}
    _default_ax_titles = {"x": "x", "y": "y"}

    def __init__(self, best_result, options, figures_dir):
        self.result = best_result
        self.plots_failed = False

        if self.result.multivariate:
            self.plots_failed = True
            raise PlottingError(
                "Plots cannot be generated for multivariate problems"
            )
        if (
            self.result.problem_format == "horace"
            and self.result.spinw_plot_info is None
        ):
            self.plots_failed = True
            raise PlottingError(
                "Plots cannot be generated for this Horace problem"
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

    def plot_initial_guess(self, df_fit):
        """
        Plots the initial guess along with the data and stores in a file

        :param df_fit: A dataframe holding the data
        :type df_fit: Pandas dataframe

        :return: path to the saved file
        :rtype: str
        """
        title = self.result.name
        subplot_titles = None
        ax_titles = self._default_ax_titles
        n_plots = 1

        if self.result.spinw_plot_info is not None:
            n_plots = self.result.spinw_plot_info["n_cuts"]
            subplot_titles = self._get_subplot_titles_SpinW(self.result)
            ax_titles = self._SpinW_ax_titles

        fig = make_subplots(
            rows=1,
            cols=n_plots,
            subplot_titles=subplot_titles,
        )

        self._error_dict["array"] = df_fit["e"][df_fit["minimizer"] == "Data"]
        data_len = int(
            len(df_fit["y"][df_fit["minimizer"] == "Data"]) / n_plots
        )

        for i in range(n_plots):
            # Plot starting guess
            fig.add_trace(
                go.Scatter(
                    x=df_fit["x"][df_fit["minimizer"] == "Data"],
                    y=df_fit["y"][df_fit["minimizer"] == "Starting Guess"][
                        (data_len * i) : (data_len * (i + 1))
                    ],
                    name="Starting Guess",
                    line=self._subplots_line,
                    showlegend=i == 0,
                    legendgroup="starting-guess",
                    mode="markers+lines",
                ),
                row=1,
                col=i + 1,
            )
            self._update_axes_titles(fig, i, ax_titles)

        # Add raw data as a scatter plot
        self._add_data_points(
            fig,
            df_fit["x"][df_fit["minimizer"] == "Data"],
            df_fit["y"][df_fit["minimizer"] == "Data"],
            self._error_dict,
            n_plots,
        )

        fig.update_layout(title=title)
        self._update_to_logscale_if_needed(fig, self.result)

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

    def plotly_fit(self, df_fit):
        """
        Uses plotly to plot the calculated fit, along with the best fit.
        Stores the plot in a file

        :param df_fit: A dataframe holding the data
        :type df_fit: Pandas dataframe

        :return: A dictionary of paths to the saved files
        :rtype: dict[str, str]
        """
        # Plotly implementation below
        htmlfiles = {}
        x_best = df_fit["x"][df_fit["best"]]
        y_best = df_fit["y"][df_fit["best"]]
        x_data = df_fit["x"][df_fit["minimizer"] == "Data"]
        y_data = df_fit["y"][df_fit["minimizer"] == "Data"]
        x_start = df[df["minimizer"] == "Starting Guess"]["x"]
        y_start = df[df["minimizer"] == "Starting Guess"]["y"]
        self._error_dict["array"] = df_fit["e"][df_fit["minimizer"] == "Data"]
        n_plots = 1
        subplot_titles = None
        ax_titles = self._default_ax_titles

        if self.result.spinw_plot_info is not None:
            n_plots = self.result.spinw_plot_info["n_cuts"]
            subplot_titles = self._get_subplot_titles_SpinW(self.result)
            ax_titles = self._SpinW_ax_titles
            self._check_spinw_data_len(self.result, len(y_data), n_plots)

        data_len = int(
            len(df_fit["y"][df_fit["minimizer"] == "Data"]) / n_plots
        )
        df_fit = df_fit[~df_fit.minimizer.isin(["Data", "Starting Guess"])]

        for minimizer in df_fit["minimizer"].unique():
            fig = make_subplots(
                rows=1,
                cols=n_plots,
                subplot_titles=subplot_titles,
            )

            for i in range(n_plots):
                fig.add_trace(
                    go.Scatter(
                        x=df_fit["x"][df_fit["minimizer"] == minimizer],
                        y=df_fit["y"][df_fit["minimizer"] == minimizer][
                            (data_len * i) : (data_len * (i + 1))
                        ],
                        name=minimizer,
                        line=self._subplots_line,
                        showlegend=i == 0,
                        mode="markers+lines",
                        legendgroup=minimizer,
                    ),
                    row=1,
                    col=i + 1,
                )

                if not df_fit["best"][df_fit["minimizer"] == minimizer].iloc[
                    0
                ]:
                    # Add the best plot
                    name = (
                        "Best Fit "
                        + f"({df_fit['minimizer'][df_fit['best']].iloc[0]})"
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=x_best,
                            y=y_best[(data_len * i) : (data_len * (i + 1))],
                            name=name,
                            line=self._best_fit_line,
                            showlegend=i == 0,
                        ),
                        row=1,
                        col=i + 1,
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=x_start,
                            y=y_start,
                            mode="lines+markers",
                            name="Starting Guess",
                            line=self._starting_guess_plot_line,
                        )
                    )

                self._update_axes_titles(fig, i, ax_titles)

            # Add raw data
            self._add_data_points(
                fig, x_data, y_data, self._error_dict, n_plots
            )
            fig.update_layout(title=self.result.name)
            self._update_to_logscale_if_needed(fig, self.result)

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

        colours = cls._sample_colours(np.linspace(0, 1, len(categories)))
        first_result = next(iter(categories.values()))[0]
        n_plots = 1
        ax_titles = cls._default_ax_titles
        subplot_titles = None

        if first_result.spinw_plot_info is not None:
            subplot_titles = cls._get_subplot_titles_SpinW(first_result)
            n_plots = len(subplot_titles)
            ax_titles = cls._SpinW_ax_titles

        fig = make_subplots(
            rows=1,
            cols=n_plots,
            subplot_titles=subplot_titles,
        )

        # Plot data
        if "weighted_nlls" in options.cost_func_type:
            error_y = {
                "type": "data",
                "array": first_result.data_e,
                "color": "rgba(0,0,0,0.3)",
                "thickness": 1,
                "visible": True,
            }
        else:
            error_y = None

        data_x = first_result.data_x
        data_y = first_result.data_y
        cls._add_data_points(fig, data_x, data_y, error_y, n_plots)

        # Plot categories (cost functions)
        for (categ, results), colour in zip(categories.items(), colours):
            for result in results:
                if result.params is not None:
                    cls.plot_minimizer_results(
                        fig,
                        result,
                        n_plots,
                        categ,
                        ax_titles,
                        colour,
                    )
                    fig.update_layout(title=title)

                cls._update_to_logscale_if_needed(fig, result)

        html_fname = f"summary_plot_for_{first_result.sanitised_name}.html"

        cls.write_html_with_link_plotlyjs(
            fig, figures_dir, html_fname, options
        )
        return html_fname

    @classmethod
    def _add_data_points(cls, fig, data_x, data_y, error_y, n_plots):
        """
        Adds data points and error bars to given plot.

        :param fig: The plotly figure to add the data to
        :type fig: plotly.graph_objects.Figure
        :param data_x: Data along x axis
        :type data_x: np.ndarray
        :param data_y: Data along y axis
        :type data_y: np.ndarray
        :param error_y: Error associated with the points
        :type error_y: np.ndarray
        :param n_plots: number of subplots in the one row
        :type n_plots: int

        :return: Updated plot
        :rtype: plotly.graph_objects.Figure
        """
        data_len = int(len(data_y) / n_plots)

        for i in range(n_plots):
            fig.add_trace(
                go.Scatter(
                    x=data_x,
                    y=data_y[(data_len * i) : (data_len * (i + 1))],
                    error_y=error_y,
                    mode="markers",
                    name="Data",
                    marker=cls._data_marker,
                    showlegend=i == 0,
                    legendgroup="group-data",
                ),
                row=1,
                col=i + 1,
            )
        return fig

    @classmethod
    def plot_minimizer_results(
        cls, fig, result, n_plots, categ, ax_titles, colour
    ):
        """
        Plot results for each minimizer.
        :param fig: The plotly figure to add the traces to
        :type fig: plotly.graph_objects.Figure
        :param result: Result we want to add the trace for
        :type result: FittingResult
        :param n_plots_per_row: number of subplots per row
        :type n_plots_per_row: int
        :param categ: Cost function name
        :type categ: str
        :param ax_titles: dict with titles for x and y axis
        :type ax_titles: dict
        :param colour: Colour for the minimizer we are plotting
        :type colour: str
        :return: Updated plot
        :rtype: plotly.graph_objects.Figure
        """
        line = (
            cls._summary_best_plot_line
            if result.is_best_fit
            else cls._summary_plot_line
        )
        label = categ if result.is_best_fit else ""
        if result.is_best_fit:
            line = cls._summary_best_plot_line
            line["color"] = colour
        else:
            line = cls._summary_plot_line
            line["color"] = (
                "rgba" + colour[3:-1] + ", 0.5)"  # 0.5 transparency
            )

        data_len = int(len(result.data_y) / n_plots)

        for i in range(n_plots):
            if n_plots > 1:
                x = result.data_x
                y = result.fin_y[(data_len * i) : (data_len * (i + 1))]
            else:
                x = result.data_x[result.sorted_index]
                y = result.fin_y[result.sorted_index]

            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    name=label,
                    line=line,
                    showlegend=result.is_best_fit and i == 0,
                    legendgroup=f"group-{categ}-{result.is_best_fit}"
                    if n_plots > 1
                    else None,
                ),
                row=1,
                col=i + 1,
            )

            cls._update_axes_titles(fig, i, ax_titles)

        return fig

    @classmethod
    def plot_residuals(cls, categories, title, options, figures_dir):
        """
        Create a comparison plot showing residuals for all fits,
        while emphasizing the residuals for the best fit .

        :param categories: The results to plot
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
        first_result = next(iter(categories.values()))[0]
        col_vals = np.linspace(0, 1, len(list(categories.values())[0]))
        colours = cls._sample_colours(col_vals)
        n_plots_per_row = 1

        if first_result.spinw_plot_info is not None:
            subplot_titles = cls._get_subplot_titles_SpinW(first_result)
            cls._check_spinw_data_len(
                first_result,
                len(first_result.data_y),
                len(subplot_titles),
            )
            n_plots_per_row = len(subplot_titles)

        # Create subplots on each row if needed
        if n_plots_per_row > 1:
            fig = cls._create_empty_residuals_plots(categories, subplot_titles)
        else:
            fig = make_subplots(
                rows=len(categories),
                cols=n_plots_per_row,
                subplot_titles=list(categories.keys()),
            )

        for row_ind, (results) in enumerate(categories.values(), 1):
            for result, colour in zip(results, colours):
                if result.params is not None:
                    fig = cls._add_residual_traces_to_fig(
                        fig, result, n_plots_per_row, colour, row_ind
                    )
                    fig.update_layout(title=title + ": residuals")

                cls._update_to_logscale_if_needed(fig, result)

            if row_ind == 1:
                fig.update_traces(row=row_ind)

        html_fname = f"residuals_plot_for_{first_result.sanitised_name}.html"
        cls.write_html_with_link_plotlyjs(
            fig, figures_dir, html_fname, options
        )

        return html_fname

    @classmethod
    def _create_empty_residuals_plots(cls, categories, subplot_titles):
        """
        Creates the initially empty residuals plot for spinw problems.

        :param categories: The results to plot
        :type categories: dict[str, list[FittingResults]]
        :param subplot_titles: Subplot titles
        :type subplot_titles: list

        :return: The produced figure
        :rtype: plotly.graph_objects.Figure
        """
        row_titles = list(categories.keys())

        fig = make_subplots(
            rows=len(categories),
            cols=len(subplot_titles),
            row_titles=row_titles,
            subplot_titles=subplot_titles * len(categories),
        )

        # Place name of cost function on left hand side of figure
        fig.for_each_annotation(
            lambda a: a.update(x=-0.08, textangle=-90)
            if a.text in row_titles
            else ()
        )
        return fig

    @classmethod
    def _add_residual_traces_to_fig(
        cls, fig, result, n_plots_per_row, colour, row_ind
    ):
        """
        Adds traces to the empty residuals plot figure.

        :param fig: The plotly figure to add the traces to
        :type fig: plotly.graph_objects.Figure
        :param result: Result we want to add the trace for
        :type result: FittingResult
        :param n_plots_per_row: number of subplots per row
        :type n_plots_per_row: int
        :param colour: Colour for the minimizer we are plotting
        :type colour: str
        :param row_ind: Index of the row we are adding traces to
        :type row_ind: int

        :return: Updated plot
        :rtype: plotly.graph_objects.Figure
        """
        minim = result.minimizer
        label = f" {minim}"
        data_len = int(len(result.data_y) / n_plots_per_row)

        for i in range(n_plots_per_row):
            fig.add_trace(
                go.Scatter(
                    x=result.data_x,
                    y=result.r_x[(data_len * i) : (data_len * (i + 1))],
                    mode="markers",
                    name=label,
                    marker={"color": colour},
                    showlegend=(i == 0 and row_ind == 1),
                    legendgroup=f"group{minim}",
                ),
                row=row_ind,
                col=i + 1,
            )

        return fig

    @classmethod
    def _check_spinw_data_len(cls, result, y_data_len, n_plots_per_row):
        """
        Checks x and y data have same length

        :param result: Any of the results
        :type result: FittingResult
        :param y_data_len: Length of data along y
        :type y_data_len: int
        :param n_plots_per_row: Number of subplots in a row
        :type n_plots_per_row: int
        """
        data_len = int(y_data_len / n_plots_per_row)
        if data_len != len(result.spinw_plot_info["ebin_cens"]):
            raise PlottingError("x and y data lengths are not the same")

    @classmethod
    def _get_subplot_titles_SpinW(cls, result):
        """Get subplot titles for SpinW"""
        subplot_titles = [
            f"{i} Å<sup>-1</sup>" for i in result.spinw_plot_info["q_cens"]
        ]
        return subplot_titles

    @classmethod
    def _update_axes_titles(cls, fig, col_ind, ax_titles=None):
        ax_titles = ax_titles if not None else cls._default_ax_titles
        if col_ind == 0:
            fig.update_yaxes(title_text=ax_titles["y"], row=1, col=col_ind + 1)
        fig.update_xaxes(title_text=ax_titles["x"], row=1, col=col_ind + 1)
        return fig

    @classmethod
    def _update_to_logscale_if_needed(self, fig, result):
        if result.plot_scale in ["loglog", "logx"]:
            fig.update_xaxes(type="log")
        if result.plot_scale in ["loglog", "logy"]:
            fig.update_yaxes(type="log")
        return fig

    @classmethod
    def _sample_colours(cls, points):
        """
        Samples plotly colours based on values passed as input
        """
        plotly_colours = ptly_colors.sample_colorscale(
            ptly_colors.sequential.Rainbow, samplepoints=points
        )
        return plotly_colours
