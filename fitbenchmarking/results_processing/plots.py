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
            and self.result.plot_info is None
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
    def write_html_with_link_plotlyjs(
        fig, figures_dir, htmlfile, options
    ) -> None:
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
        """
        plotly_path = get_js(options, figures_dir).get("plotly")
        html_file_name = os.path.join(figures_dir, htmlfile)
        fig.write_html(html_file_name, include_plotlyjs=plotly_path)

    def plot_initial_guess(self, df_fit) -> str:
        """
        Plots the initial guess along with the data and stores in a file

        :param df_fit: A dataframe holding the data
        :type df_fit: Pandas dataframe

        :return: path to the saved file
        :rtype: str
        """
        title = self.result.name
        n_plots, subplot_titles, ax_titles = self._set_n_plots_and_titles(
            self.result
        )

        fig = make_subplots(
            rows=1,
            cols=n_plots,
            subplot_titles=subplot_titles,
        )

        self._error_dict["array"] = df_fit["e"][df_fit["minimizer"] == "Data"]

        self._add_data_points(
            fig,
            df_fit["x"][df_fit["minimizer"] == "Data"],
            df_fit["y"][df_fit["minimizer"] == "Data"],
            self._error_dict,
            n_plots,
        )
        self._add_starting_guess(fig, df_fit, n_plots, ax_titles)

        fig.update_layout(title=title)
        self._update_to_logscale_if_needed(fig, self.result)

        htmlfile = f"start_for_{self.result.sanitised_name}.html"
        self.write_html_with_link_plotlyjs(
            fig, self.figures_dir, htmlfile, self.options
        )
        return htmlfile

    @staticmethod
    def best_filename(result) -> str:
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

    def plotly_fit(self, df_fit) -> dict[str, str]:
        """
        Uses plotly to plot the calculated fit, along with the best fit.
        Stores the plot in a file

        :param df_fit: A dataframe holding the data
        :type df_fit: Pandas dataframe

        :return: A dictionary of paths to the saved files
        :rtype: dict[str, str]
        """
        htmlfiles = {}
        x_best = df_fit["x"][df_fit["best"]]
        y_best = df_fit["y"][df_fit["best"]]
        x_data = df_fit["x"][df_fit["minimizer"] == "Data"]
        y_data = df_fit["y"][df_fit["minimizer"] == "Data"]
        self._error_dict["array"] = df_fit["e"][df_fit["minimizer"] == "Data"]

        n_plots, subplot_titles, ax_titles = self._set_n_plots_and_titles(
            self.result
        )

        if self.result.plot_info is not None:
            self._check_data_len(x_data, y_data)

        data_len = int(
            len(df_fit["y"][df_fit["minimizer"] == "Data"]) / n_plots
        )

        for minimizer in df_fit[
            ~df_fit.minimizer.isin(["Data", "Starting Guess"])
        ]["minimizer"].unique():
            fig = make_subplots(
                rows=1,
                cols=n_plots,
                subplot_titles=subplot_titles,
            )
            self._add_data_points(
                fig, x_data, y_data, self._error_dict, n_plots
            )
            self._add_starting_guess(fig, df_fit, n_plots, ax_titles)

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
                            legendgroup="best-minim",
                            showlegend=i == 0,
                        ),
                        row=1,
                        col=i + 1,
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

    def plot_posteriors(self, result) -> str:
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
    def plot_summary(cls, categories, title, options, figures_dir) -> str:
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
        n_plots, subplot_titles, ax_titles = cls._set_n_plots_and_titles(
            first_result
        )

        fig = make_subplots(
            rows=1,
            cols=n_plots,
            subplot_titles=subplot_titles,
        )

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

        # in the SpinW 2d data case
        if first_result.data_x_cuts is not None:
            data_x = first_result.data_x_cuts
            data_y = first_result.data_y_cuts

        cls._add_data_points(fig, data_x, data_y, error_y, n_plots)

        # Plot categories (cost functions)
        for (categ, results), colour in zip(categories.items(), colours):
            for result in results:
                if result.params is not None:
                    cls._plot_minimizer_results(
                        fig,
                        result,
                        n_plots,
                        categ,
                        ax_titles,
                        colour,
                    )

                cls._update_to_logscale_if_needed(fig, result)

        fig.update_layout(title=title)

        html_fname = f"summary_plot_for_{first_result.sanitised_name}.html"
        cls.write_html_with_link_plotlyjs(
            fig, figures_dir, html_fname, options
        )
        return html_fname

    @classmethod
    def _add_data_points(
        cls, fig, data_x, data_y, error_y, n_plots
    ) -> go.Figure:
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
    def _plot_minimizer_results(
        cls, fig, result, n_plots, categ, ax_titles, colour
    ) -> go.Figure:
        """
        Plots results for each minimizer.

        :param fig: The plotly figure to add the traces to
        :type fig: plotly.graph_objects.Figure
        :param result: Result we want to add the trace for
        :type result: FittingResult
        :param n_plots_per_row: number of subplots per row
        :type n_plots_per_row: int
        :param categ: Cost function name
        :type categ: str
        :param ax_titles: Titles for x and y axis
        :type ax_titles: dict[str, str]
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

        for i in range(n_plots):
            if n_plots > 1 and result.data_x_cuts is not None:
                x = result.data_x_cuts
                data_len = int(len(x) / n_plots)
                y = result.fin_y_cuts[(data_len * i) : (data_len * (i + 1))]
            elif n_plots > 1:
                x = result.data_x
                data_len = int(len(x) / n_plots)
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
    def plot_residuals(cls, categories, title, options, figures_dir) -> str:
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
        subplot_titles = None

        if first_result.plot_info is not None:
            n_plots_per_row = first_result.plot_info["n_plots"]
            subplot_titles = first_result.plot_info["subplot_titles"]

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
                    fig = cls._add_residual_traces(
                        fig, result, n_plots_per_row, colour, row_ind
                    )
                cls._update_to_logscale_if_needed(fig, result)

            if row_ind == 1:
                fig.update_traces(row=row_ind)

        fig.update_layout(title=title + ": residuals")

        html_fname = f"residuals_plot_for_{first_result.sanitised_name}.html"
        cls.write_html_with_link_plotlyjs(
            fig, figures_dir, html_fname, options
        )
        return html_fname

    @classmethod
    def plot_2d_data(cls, categories, title, options, figures_dir) -> str:
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

        html_fname = ""
        n_categs = len(categories)
        titles = []

        for categ_key, results in categories.items():
            for result in results:
                if (
                    result.plot_info["plot_type"] == "2d"
                    and result.is_best_fit
                ):
                    titles.extend([f"{categ_key}: {result.minimizer} (best)"])

        # If data is not 2d, don't create plot
        if len(titles) == 0:
            return ""

        width = None
        if n_categs < 2:
            width = 600

        fig = make_subplots(
            rows=1,
            cols=n_categs,
            shared_yaxes=True,
            horizontal_spacing=0.1,
            subplot_titles=titles,
        )

        for ind, (categ_key, results) in enumerate(categories.items(), 1):
            for result in results:
                if (
                    result.plot_info["plot_type"] == "2d"
                    and result.is_best_fit
                ):
                    img = np.rot90(result.fin_y_complete.T, k=4)
                    fig.add_trace(
                        px.imshow(
                            img,
                        ).data[0],
                        row=1,
                        col=ind,
                    )
                    fig.add_trace(
                        go.Contour(
                            z=img, contours_coloring="lines", line_width=2
                        ),
                    )
                    step = 6
                    ebin_cens = result.plot_info["ebin_cens"]
                    y_ticktext = np.round(
                        np.linspace(ebin_cens[0], ebin_cens[-1], step), 2
                    )
                    y_tickvals = np.linspace(0, np.shape(img)[0], step)
                    fig.update_yaxes(
                        title_text="Energy (meV)",
                        tickmode="array",
                        tickvals=y_tickvals,
                        ticktext=y_ticktext,
                        row=1,
                        col=ind,
                    )

                    modQ_cens = result.plot_info["modQ_cens"]
                    x_ticktext = np.round(
                        np.linspace(modQ_cens[0], modQ_cens[-1], step), 2
                    )
                    x_tickvals = np.linspace(0, np.shape(img)[1], step)
                    fig.update_xaxes(
                        title_text="|Q| (Å<sup>-1</sup>)",
                        tickmode="array",
                        tickvals=x_tickvals,
                        ticktext=x_ticktext,
                        row=1,
                        col=ind,
                    )

        fig.update_layout(title=title + ": 2d plots", width=width)
        fig.update_coloraxes(colorscale="viridis")

        html_fname = f"2d_plots_for_best_minims_{result.sanitised_name}.html"
        cls.write_html_with_link_plotlyjs(
            fig, figures_dir, html_fname, options
        )
        return html_fname

    @classmethod
    def _create_empty_residuals_plots(
        cls, categories, subplot_titles
    ) -> go.Figure:
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

    def _add_starting_guess(
        self, fig, df_fit, n_plots_per_row, ax_titles
    ) -> go.Figure:
        """
        Adds starting guess to figure.

        :param fig: The plotly figure to add the traces to
        :type fig: plotly.graph_objects.Figure
        :param df_fit: The dataframe with the data to plot
        :type df_fit: Pandas dataframe
        :param n_plots_per_row: number of subplots per row
        :type n_plots_per_row: int
        :param ax_titles: Titles for axes
        :type ax_titles: dict[str, str]

        :return: Updated plot
        :rtype: plotly.graph_objects.Figure
        """
        data_len = int(
            len(df_fit["y"][df_fit["minimizer"] == "Starting Guess"])
            / n_plots_per_row
        )
        for i in range(n_plots_per_row):
            fig.add_trace(
                go.Scatter(
                    x=df_fit["x"][df_fit["minimizer"] == "Starting Guess"],
                    y=df_fit["y"][df_fit["minimizer"] == "Starting Guess"][
                        (data_len * i) : (data_len * (i + 1))
                    ],
                    name="Starting Guess",
                    line=self._starting_guess_plot_line,
                    showlegend=i == 0,
                    legendgroup="starting-guess",
                    mode="markers+lines",
                ),
                row=1,
                col=i + 1,
            )
            self._update_axes_titles(fig, i, ax_titles)

        return fig

    @classmethod
    def _add_residual_traces(
        cls, fig, result, n_plots_per_row, colour, row_ind
    ) -> go.Figure:
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
        data_x = result.data_x
        r_x = result.r_x

        # in the SpinW 2d data case
        if result.r_x_cuts is not None:
            data_x = result.data_x_cuts
            r_x = result.r_x_cuts

        data_len = int(len(data_x) / n_plots_per_row)
        for i in range(n_plots_per_row):
            fig.add_trace(
                go.Scatter(
                    x=data_x,
                    y=r_x[(data_len * i) : (data_len * (i + 1))],
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

    def _check_data_len(self, x_data, y_data) -> None:
        """
        Checks x and y data have same length and raises error if not.
        """
        if len(y_data) != len(x_data):
            raise PlottingError("x and y data lengths are not the same")

    @classmethod
    def _update_axes_titles(cls, fig, col_ind, ax_titles) -> go.Figure:
        """
        Sets the titles of x and y axes.
        For space reasons, only sets the y axis title of the plot on the very
        left, as this will be the same in the other plots.

        :param fig: The plotly figure to add the traces to
        :type fig: plotly.graph_objects.Figure
        :param col_ind: Index of the colum (subplot) we are adding ax titles to
        :type col_ind: int
        :param ax_titles: Titles for each axis
        :type ax_titles: dict[str, str]

        :return: Updated plot
        :rtype: plotly.graph_objects.Figure
        """
        if col_ind == 0:
            fig.update_yaxes(title_text=ax_titles["y"], row=1, col=col_ind + 1)
        fig.update_xaxes(title_text=ax_titles["x"], row=1, col=col_ind + 1)
        return fig

    @classmethod
    def _update_to_logscale_if_needed(self, fig, result) -> go.Figure:
        """
        Updates logscale to log if this is specified in result.plot_scale .
        """
        if result.plot_scale in ["loglog", "logx"]:
            fig.update_xaxes(type="log")
        if result.plot_scale in ["loglog", "logy"]:
            fig.update_yaxes(type="log")
        return fig

    @classmethod
    def _sample_colours(cls, points) -> list[str]:
        """
        Samples plotly colours based on values passed as input
        """
        plotly_colours = ptly_colors.sample_colorscale(
            ptly_colors.sequential.Rainbow, samplepoints=points
        )
        return plotly_colours

    @classmethod
    def _set_n_plots_and_titles(cls, result):
        """
        Returns n_plots, subplot_titles, ax_titles
        """
        n_plots = 1
        subplot_titles = None
        ax_titles = cls._default_ax_titles

        if result.plot_info is not None:
            n_plots = result.plot_info["n_plots"]
            subplot_titles = result.plot_info["subplot_titles"]
            ax_titles = result.plot_info["ax_titles"]

        return n_plots, subplot_titles, ax_titles
