import inspect
import numbers
import os
import re
from dataclasses import dataclass

import dash_bootstrap_components as dbc
import numpy as np
import plotly.colors
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html, set_props
from lxml import etree
from lxml import html as xml_html
from plotly.validator_cache import ValidatorCache

import fitbenchmarking
from fitbenchmarking.utils.fitbm_result import FittingResult


class CompareScatter:
    """
    The compare scatter plots every fitting result on a dash plot.
    Note: The comparison scatter plot will only function while dash is running.

    The comparison scatter has a two column legend. If only items from one
    column are selected, then the union of all valid points are highlighted.
    If items from both columns are selected, then the intersection of the two
    columns will be highlighted.

    Clicking on a point will take you to the fitting report page for that
    point.
    """

    script_path = (
        os.path.dirname(inspect.getfile(fitbenchmarking))
        + "/results_processing/scripts/compare_scatter"
    )

    def __init__(self, app: Dash, options, results=[]):
        """
        Initialise the compare_scatter class and MVC components.
        """
        self.results = results
        self.model = CompareScatterDataModel(results)
        self.view = CompareScatterView()
        self.app = app
        self.options = options

    def item_should_have_warning_toast(self, item):
        """
        Given a string name of a minimizer, return a bool representing if it
        failed to complete at least one problem (i.e. it had and error flag of
        3)

        :param item: the minimizer to check
        :type item: str

        :return: whether that item threw any errors
        :rtype: bool
        """
        errors, _ = self.view.get_per_minimizer_errors_and_runs(
            error_flags=self.model.get_values_from_results("error_flag"),
            minimizer_names=self.model.get_values_from_results(
                "modified_minimizer_name", with_software=True
            ),
        )
        if item in errors:
            return bool(errors[item])
        else:
            return False

    def add_legend_callbacks(self, legend_items: list[str]):
        """
        Given a list of legend items, add a callback for each ID to allow it to
        set the focus of the appropriate traces.

        :param legend_items: A list of minimizer names or IDs
        :type legend_items: list[str]
        """

        for i, legend_item in enumerate(legend_items):
            button_id = self.view.sanitize_for_id(legend_item)
            button_io: list = [
                Output("compare_scatter", "figure", allow_duplicate=True),
                Output("legend-status", "data", True),
                Output(button_id, "style"),
                Output("all_button", "style", True),
                Output("none_button", "style", True),
            ]

            has_run_failures = self.item_should_have_warning_toast(legend_item)

            if has_run_failures:
                button_io.append(Output(f"{button_id}_toast", "is_open", True))

            button_io.extend(
                [
                    Input(button_id, "n_clicks"),
                    State("legend-status", "data"),
                ]
            )

            def focus_callback(
                _,
                state,
                return_new_state=has_run_failures,
                group=legend_item,
            ):
                new_state, state = self.view.toggle_group_state(group, state)
                new_style = (
                    self.view.active_button_style
                    if new_state
                    else self.view.inactive_button_style
                )
                plot = self.view.apply_state(self.view.plot, state)
                all_button_style, none_button_style = (
                    self.view.get_all_none_button_style(state)
                )
                if return_new_state:
                    return (
                        plot,
                        state,
                        new_style,
                        all_button_style,
                        none_button_style,
                        new_state,
                    )
                else:
                    return (
                        plot,
                        state,
                        new_style,
                        all_button_style,
                        none_button_style,
                    )

            self.app.callback(
                button_io,
                prevent_initial_call=True,
            )(focus_callback)

    def add_all_none_button_callbacks(self):
        """
        Add a callback for the select all and select none buttons on the legend
        to allow them to manage the focus of all items on the legend.
        """

        self.app.callback(
            Output("legend-status", "data", True),
            Output("all_button", "style", True),
            Output("none_button", "style", True),
            Output("compare_scatter", "figure", True),
            Input("none_button", "n_clicks"),
            State("legend-status", "data"),
            prevent_initial_call=True,
        )(
            lambda _, state, plot=self.view.plot: (
                self.view.set_focus_for_all_items(plot, False, state)
            )
        )

        self.app.callback(
            Output("legend-status", "data", True),
            Output("all_button", "style", True),
            Output("none_button", "style", True),
            Output("compare_scatter", "figure", True),
            Input("all_button", "n_clicks"),
            State("legend-status", "data"),
            prevent_initial_call=True,
        )(
            lambda _, state, plot=self.view.plot: (
                self.view.set_focus_for_all_items(plot, True, state)
            )
        )

    def add_axis_dropdown_callbacks(self):
        """
        Add the callbacks required for x-dropdown and y-dropdown to change
        the data plotted on each axis when a different metric to be plotted
        is selected from the available list.
        """
        self.app.callback(
            Output("compare_scatter", "figure", True),
            Input("x-dropdown", "value"),
            prevent_initial_call=True,
        )(
            lambda value, model=self.model, view=self.view: (
                view.update_axes_data(
                    x_title=value,
                    x_data=model.get_values_from_results(
                        model.get_attr_from_readable_name(value)
                    ),
                )
                if value is not None
                else view.plot
            )
        )

        self.app.callback(
            Output("compare_scatter", "figure", True),
            Input("y-dropdown", "value"),
            prevent_initial_call=True,
        )(
            lambda value, model=self.model, view=self.view: (
                view.update_axes_data(
                    y_title=value,
                    y_data=model.get_values_from_results(
                        model.get_attr_from_readable_name(value)
                    ),
                )
                if value is not None
                else view.plot
            )
        )

    def add_log_axis_button_callbacks(self):
        """
        Add the callbacks required to allow the x and y-log-axis buttons to
        switch the axis type between linear and log.
        """

        self.app.callback(
            Output("compare_scatter", "figure", True),
            Input("x-log-axis", "value"),
            prevent_initial_call=True,
        )(
            lambda value, view=self.view: (
                view.plot.update_xaxes(type="log")
                if "Log axis" in value
                else view.plot.update_xaxes(type="linear")
            )
        )

        self.app.callback(
            Output("compare_scatter", "figure", True),
            Input("y-log-axis", "value"),
            prevent_initial_call=True,
        )(
            lambda value, view=self.view: (
                view.plot.update_yaxes(type="log")
                if "Log axis" in value
                else view.plot.update_yaxes(type="linear")
            )
        )

    def add_clickthrough_link_callback(self):
        """
        Add the clientside callback required to handle the clickthrough link
        behaviour for the compare scatter. I.e. clicking on a point should
        navigate the parent window to the relevant fitting report page.
        """

        with open(f"{self.script_path}/handle_link.js") as file:
            self.app.clientside_callback(
                file.read(),
                Output("dummy-click", "children"),
                Input("compare_scatter", "clickData"),
            )

    def add_resize_callback(self):
        """
        Add the clientside callback to send the window height information from
        inside the compare scatter iframe to the parent window, which allows
        the iframe to be scaled correctly when resized.
        """

        with open(f"{self.script_path}/resize_observer.js") as file:
            self.app.clientside_callback(
                file.read(),
                Output("dummy-height", "children"),
                Input("resize-timer", "n_intervals"),
                prevent_initial_call=False,
            )

    def add_callbacks(self, legend_items: list[str]):
        """
        Given a list of legend items, add all of the required callbacks for
        the compare scatter.

        :param legend_items: A list of minimizer names or IDs
        :type legend_items: list[str]
        """
        self.add_legend_callbacks(legend_items)
        self.add_all_none_button_callbacks()
        self.add_axis_dropdown_callbacks()
        self.add_log_axis_button_callbacks()

        self.add_clickthrough_link_callback()
        self.add_resize_callback()

    def get_fitting_report_urls(self):
        """
        Get the fitting report URLs and format as required for use as links
        :return: List of URLS
        :rtype: list[str]
        """
        return [
            "support_pages/" + val.split("support_pages/", 1)[1]
            if val != ""
            else "index.html"
            for val in self.model.get_values_from_results(
                "fitting_report_link"
            )
        ]

    def get_layout(self):
        """
        Get the compare scatter and set all of the required callbacks

        :return: A tuple of:
                 - The plot Div
                 - The app with callbacks added
        :rtype: tuple[html.Div, Dash]
        """
        default_x = "norm_runtime"
        default_y = "norm_acc"
        # hover text needs to have the <extra/> tag to remove the grey box
        # that would normally show the trace name
        hover_text = [
            text + "<extra></extra>"
            for text in self.model.get_values_from_results(
                "hover_text", include_title=True, style="html"
            )
        ]

        plot = self.view.get_plot(
            x=self.model.get_values_from_results(default_x),
            x_title=self.model.get_readable_attr_name(default_x),
            y=self.model.get_values_from_results(default_y),
            y_title=self.model.get_readable_attr_name(default_y),
            tooltips=hover_text,
            errors=self.model.get_values_from_results("error_flag"),
            minimizers=self.model.get_values_from_results(
                "modified_minimizer_name", with_software=True
            ),
            problems=self.model.get_values_from_results("problem_tag"),
            report_pages=self.get_fitting_report_urls(),
            plottable_attributes=[
                self.model.get_readable_attr_name(attr)
                for attr in self.model.get_plottable_attributes()
            ],
        )

        legend_items = [
            *self.model.get_values_from_results(
                "modified_minimizer_name", unique=True, with_software=True
            ),
            *self.model.get_values_from_results("problem_tag", unique=True),
        ]

        self.add_callbacks(legend_items)

        return plot, self.app


class CompareScatterView:
    """
    Class to handle the basic plotting of a compare scatter, in most cases use
    the CompareScatter class instead
    """

    # Index in customdata where the hover text for each point is stored
    DATA_HOVER_TEXT_INDEX = 0

    # Index in customdata where the minimizer name for each point is stored
    DATA_MINIMIZER_INDEX = 1

    # Index in customdata where the problem name for each point is stored
    DATA_PROBLEM_INDEX = 2

    # Note: index 3 maps each point to the URL of the relevant fitting report
    # page. This is accessed in handle_link.js

    # Index in customdata where each point's original position in the source
    # data is stored
    DATA_SOURCE_INDEX = 4

    banned_prefixes = [
        "circle-",  # limited readability
        "arrow",  # is offset from actual point
        "triangle-down",  # rotation
        "triangle-left",  # rotation
        "triangle-right",  # rotation
        "triangle-nw",  # rotation
        "triangle-ne",  # rotation
        "triangle-sw",  # rotation
        "triangle-se",  # rotation
        "hexagon",  # too close to circle at low zoom
        "octagon",  # too close to circle at low zoom
        "star-triangle-up",  # rotation
        "y-down",  # rotation
        "y-left",  # rotation
        "y-right",  # rotation
        "line-ew",  # rotation
        "line-ns",  # rotation
    ]

    active_opacity = 1
    inactive_opacity = 0.2

    active_error_template = (
        f"""<sup style="opacity:{active_opacity}">"""
        """<b>{0}</b></sup>"""
    )

    inactive_error_template = (
        f"""<sup style="opacity:{inactive_opacity}">"""
        """<b>{0}</b></sup>"""
    )

    active_button_style = {
        "display": "flex",
        "background-color": "white",
        "border": "none",
        "opacity": 1,
        "text-align": "left",
    }

    inactive_button_style = {
        "display": "flex",
        "background-color": "white",
        "border": "none",
        "opacity": 0.5,
        "text-align": "left",
    }

    def __init__(self):
        """
        Create the CompareScatterView and set the list of valid symbols
        """
        self.valid_symbols = self.get_all_valid_symbols()

    def get_plot(
        self,
        x: list[int],
        y: list[int],
        x_title: str,
        y_title: str,
        tooltips: list[list[str]],
        errors: list[int],
        minimizers: list[str],
        problems: list[str],
        report_pages: list[str],
        plottable_attributes: list[str],
    ):
        """
        Get a div containing the compare scatter and legend.
        Note that it has the side effect of setting self.plot for the class as
        well as returning the plot in a Div.

        When an argument is a list, it should have the same dimensions and same
        ordering as the x and y values - i.e. if x = [1,2,3] then tooltips =
        ["x:1","x:2","x:3"]

        :param x: values to plot on the X axis
        :type x: list[int]
        :param y: values to plot on the Y axis
        :type y: list[int]
        :param x_title: title for the X axis
        :type x_title: str
        :param y_title: title for the Y axis
        :type y_title: str
        :param tooltips: list of text to be used as hover text
        :type tooltips: list[list[str]]
        :param errors: list of fitting result error flags
        :type errors: list[int]
        :param minimizers: list of minimizer names
        :type minimizers: list[str]
        :param problems: list of problem names
        :type problems: list[str]
        :param report_pages: list of urls of fitting reports
        :type report_pages: list[str]
        :param plottable_attributes: A list of human readable names for
            attributes that can be plotted on the scatter plot.
        :type plottable_attributes: list[str]

        :return: Returns a div containing the plot and legend
        :rtype: html.Div
        """
        colour_groups = plotly.colors.sample_colorscale(
            colorscale="mrybm",
            # since the scale is cyclical, we take an extra sample to leave
            # some space between the first and last colour
            samplepoints=len(dict.fromkeys(minimizers)) + 1,
        )

        error_superscripts = [
            self.active_error_template.format(flag) if flag != 0 else ""
            for flag in errors
        ]

        # since plotly may reorganise points to group them into traces when
        # there are multiple points under one minimizer problem pairing (e.g.
        # when we have run with multiple cost functions selected), we need to
        # keep track of where in the data array that point came from by storing
        # it in the customdata field of the point. This means that later when
        # we need to make edits to what is being plotted, we are able to
        # correctly place the information in self.plot.data
        data_locations = list(range(len(x)))

        self.plot = px.scatter(
            x=x,
            y=y,
            color=minimizers,
            symbol=problems,
            symbol_sequence=self.valid_symbols,
            custom_data=[
                tooltips,
                minimizers,
                problems,
                report_pages,
                data_locations,
            ],
            log_x=True,
            log_y=True,
            text=error_superscripts,
            color_discrete_sequence=colour_groups,
        )

        self.plot.update_layout(xaxis_title=x_title, yaxis_title=y_title)
        self.plot.update_layout(margin={"l": 0, "r": 10, "t": 10, "b": 0})
        self.plot.update_layout(hoverlabel={"bgcolor": "white"})
        self.plot.update_layout(scattermode="group", scattergap=0.5)
        self.plot.update_traces(
            hovertemplate=f"%{{customdata[{self.DATA_HOVER_TEXT_INDEX}]}}",
            textposition="middle right",
            marker={
                "line": {
                    "width": 0.6,
                    "color": "#e5ecf6",  # colour of plot background
                },
                "size": 13,
            },
            showlegend=False,
        )

        legend = self.get_legend(
            symbol_groups=problems,
            symbol_map=self.valid_symbols,
            colour_groups=minimizers,
            colour_map=colour_groups,
        )

        div_contents = [
            dcc.Store(id="page-load-trigger", data={"loaded": True}),
            html.Div(
                [
                    dcc.Graph(
                        figure=self.plot,
                        id="compare_scatter",
                        style={"flex": "1", "min-width": "66vw"},
                    ),
                    legend,
                ],
                style={"display": "flex", "overflow": "hidden"},
            ),
            html.Div(
                [
                    html.Div(
                        "X axis attribute:",
                        style={"padding-right": "5px", "padding-left": "5px"},
                    ),
                    html.Div(
                        [
                            dcc.Dropdown(
                                plottable_attributes,
                                value=[x_title],
                                id="x-dropdown",
                                clearable=False,
                                style={
                                    "width": "27ch",
                                },
                            ),
                            dcc.Checklist(
                                ["Log axis"],
                                ["Log axis"],
                                id="x-log-axis",
                                style={
                                    "padding-left": "5px",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "align-items": "center",
                        },
                    ),
                    html.Div(
                        "Y axis attribute:",
                        style={"padding-right": "5px", "padding-left": "5px"},
                    ),
                    html.Div(
                        [
                            dcc.Dropdown(
                                plottable_attributes,
                                value=[y_title],
                                id="y-dropdown",
                                clearable=False,
                                style={
                                    "width": "27ch",
                                },
                            ),
                            dcc.Checklist(
                                ["Log axis"],
                                ["Log axis"],
                                id="y-log-axis",
                                style={
                                    "padding-left": "5px",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "align-items": "center",
                        },
                    ),
                ],
                style={"float": "right"},
            ),
            # dummy divs needed for callbacks
            html.Div(id="dummy-click", style={"display": "none"}),
            html.Div(id="dummy-height", style={"display": "none"}),
            # run once a second for the first five seconds to resize as the
            # plot loads
            dcc.Interval(id="resize-timer", max_intervals=5),
        ]

        warning_messages = self.get_warning_text_for_results(
            errors, minimizers
        )
        toasts = self.create_warning_toasts(warning_messages)
        div_contents.extend(toasts)

        return html.Div(
            div_contents,
            id="compare_scatter_container",
        )

    def create_warning_toasts(self, warning_messages_by_minimizer):
        """
        Returns an array of dbc.Toasts. Only creates toasts for minimizers with
        warning messages.

        Each toast will have the returned ID of
        f"{sanitized_minimizer_name}_toast"

        :param warning_messages_by_minimizer: key: minimizer, value: warning
            message or None
        :type warning_messages_by_minimizer: dict[str, str | None]

        :return: A list containing the created dbc.Toast objects
        :rtype: list[dbc.Toast]
        """
        toasts = []
        for minimizer in warning_messages_by_minimizer:
            message = warning_messages_by_minimizer[minimizer]
            if message is not None:
                toasts.insert(
                    0,
                    dbc.Toast(
                        message,
                        id=f"{self.sanitize_for_id(minimizer)}_toast",
                        header="Warning",
                        is_open=False,
                        dismissable=True,
                        icon="warning",
                        duration=5000,
                        style={
                            "position": "fixed",
                            "top": 66,
                            "right": 10,
                            "width": 350,
                        },
                    ),
                )
        return toasts

    @staticmethod
    def get_per_minimizer_errors_and_runs(error_flags, minimizer_names):
        """
        Get two dictionaries, both using minimizer name as the key, the errors
        dictionary uses the number of runs with an error flag of 3 to calculate
        the value, and the runs dictionary uses the number of occurrences of
        the minimizer name in the minimizer_names list as the value.

        :param error_flags: list of error flags in same order as minimizer
            names
        :type error_flags: list[int]
        :param minimizer_names: list of minimizer names, including duplicates (
            e.g. ``["min1", "min1", "min2", "min2"]``) each instance represents
            one run of that minimizer
        :type minimizer_names: list[str]


        :return: A tuple of dictionaries, the first containing the number of
                 errors for each minimizer, and the second containing the
                 number of runs for each minimizer.
                 (errors, runs)
        :rtype: tuple[dict[str, int], dict[str, int]]
        """

        errors_by_minimizer = dict.fromkeys(minimizer_names, 0)
        runs_by_minimizer = dict.fromkeys(minimizer_names, 0)

        # create a dict containing the n fails and runs of each minimizer
        for i, minimizer in enumerate(minimizer_names):
            runs_by_minimizer[minimizer] += 1
            if error_flags[i] == 3:
                errors_by_minimizer[minimizer] += 1

        return errors_by_minimizer, runs_by_minimizer

    def update_axes_data(
        self, x_title=None, x_data=None, y_title=None, y_data=None
    ):
        """
        Update the data and title for the x and/or y axes of the plot.

        :param x_title: The new title for the x-axis, defaults to None
        :type x_title: str, optional
        :param x_data: The new data for the x-axis, defaults to None
        :type x_data: list, optional
        :param y_title: The new title for the y-axis, defaults to None
        :type y_title: str, optional
        :param y_data: The new data for the y-axis, defaults to None
        :type y_data: list, optional
        :return: The updated plot figure.
        :rtype: go.Figure
        """
        if x_title is not None:
            if x_data is None:
                raise ValueError(
                    "x_data must be provided when x_title is provided"
                )
            self.plot.update_layout(xaxis_title=x_title)

        if y_title is not None:
            if y_data is None:
                raise ValueError(
                    "y_data must be provided when y_title is provided"
                )
            self.plot.update_layout(yaxis_title=y_title)

        for trace in self.plot.data:
            if not isinstance(trace, go.Scatter):
                continue
            indices = [
                int(data[self.DATA_SOURCE_INDEX]) for data in trace.customdata
            ]
            if x_data is not None:
                trace.x = tuple(x_data[i] for i in indices)
            if y_data is not None:
                trace.y = tuple(y_data[i] for i in indices)

        return self.plot

    def get_warning_text_for_results(self, error_flags, minimizer_names):
        """
        Get the warning text for a minimizer, which changes depending on its
        the number of associated error flags with a value of 3.

        When no error flags with a value of 3 are found, it should set the
        warning text to None, otherwise it should create a string which tells
        the user what proportion of runs failed.

        :param error_flags: list of error flags in same order as minimizer
            names

        :type error_flags: list[int]

        :param minimizer_names: list of minimizer names, including duplicates (
            e.g. ``["min1", "min1", "min2", "min2"]``) each instance represents
            one run of that minimizer

        :type minimizer_names: list[str]

        :return: A dict where the key is the minimizer name, and the
            value is the warning text for that minimizer or None if none is
            needed

        :rtype: dict[str, str | None]
        """

        errors_by_minimizer, runs_by_minimizer = (
            self.get_per_minimizer_errors_and_runs(
                error_flags, minimizer_names
            )
        )
        warning_text_by_minimizer = dict.fromkeys(minimizer_names)

        # construct the error text
        for minimizer in warning_text_by_minimizer:
            n_failed = errors_by_minimizer[minimizer]
            n_runs = runs_by_minimizer[minimizer]

            if n_failed:
                if n_failed == n_runs:
                    warning_text_by_minimizer[minimizer] = (
                        "Warning: this minimizer failed to run on every "
                        "problem and could not be plotted."
                    )
                else:
                    warning_text_by_minimizer[minimizer] = (
                        f"Warning: this minimizer failed to run on "
                        f"{n_failed}/{n_runs} problems. Only successful runs"
                        " have been plotted."
                    )
        return warning_text_by_minimizer

    def set_focus_for_all_items(self, plot: go.Figure, focus, state):
        """
        Given a focus value and a dictionary of the state of each legend item
        set the focus for every point on the plot, return the plot with the new
        focus set, the updated dictionary with the state of each legend item,
        and the new style for the all/none buttons (which need to lose focus)
        whenever not every item is selected.

        the state dictionary should have the following structure:

        .. code:: python

            state = {
                "minimizer": {"minimizer_name":True},
                "problem": {"problem_name":True},
            }

        Here "focus" has been used to mean whether a minimizer is selected or
        not on the legend

        :param focus: The new focus state for all items
        :type focus: bool

        :param state: Dictionary with the structure described above
        :type state: dict[str, dict[str, bool]]

        :return: A tuple of the following
            - ``state`` the updated state dictionary
            - ``all_button_style`` the updated style for the select all button
            - ``none_button_style`` the updated style for the select all button
            - ``plot`` the plot after the traces have been updated
        :rtype: tuple[dict[str, dict[str, bool]],
                      dict[str, any],
                      dict[str, any],
                      go.Figure]
        """
        style = (
            self.active_button_style if focus else self.inactive_button_style
        )

        for item_type in state:
            for item in state[item_type]:
                state[item_type][item] = focus
                set_props(self.sanitize_for_id(item), {"style": style})

        plot = self.apply_state(plot, state, "all" if focus else "none")

        all_button_style = (
            self.active_button_style if focus else self.inactive_button_style
        )
        none_button_style = (
            self.active_button_style
            if not focus
            else self.inactive_button_style
        )
        return state, all_button_style, none_button_style, plot

    @staticmethod
    def toggle_group_state(group, state):
        """
        Given either a minimizer or a problem and a state dict in the format:

        .. code:: python

            state = {
                "minimizer": {"minimizer_name":True},
                "problem": {"problem_name":True},
            }

        Invert the current state and return the new state, including the
        dictionary with the new state now set

        :param group: The group to find in the state dictionary
        :type group: str
        :param state: The state dictionary to query and modify
        :type state: dict

        :return: A tuple containing:
                 - The state of the group after toggling
                 - The modified state dictionary
        :rtype: tuple[bool, dict]
        """
        if group in state["problem"]:
            group_state = not state["problem"][group]
            state["problem"][group] = group_state
        elif group in state["minimizer"]:
            group_state = not state["minimizer"][group]
            state["minimizer"][group] = group_state
        else:
            raise ValueError(f"Group '{group}' was not in state '{state}'")
        return group_state, state

    def get_all_none_button_style(self, state):
        """
        Given a dictionary of the state of each legend item, return the correct
        style for the select all and select none buttons.

        The state dict should be in the following format:

        .. code:: python

            state = {
                "minimizer": {"minimizer_name":True},
                "problem": {"problem_name":True},
            }

        :param state: Dictionary with the structure described above
        :type state: dict[str,dict[str,bool]]

        :return: A tuple of (all_button_style, none_button_style) where:
            - ``all_button_style`` is the updated style for the select all
            button
            - ``none_button_style`` is the updated style for the select none
            button

        :rtype: tuple[dict[str, any], dict[str, any]]
        """
        all_selected = all(state["minimizer"].values()) and all(
            state["problem"].values()
        )
        all_deselected = not any(state["minimizer"].values()) and not any(
            state["problem"].values()
        )
        all_button_style = (
            self.active_button_style
            if all_selected
            else self.inactive_button_style
        )
        none_button_style = (
            self.active_button_style
            if all_deselected
            else self.inactive_button_style
        )

        return all_button_style, none_button_style

    def apply_state(
        self, plot: go.Figure, state: dict, group: str | None = None
    ):
        """
        Given a state dictionary, and a plot, set the opacity on each trace
        of the plot to match the expected opacity for the state in the
        dictionary.

        if "all" or "none" is provided for the group parameter, then act like
        state was True for everything given the former or False for everything
        given the latter.

        the active and inactive opacities are set based on self.active_opacity
        and self.inactive_opacity

        :param plot: The plot to modify
        :type plot: go.Figure
        :param state: Dictionary of state of each problem, sorted by minimizer
                      and problem
        :type state: dict[str, dict[str, bool]]
        :param group: The group of points to set visibility for, either "all"
            or "none", all other values have no effect
        :type group: str
                      or "none".
        :type group: str | None

        :return: The modified plot
        :rtype: go.Figure
        """

        valid_group_types = ["all", "none"]
        if group is not None and group not in ["all", "none"]:
            raise ValueError(
                f"Apply state only supports group = {valid_group_types} or ",
                f"None, '{group}' was provided",
            )

        select_all = group == "all"
        deselect_all = group == "none"

        selected_minimizers = [
            g for g in state["minimizer"] if state["minimizer"][g]
        ]
        selected_problems = [
            g for g in state["problem"] if state["problem"][g]
        ]
        for t in plot.data:
            if deselect_all:
                visible = False
            elif select_all:
                visible = True
            else:
                assert type(t) is go.Scatter
                # uses type: ignore here because plotly defines customdata as
                # a list[float], but in our case it is a list[list[str]]
                # The documentation (linked below) shows how using customadata
                # to store information other than floats is idiomatic.
                # https://plotly.com/python/hover-text-and-formatting/
                # always select [0] here because each trace only has one point
                minimizer = t.customdata[0][self.DATA_MINIMIZER_INDEX]  # type: ignore
                problem = t.customdata[0][self.DATA_PROBLEM_INDEX]  # type: ignore
                if (
                    (
                        len(selected_problems) == 0
                        and minimizer in selected_minimizers
                    )
                    or (
                        len(selected_minimizers) == 0
                        and problem in selected_problems
                    )
                    or (
                        minimizer in selected_minimizers
                        and problem in selected_problems
                    )
                ):
                    visible = True
                else:
                    visible = False

            if visible:
                self.set_trace_opacity(t, self.active_opacity)
            else:
                self.set_trace_opacity(t, self.inactive_opacity)
        return plot

    @staticmethod
    def set_trace_opacity(t, new_opacity):
        """
        Given a trace, update the opacity of the text field and points.

        :param t: The trace to modify
        :type t: plotly trace
        :param new_opacity: the opacity after the change
        :type new_opacity: float
        """

        # set the opacity of the plotted trace
        t.marker["opacity"] = new_opacity

        if t.text is None:
            return

        texts = t.text if not isinstance(t.text, str) else (t.text,)
        new_texts = []
        for text in texts:
            if text:
                html_tree = xml_html.fromstring(text)
                html_tree.set("style", f"opacity:{new_opacity}")
                new_texts.append(etree.tostring(html_tree).decode("ascii"))
            else:
                new_texts.append(text)
        t.text = tuple(new_texts)

    def get_legend(self, symbol_groups, symbol_map, colour_groups, colour_map):
        """
        Receives a list of items which should be grouped by either symbol or
        colour and the colours/symbols they should be grouped by.
        Creates a legend using dash html components, that includes the name
        of each legend item and an icon representing each shape or colour.

        :param symbol_groups: The values which are used to group by symbol
        :type symbol_groups: list[str]
        :param symbol_map: A list of available symbols to use for grouping
        :type symbol_map: list[str]
        :param colour_groups: The values which are used to group by colour
        :type colour_groups: list[str]
        :param colour_map: A list of available colours to use for grouping
        :type colour_map: list[str]

        :return: A div containing the created legend
        :rtype: html.Div
        """

        unique_symbol_groups = list(dict.fromkeys(symbol_groups))
        unique_colour_groups = list(dict.fromkeys(colour_groups))

        legend_status = {"minimizer": {}, "problem": {}}

        problem_legend: list = [html.H3("Problem")]

        for i, symbol_mapped_value in enumerate(unique_symbol_groups):
            id = self.sanitize_for_id(symbol_mapped_value)

            legend_item = html.Button(
                [
                    self.get_point(symbol=symbol_map[i]),
                    symbol_mapped_value,
                ],
                style=self.active_button_style,
                id=self.sanitize_for_id(symbol_mapped_value),
            )

            legend_status["problem"][symbol_mapped_value] = True
            problem_legend.append(legend_item)
            problem_legend.append(html.Br())

        minimizer_legend: list = [html.H3("Minimizer")]

        for i, color_mapped_value in enumerate(unique_colour_groups):
            id = self.sanitize_for_id(color_mapped_value)

            item_title = []
            for section in re.split(r"(j:|h:)", color_mapped_value):
                if re.match(r"(j:|h:)", section) is not None:
                    item_title.append(html.Br())
                item_title.append(section)

            legend_item = html.Button(
                [
                    self.get_point(colour=colour_map[i]),
                    *item_title,
                ],
                style=self.active_button_style,
                id=id,
            )
            legend_status["minimizer"][color_mapped_value] = True
            minimizer_legend.append(legend_item)
            minimizer_legend.append(html.Br())

        all_none_buttons = html.Div(
            [
                html.Button(
                    "All", id="all_button", style=self.active_button_style
                ),
                html.Div("|", style={"font-weight": "bold"}),
                html.Button(
                    "None",
                    id="none_button",
                    style=self.inactive_button_style,
                ),
            ],
            style={
                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
            },
        )

        legend = [
            html.Div(problem_legend),
            html.Div(minimizer_legend),
            dcc.Store(id="legend-status", data=legend_status),
        ]

        complete_legend = html.Div(
            [
                html.Div(legend, style={"display": "flex", "gap": "10px"}),
                html.Div(all_none_buttons),
            ],
            id="compare_scatter_legend",
        )

        return complete_legend

    @staticmethod
    def sanitize_for_id(to_sanitize: str):
        """
        removes all non alphanumeric characters from the provided string

        :param to_sanitize: String to sanitize
        :type to_sanitize: str

        :return: Sanitized string
        :rtype: str
        """

        return "".join([char for char in to_sanitize if char.isalnum()])

    @staticmethod
    def get_point(symbol="circle-x", colour="rgba(150,150,150,1)"):
        """
        Get a html div containing a single point, which is an example of the
        provided input values. The point is non intractable, intended for
        use in legends and embedded within other elements.

        This is needed because plotly does not expose the shape objects for use
        in situations like these, which means that the only way we can display
        a single point with a specific symbol (such as you would see on the
        legend) is to actually plot it on a graph.

        :param symbol: Shape to give the point
        :type symbol: str
        :param colour: Colour to give the point
        :type colour: str

        :return: Div containing the generated symbol
        :rtype: html.Div
        """

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=[0],
                y=[0],
                marker={
                    "symbol": symbol,
                    "color": colour,
                    "line": {
                        "width": 1.5,
                        "color": "white",
                    },
                    "size": 12,
                },
            )
        )
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis={
                "range": [-0.01, 0.01],
                "visible": False,
                "showgrid": False,
                "zeroline": False,
                "fixedrange": True,
            },
            yaxis={
                "range": [-0.01, 0.01],
                "visible": False,
                "showgrid": False,
                "zeroline": False,
                "fixedrange": True,
                "scaleanchor": "x",
            },
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            width=15,
            height=15,
        )
        return html.Div(
            [dcc.Graph(figure=fig, config={"staticPlot": True})],
            style={
                "margin": "0",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
            },
        )

    def get_all_valid_symbols(self):
        """
        Filter the valid list of symbols for a plotly plot to only those which
        have been determined visually distinct enough to be presented on the
        plot.

        Filters according to self.is_banned_symbol.

        :return: list of visually distinct symbol names
        :rtype: list[str]:
        """

        validator = ValidatorCache.get_validator("scatter.marker", "symbol")
        # the validator returns values in the format:
        # int(ID), str(ID), str(name)
        # we only the string names, so we select every third value
        # (starting from the third)
        valid_symbols = validator.values[2::3]
        valid_symbols.sort(key=self.get_symbol_sort_key)
        valid_symbols = list(filter(self.is_valid_symbol, valid_symbols))
        return valid_symbols

    def is_valid_symbol(self, symbol: str):
        """
        Some types of symbols (specifically the ones with rotations) repeat
        too frequently with only minor changes, which reduces readability, so
        we need to remove them before display. This function filters out
        rotations and translations as determined by self.banned_prefixes

        :param symbol: Symbol to check
        :type symbol: str

        :return: returns true if the symbol so not banned
        :rtype: bool
        """

        return all(
            not symbol.startswith(prefix) for prefix in self.banned_prefixes
        )

    @staticmethod
    def get_symbol_sort_key(symbol: str):
        """
        Given a string, return an int priority. This function has been set up
        so that solid colour symbols are favoured over open symbols. It can be
        used to sort a list of symbols into an order based on which suffix
        they contain.

        :param symbol: The string to check
        :type symbol: str

        :return: a number representing how early it should appear in the sorted
            list 0 being the earliest

        :rtype: int
        """

        # prefer symbols with solid colours
        suffix_ranking = {"dot": 1, "open": 2, "open-dot": 3}
        for suffix in suffix_ranking:
            if symbol.endswith(suffix):
                return suffix_ranking[suffix]
        return 0


@dataclass(frozen=True)
class CompareScatterDataModel:
    results: list[FittingResult]

    def __post_init__(self):
        self.results.sort(key=self.get_sort_key)

    @staticmethod
    def get_sort_key(result: FittingResult):
        return result.name

    def get_plottable_attributes(self) -> list[str]:
        """
        Get a list of attributes that make logical sense to plot on a scatter
        plot. Works by reading all attributes of the FittingResults and
        removing any which return a non-numeric value.

        :return: list of attributes that can be plotted
        :rtype: list[str]
        """

        plottable_attributes = [
            "accuracy",
            "energy",
            "first_runtime",
            "func_evals",
            "get_n_data_points",
            "get_n_parameters",
            "harmonic_runtime",
            "iteration_count",
            "maximum_runtime",
            "mean_runtime",
            "median_runtime",
            "minimum_runtime",
            "norm_acc",
            "norm_energy",
            "norm_runtime",
            "runtime",
            "trim_runtime",
        ]

        return [
            attribute
            for attribute in plottable_attributes
            if self.list_contains_plottable_types(
                self.get_values_from_results(attribute)
            )
        ]

    _known_mappings = {
        "accuracy": "Accuracy (χ²)",
        "energy": "Energy (kWh)",
        "first_runtime": "First Runtime (s)",
        "func_evals": "N Function Evaluations",
        "harmonic_runtime": "Harmonic Runtime (s)",
        "maximum_runtime": "Maximum Runtime (s)",
        "mean_runtime": "Mean Runtime (s)",
        "median_runtime": "Median Runtime (s)",
        "minimum_runtime": "Minimum Runtime (s)",
        "norm_acc": "Normalised Accuracy",
        "norm_energy": "Normalised Energy",
        "norm_runtime": "Normalised Runtime",
        "runtime": "Runtime (s)",
        "trim_runtime": "Trimmed Mean Runtime (s)",
        "get_n_data_points": "N Data Points",
        "get_n_parameters": "N Parameters",
    }

    def get_readable_attr_name(self, attribute: str):
        """
        Given an attribute name, return a human readable name for use in the
        title text for the plot. This means in title case, with underscores
        replaced with spaces and units added if applicable and known.

        :param attribute: A machine readable name of an attribute
        :type attribute: str

        :return: The name of the attribute in a human readable format
        :rtype: str
        """
        if attribute in self._known_mappings:
            return self._known_mappings[attribute]
        return re.sub("_", " ", attribute).title()

    def get_attr_from_readable_name(self, name: str):
        """
        Given a human readable name, return the attribute name.

        :param name: A human readable name of an attribute
        :type name: str

        :return: The actual attribute name
        :rtype: str
        """
        for attr, readable_name in self._known_mappings.items():
            if readable_name == name:
                return attr
        # If not in known mappings, try to reverse the general conversion
        return name.lower().replace(" ", "_")

    @staticmethod
    def list_contains_plottable_types(values: list):
        """
        Return True if the provided list contains at least one numeric value,
        and is not entirely unplottable (i.e. np.inf)

        :param values: list of values to check
        :type values: list

        :return: if the list can be plotted on a scatter plot
        :rtype: bool
        """
        can_be_plotted = [
            (
                isinstance(value, numbers.Number)
                and not (value is np.nan or value is np.inf)
                and not isinstance(value, bool)
            )
            for value in values
        ]

        return any(can_be_plotted)

    def get_values_from_results(
        self, attribute: str, unique=False, **func_kwargs
    ) -> list:
        """
        Given the name of an attribute or method, retrieve the value of that
        attribute/method from each fitting result. Arguments can be passed to
        methods using func_kwargs.

        :param attribute: The attribute/method to get from every result stored
            in the data model
        :type attribute: str
        :param unique: Whether to return a list of only unique results or
            allow the list to include duplicates
        :type unique: bool
        :param func_kwargs: The arguments to send if the metric is callable
        :type func_kwargs: dict

        :return: List of values retrieved, presented in the order that the
            items appear in the model
        :rtype: list[any]
        """

        # in the case of name and normalized values, a function call is
        # required to retrieve the data, so we need to check if we have been
        # passed an attribute or method name

        values = []
        if attribute is None:
            raise ValueError("Attribute name cannot be None")
        if callable(getattr(self.results[0], attribute)):
            for result in self.results:
                func = getattr(result, attribute)
                values.append(func(**func_kwargs))
            if unique:
                values = list(dict.fromkeys(values))

        else:
            if func_kwargs:
                raise TypeError(
                    f"Attribute {attribute} is not callable, but "
                    "kwargs were provided"
                )

            values = [getattr(result, attribute) for result in self.results]
            if unique:
                values = list(dict.fromkeys(values))
        return values
