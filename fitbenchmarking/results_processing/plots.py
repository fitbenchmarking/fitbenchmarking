"""
Higher level functions that are used for plotting the fit plot and a starting
guess plot.
"""

from itertools import cycle
from pathlib import Path
from typing import Optional

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
    _multistart_successful_fit_line = {
        "width": 2,
        "color": "rgba(0, 0, 255, 0.2)",
    }
    _multistart_unsuccessful_fit_line = {
        "width": 2,
        "color": "rgba(255, 0, 0, 0.2)",
    }
    _subplots_line = {"width": 1, "color": "red"}
    _error_dict = {
        "type": "data",
        "array": None,
        "thickness": 1,
        "width": 4,
        "color": "rgba(0,0,0,0.4)",
    }
    _default_ax_titles = {"x": "x", "y": "y"}
    _legend_style = {
        "yanchor": "top",
        "y": -0.3,
        "xanchor": "center",
        "x": 0.5,
    }

    def __init__(self, best_result, options, figures_dir):
        self.result = best_result

        if self.result.multivariate:
            raise PlottingError(
                "Plots cannot be generated for multivariate problems"
            )
        if (
            self.result.problem_format == "horace"
            and self.result.plot_info is None
        ):
            raise PlottingError(
                "Plots cannot be generated for this Horace problem"
            )
        if self.result.problem_format == "bal":
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
        html_file_name = Path(figures_dir) / htmlfile
        fig.write_html(html_file_name, include_plotlyjs=plotly_path)

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

        n_plots, subplot_titles, ax_titles = self._get_n_plots_and_titles(
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

            fig.update_layout(
                title=self.result.name, legend=self._legend_style
            )
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

    @staticmethod
    def plot_summary(categories, title, options, figures_dir) -> str:
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
        colours = Plot._sample_colours(np.linspace(0, 1, len(categories)))
        first_result = next(iter(categories.values()))[0]
        n_plots, subplot_titles, ax_titles = Plot._get_n_plots_and_titles(
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
        if hasattr(first_result, "data_x_cuts"):
            data_x = first_result.data_x_cuts
            data_y = first_result.data_y_cuts

        Plot._add_data_points(fig, data_x, data_y, error_y, n_plots)

        # Plot categories (cost functions)
        for (categ, results), colour in zip(categories.items(), colours):
            for result in results:
                if result.params is not None:
                    Plot._plot_minimizer_results(
                        fig,
                        result,
                        n_plots,
                        categ,
                        ax_titles,
                        colour,
                    )

                Plot._update_to_logscale_if_needed(fig, result)

        fig.update_layout(title=title, legend=Plot._legend_style)

        html_fname = f"summary_plot_for_{first_result.sanitised_name}.html"
        Plot.write_html_with_link_plotlyjs(
            fig, figures_dir, html_fname, options
        )
        return html_fname

    @staticmethod
    def _add_data_points(fig, data_x, data_y, error_y, n_plots) -> go.Figure:
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
                    marker=Plot._data_marker,
                    showlegend=i == 0,
                    legendgroup="group-data",
                ),
                row=1,
                col=i + 1,
            )
        return fig

    @staticmethod
    def _plot_minimizer_results(
        fig, result, n_plots, categ, ax_titles, colour
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
            Plot._summary_best_plot_line
            if result.is_best_fit
            else Plot._summary_plot_line
        )
        label = categ if result.is_best_fit else ""
        if result.is_best_fit:
            line = Plot._summary_best_plot_line
            line["color"] = colour
        else:
            line = Plot._summary_plot_line
            line["color"] = (
                "rgba" + colour[3:-1] + ", 0.5)"  # 0.5 transparency
            )

        for i in range(n_plots):
            if n_plots > 1:
                # for SpinW data
                if hasattr(result, "data_x_cuts"):
                    # if the fit was on 2d data
                    x = result.data_x_cuts
                    data_len = int(len(x) / n_plots)
                    y = result.fin_y_cuts[
                        (data_len * i) : (data_len * (i + 1))
                    ]
                else:
                    # if the fit was on 1d cuts of 2d data
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
            Plot._update_axes_titles(fig=fig, col_ind=i, ax_titles=ax_titles)

        return fig

    @staticmethod
    def plot_residuals(categories, title, options, figures_dir) -> str:
        """
        Create a comparison plot showing residuals for all fits,
        while emphasizing the residuals for the best fit.

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
        colours = Plot._sample_colours(col_vals)
        n_plots_per_row = 1
        subplot_titles = None

        if first_result.plot_info is not None:
            n_plots_per_row = first_result.plot_info["n_plots"]
            subplot_titles = first_result.plot_info["subplot_titles"]

        # Create subplots on each row if needed
        if n_plots_per_row > 1:
            fig = Plot._create_empty_residuals_plots(
                categories, subplot_titles
            )
        else:
            fig = make_subplots(
                rows=len(categories),
                cols=n_plots_per_row,
                subplot_titles=list(categories.keys()),
            )

        for row_ind, (results) in enumerate(categories.values(), 1):
            for result, colour in zip(results, colours):
                if result.params is not None:
                    fig = Plot._add_residual_traces(
                        fig, result, n_plots_per_row, colour, row_ind
                    )
                Plot._update_to_logscale_if_needed(fig, result)

            if row_ind == 1:
                fig.update_traces(row=row_ind)

        fig.update_layout(title=title + ": residuals")

        html_fname = f"residuals_plot_for_{first_result.sanitised_name}.html"
        Plot.write_html_with_link_plotlyjs(
            fig, figures_dir, html_fname, options
        )
        return html_fname

    @staticmethod
    def plot_multistart(results, options, figures_dir) -> str:
        """
        Creates a plot showing the results categorized by
        cost function, software and minimizer. The plots
        summarize the performance of different minimizers
        with multiple starting conditions. The plots generated
        are color coded. The blue traces are the ones that achieved
        a good fit while the red traces are the ones that did not.

        :param results: All the results sorted by cost function,
                        software and minimizer.
        :type results: dict[str, list[FittingResults]]

        :return: The path to the new plot
        :rtype: str
        """
        # Determine the number of plots and set the loop variables
        minimizer_count = sum(
            len(mins) for mins in options.minimizers.values()
        )
        n_plots = len(results) * minimizer_count
        max_plots_per_row = min(n_plots, 3)
        n_rows = int(np.ceil(n_plots / max_plots_per_row))
        cyclic_column_iter = cycle(range(1, max_plots_per_row + 1))
        row_ix, col_ix, plot_ix = 1, next(cyclic_column_iter), 1

        # Generate the plot titles
        titles = [
            f"<b>{software} - {minimizer}<br>({cost_function})<b>"
            for cost_function in results
            for software in results[cost_function]
            for minimizer in results[cost_function][software]
        ]

        # Create the figure with subplots
        fig = make_subplots(
            rows=n_rows,
            cols=max_plots_per_row,
            subplot_titles=titles,
        )

        # Update the font size of the titles
        for annotation in fig.layout.annotations:
            annotation.font.size = 9

        # Add the data and traces to the subplots in the figure
        for cost_function in results:
            for software in results[cost_function]:
                for minimizer in results[cost_function][software]:
                    data_points_added = False
                    for result in results[cost_function][software][minimizer]:
                        # Add the data points to the plot
                        if not data_points_added:
                            error_y = Plot._error_dict | {
                                "array": result.data_e
                            }
                            fig.add_trace(
                                go.Scatter(
                                    x=result.data_x,
                                    y=result.data_y,
                                    error_y=error_y,
                                    name="Data",
                                    mode="markers",
                                    marker=Plot._data_marker,
                                    showlegend=False,
                                ),
                                row=row_ix,
                                col=col_ix,
                            )
                            data_points_added = True

                        # Determine the line style. The traces are blue if the
                        # fit was successful and red if it was not.
                        line_style = (
                            Plot._multistart_successful_fit_line
                            if result.norm_acc
                            <= options.multistart_success_threshold
                            else Plot._multistart_unsuccessful_fit_line
                        )

                        # Add the starting guess trace
                        fig.add_trace(
                            go.Scatter(
                                x=result.data_x,
                                y=result.ini_y,
                                mode="lines",
                                line=line_style,
                                name=result.name.split(", ")[-1],
                                showlegend=False,
                            ),
                            row=row_ix,
                            col=col_ix,
                        )

                    # Set the axis titles of the subplots
                    Plot._update_axes_titles(
                        fig=fig,
                        col_ind=col_ix - 1,
                        row_ind=row_ix,
                        ax_titles=Plot._default_ax_titles,
                    )

                    # Update the loop variables
                    plot_ix += 1
                    row_ix = int(np.ceil(plot_ix / max_plots_per_row))
                    col_ix = next(cyclic_column_iter)

        # Create the custom legend
        for style, name in zip(
            [
                Plot._multistart_successful_fit_line,
                Plot._multistart_unsuccessful_fit_line,
            ],
            ["Success", "Fail"],
        ):
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="lines",
                    line=style,
                    name=name,
                    showlegend=True,
                )
            )
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=Plot._data_marker,
                name="Data",
                showlegend=True,
            )
        )

        html_fname = f"multistart_plot_for_{result.sanitised_name}.html"
        Plot.write_html_with_link_plotlyjs(
            fig, figures_dir, html_fname, options
        )
        return html_fname

    @staticmethod
    def plot_2d_data(categories, title, options, figures_dir) -> str:
        """
        Show 2d plots for 2d data fitting, with contour plots.
        One plot is shown for the best minimizer for each cost function.

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
        subp_titles = []

        for categ_key, results in categories.items():
            for result in results:
                if (
                    result.plot_info is None
                    or "plot_type" not in result.plot_info
                ):
                    pass
                elif (
                    result.plot_info["plot_type"] == "2d"
                    and result.is_best_fit
                ):
                    subp_titles.extend([f"{categ_key}: {result.minimizer} "])

        # If no 2d result has been found in the above loop, don't create plot
        if len(subp_titles) == 0:
            return ""

        # Limit width of plot if only 1 subplot
        width = None
        if n_categs < 2:
            width = 600

        fig = make_subplots(
            rows=1,
            cols=n_categs,
            shared_yaxes=True,
            horizontal_spacing=0.1,
            subplot_titles=subp_titles,
        )

        for ind, (categ_key, results) in enumerate(categories.items(), 1):
            for result in results:
                if (
                    result.plot_info["plot_type"] == "2d"
                    and result.is_best_fit
                    and hasattr(result, "fin_y_complete")
                ):
                    img = np.rot90(result.fin_y_complete.T, k=4)
                    fig.add_trace(
                        px.imshow(img).data[0],
                        row=1,
                        col=ind,
                    )
                    # Add contour plots on top
                    fig.add_trace(
                        go.Contour(
                            z=img,
                            contours_coloring="lines",
                            line_width=2,
                            visible="legendonly",
                            showscale=False,
                            showlegend=True,
                            name=f"{categ_key} contour",
                        ),
                        row=1,
                        col=ind,
                    )

                    y_tickvals = None
                    y_ticktext = None
                    y_axis_title = None
                    x_tickvals = None
                    x_ticktext = None
                    x_axis_title = None

                    # check if problem if it's SpinW data
                    if "ebin_cens" in result.plot_info:
                        # set y tick vals and text
                        n_ticks = 6
                        ebin_cens = result.plot_info["ebin_cens"]
                        y_ticktext = np.round(
                            np.linspace(ebin_cens[0], ebin_cens[-1], n_ticks),
                            2,
                        )
                        y_tickvals = np.linspace(0, np.shape(img)[0], n_ticks)
                        y_axis_title = "Energy (meV)"

                        # set x tick vals and text
                        modQ_cens = result.plot_info["modQ_cens"]
                        x_ticktext = np.round(
                            np.linspace(modQ_cens[0], modQ_cens[-1], n_ticks),
                            2,
                        )
                        x_tickvals = np.linspace(0, np.shape(img)[1], n_ticks)
                        x_axis_title = "|Q| (Å<sup>-1</sup>)"

                    fig.update_yaxes(
                        title_text=y_axis_title,
                        tickmode="array",
                        tickvals=y_tickvals,
                        ticktext=y_ticktext,
                        row=1,
                        col=ind,
                    )
                    fig.update_xaxes(
                        title_text=x_axis_title,
                        tickmode="array",
                        tickvals=x_tickvals,
                        ticktext=x_ticktext,
                        row=1,
                        col=ind,
                    )

        fig.update_layout(
            title=title + ": 2d plots",
            width=width,
            legend={
                "orientation": "v",
                "yanchor": "bottom",
                "y": -0.3,
                "xanchor": "center",
                "x": 0.5,
            },
        )
        fig.update_coloraxes(colorscale="viridis")

        html_fname = f"2d_plots_for_best_minims_{result.sanitised_name}.html"
        Plot.write_html_with_link_plotlyjs(
            fig, figures_dir, html_fname, options
        )
        return html_fname

    @staticmethod
    def _create_empty_residuals_plots(categories, subplot_titles) -> go.Figure:
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
            lambda a: (
                a.update(x=-0.08, textangle=-90)
                if a.text in row_titles
                else ()
            )
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
            self._update_axes_titles(fig=fig, col_ind=i, ax_titles=ax_titles)

        return fig

    @staticmethod
    def _add_residual_traces(
        fig, result, n_plots_per_row, colour, row_ind
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
        if hasattr(result, "r_x_cuts"):
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

    @staticmethod
    def _check_data_len(x_data: np.ndarray, y_data: np.ndarray) -> None:
        """
        Checks x and y data have same length and raises error if not.

        :param x_data: The x axis data
        :type x_data: np.ndarray
        :param y_data: The y axis data
        :type y_data: np.ndarray
        """
        if len(y_data) != len(x_data):
            raise PlottingError("x and y data lengths are not the same")

    @staticmethod
    def _update_axes_titles(
        fig: go.Figure, col_ind: int, ax_titles: dict, row_ind: int = 1
    ) -> go.Figure:
        """
        Sets the titles of x and y axes.
        For space reasons, only sets the y axis title of the plot on the very
        left, as this will be the same in the other plots.

        :param fig: The plotly figure to add the traces to
        :type fig: plotly.graph_objects.Figure
        :param col_ind: Index of the column (subplot) we are
                        adding ax titles to
        :type col_ind: int
        :param ax_titles: Titles for each axis
        :type ax_titles: dict[str, str]
        :param row_ind: Index of the row (subplot) we are
                        adding ax titles to
        :type row_ind: int

        :return: Updated plot
        :rtype: plotly.graph_objects.Figure
        """
        if col_ind == 0:
            fig.update_yaxes(
                title_text=ax_titles["y"], row=row_ind, col=col_ind + 1
            )
        fig.update_xaxes(
            title_text=ax_titles["x"], row=row_ind, col=col_ind + 1
        )
        return fig

    @staticmethod
    def _update_to_logscale_if_needed(fig, result) -> go.Figure:
        """
        Updates logscale to log if this is specified in result.plot_scale.

        :param fig: The plotly figure to update the axis for
        :type fig: plotly.graph_objects.Figure
        :param result: Result for which axis needs to be updated.
        :type result: FittingResult

        :return: Updated plot
        :rtype: plotly.graph_objects.Figure
        """
        if result.plot_scale in ["loglog", "logx"]:
            fig.update_xaxes(type="log")
        if result.plot_scale in ["loglog", "logy"]:
            fig.update_yaxes(type="log")
        return fig

    @staticmethod
    def _sample_colours(points: np.ndarray) -> list[str]:
        """
        Samples plotly colours based on values passed as input.

        :param points: A list of evenly spaced values between 0 and 1
        :type points: np.ndarray

        :return: The list of sampled colours
        :rtype: list[str]
        """
        plotly_colours = ptly_colors.sample_colorscale(
            ptly_colors.sequential.Rainbow, samplepoints=points
        )
        return plotly_colours

    @staticmethod
    def _get_n_plots_and_titles(result) -> tuple[int, Optional[str], str]:
        """
        A helper method that returns number of plots, subplot titles
        and axis titles.

        :param result: Result for which plot and title information
                       needs to be extracted.
        :type result: FittingResult

        :return: The number of plots, subplot titles and axis titles
        :rtype: tuple[int, Optional[str], str]
        """
        if result.plot_info is not None:
            return (
                result.plot_info["n_plots"],
                result.plot_info["subplot_titles"],
                result.plot_info["ax_titles"],
            )
        return 1, None, Plot._default_ax_titles
