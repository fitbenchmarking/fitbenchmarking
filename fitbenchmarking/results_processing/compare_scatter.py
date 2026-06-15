import inspect
import os

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
from fitbenchmarking.utils.misc import get_hover_text

# from fitbenchmarking.utils.fitbm_result import FittingResult


class CompareScatter:
    """
    The main interface for the compare scatter, also acts as the MVC controller
    for the compare scatter.
    """

    def __init__(self, app: Dash, options, results=[]):
        """
        Initialise the compare_scatter class and MVC components.
        """
        self.results = results
        self.model = CompareScatterDataModel(results)
        self.view = CompareScatterView()
        self.app = app
        self.options = options

        # self.controller = compare_scatter_controller()
        # most of the interface is just get plot from the view

    def item_should_have_warning_toast(self, item):
        """
        Given a string name of a minimizer, return a bool representing if it
        failed to complete at least one problem (i.e. it had and error flag of
        3)

        :param item: the minimizer to check
        :type str:

        :return: whether that item threw any errors
        :rtype bool:
        """
        errors, _ = self.view.get_per_minimizer_errors_and_runs(
            error_flags=self.model.get_values_for_axis("error_flag"),
            minimizer_names=self.model.get_values_for_axis(
                "modified_minimizer_name", with_software=True
            ),
        )
        if item in errors:
            return bool(errors[item])
        else:
            return False

    def add_callbacks(self, app: Dash, legend_items: list[str]):
        """
        Given a dash app and a list of legend items, add a callback for each
         ID to allow it to set the focus of the appropriate traces.

        Also add the required clientside callbacks to resize the iframe which
        contains the compare scatter at runtime, and to add the handling for
        the clickthrough links

        :param app: The existing dash app to add the callbacks to
        :type Dash:
        :param legend_items: A list of minimizer names or IDs
        :type list[str]:

        :return: The app with callbacks added
        :rtype Dash:
        """
        if isinstance(self.view.plot, go.Figure):
            for i, legend_item in enumerate(legend_items):
                button_id = self.view.sanitize_for_id(legend_item)
                button_io: list = [
                    Output("compare_scatter", "figure", allow_duplicate=True),
                    Output("legend-status", "data", True),
                    Output(button_id, "style"),
                    Output("all_button", "style", True),
                    Output("none_button", "style", True),
                ]

                has_run_failures = self.item_should_have_warning_toast(
                    legend_item
                )

                if has_run_failures:
                    button_io.append(
                        Output(f"{button_id}_toast", "is_open", True)
                    )

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
                    new_state, state = self.view.toggle_group_state(
                        group, state
                    )
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

                app.callback(
                    button_io,
                    prevent_initial_call=True,
                )(focus_callback)

            app.callback(
                Output("legend-status", "data", True),
                Output("all_button", "style", True),
                Output("none_button", "style", True),
                Output("compare_scatter", "figure", True),
                Input("none_button", "n_clicks"),
                State("legend-status", "data"),
                prevent_initial_call=True,
            )(lambda _, state: self.view.set_focus_for_all_items(False, state))

            app.callback(
                Output("legend-status", "data", True),
                Output("all_button", "style", True),
                Output("none_button", "style", True),
                Output("compare_scatter", "figure", True),
                Input("all_button", "n_clicks"),
                State("legend-status", "data"),
                prevent_initial_call=True,
            )(lambda _, state: self.view.set_focus_for_all_items(True, state))

            script_path = os.path.dirname(inspect.getfile(fitbenchmarking))
            script_path += "/results_processing/scripts/compare_scatter"

            with open(f"{script_path}/handle_link.js") as file:
                app.clientside_callback(
                    file.read(),
                    Output("dummy-click", "children"),
                    Input("compare_scatter", "clickData"),
                )

            with open(f"{script_path}/resize_observer.js") as file:
                app.clientside_callback(
                    file.read(),
                    Output("dummy-height", "children"),
                    Input("compare_scatter", "figure"),
                    prevent_initial_call=False,
                )

        else:
            raise ValueError(
                f"warning plot type is: {type(self.view.plot)} but go.Figure "
                "was expected"
            )
        return app

    def get_fitting_report_urls(self):
        """
        Get the fitting report URLs and format as required for use as links
        :return: List of URLS
        :rtype list[str]:
        """
        return [
            "support_pages/" + val.split("support_pages/", 1)[1]
            if val != ""
            else "index.html"
            for val in self.model.get_values_for_axis("fitting_report_link")
        ]

    def get_layout(self):
        """
        Get the compare scatter and set all of the required callbacks

        :return: The plot Div/List
        :rtype Div | list[]:
        :return: The app with callbacks added
        :rtype Dash:
        """
        default_x = "norm_runtime"
        default_y = "norm_acc"

        plot = self.view.get_plot(
            x=self.model.get_values_for_axis(default_x),
            x_title=default_x,
            y=self.model.get_values_for_axis(default_y),
            y_title=default_y,
            tooltips=self.model.get_hover_text_for_results(),
            errors=self.model.get_values_for_axis("error_flag"),
            minimizers=self.model.get_values_for_axis(
                "modified_minimizer_name", with_software=True
            ),
            problems=self.model.get_values_for_axis("problem_tag"),
            report_pages=self.get_fitting_report_urls(),
        )

        legend_items = self.model.get_values_for_axis(
            "modified_minimizer_name", unique=True, with_software=True
        )
        legend_items.extend(
            self.model.get_values_for_axis("problem_tag", unique=True)
        )

        self.app = self.add_callbacks(self.app, legend_items)
        return plot, self.app


class CompareScatterView:
    """
    Class to handle the basic plotting of a compare scatter, in most cases use
    the CompareScatter class instead
    """

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

    def __init__(self):
        """
        Create the CompareScatterView and set the list of valid symbols
        """
        self.valid_symbols = self.get_all_valid_symbols()

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
    ):
        """
        Get a div containing the compare scatter and legend.
        Not that has the side effect of setting self.plot for the class as well
        as returning the plot in a Div.

        When an argument is a list, it should have the same dimensions and same
        ordering as the x and y values - i.e. if x = [1,2,3] then tooltips =
        ["x:1","x:2","x:3"]

        :param x: values to plot on the X axis
        :type list[int]:
        :param y: values to plot on the Y axis
        :type list[int]:
        :param x_title: title for the X axis
        :type str:
        :param y_title: title for the Y axis
        :type str:
        :param tooltips: list of text to be used as hover text
        :type list[list[str]]:
        :param errors: list of fitting result error flags
        :type list[int]:
        :param minimizers: list of minimizer names
        :type list[str]:
        :param problems: list of problem names
        :type list[str]:
        :param report_pages: list of urls of fitting reports
        :type list[str]:

        :return Plot: A div containing the plot and legend
        :rtype html.Div:
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

        plot = px.scatter(
            x=x,
            y=y,
            color=minimizers,
            symbol=problems,
            symbol_sequence=self.valid_symbols,
            log_x=True,
            log_y=True,
            custom_data=[tooltips, minimizers, problems, report_pages],
            text=error_superscripts,
            color_discrete_sequence=colour_groups,
        )

        plot.update_layout(xaxis_title=x_title, yaxis_title=y_title)
        plot.update_layout(margin={"l": 0, "r": 10, "t": 10, "b": 0})
        plot.update_layout(hoverlabel={"bgcolor": "white"})
        plot.update_layout(scattermode="group", scattergap=0.5)

        plot.update_traces(
            hovertemplate="%{customdata[0]}",
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
        self.plot = plot
        legend = self.get_legend(
            symbol_groups=problems,
            symbol_map=self.valid_symbols,
            colour_groups=minimizers,
            colour_map=colour_groups,
        )
        self.legend = legend

        div_contents = [
            dcc.Store(id="page-load-trigger", data={"loaded": True}),
            dcc.Graph(
                figure=self.plot,
                id="compare_scatter",
                style={"flex": "1", "min-width": "0"},
            ),
            self.legend,
            # dummy divs needed for callbacks
            html.Div(id="dummy-click", style={"display": "none"}),
            html.Div(id="dummy-height", style={"display": "none"}),
        ]

        warning_messages = self.get_warning_text_for_results(
            errors, minimizers
        )
        toasts = self.create_warning_toasts(warning_messages)
        div_contents.extend(toasts)

        return html.Div(
            div_contents,
            style={"display": "flex", "overflow": "hidden"},
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
        :type dict[str,str|None]:

        :return Toasts: A list containing the created dbc.Toast objects
        :rtype list[dbc.Toast]:
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
        the value, and the runs dictionary uses the number of occurences of the
        minimizer name in the minimizer_names list as the value.

        :param error_flags: list of error flags in same order as minimizer
        names
        :type list[int]:
        :param minimizer_names: list of minimser names, including duplicates (
            e.g. ["min1", "min1", "min2", "min2"]) each instance represents one
            run of that minimizer
        :type list[str]:

        :return errors: A dict where the key is the minimizer name, and the
        value is the number of times that minimizer had an error flag of 3
        :rtype list[str,int]:
        :return runs: A dict where the key is the minimizer name, and the
        value is the number of times that minimizer ran
        :rtype list[str,int]:
        """

        errors_by_minimizer = dict.fromkeys(minimizer_names, 0)
        runs_by_minimizer = dict.fromkeys(minimizer_names, 0)

        # create a dict continaing the n fails and runs of each minimizer
        for i, minimizer in enumerate(minimizer_names):
            runs_by_minimizer[minimizer] += 1
            if error_flags[i] == 3:
                errors_by_minimizer[minimizer] += 1

        return errors_by_minimizer, runs_by_minimizer

    def get_warning_text_for_results(self, error_flags, minimizer_names):
        """
        Get the warning text for a minimizer, which changes depending on its
        the number of associated error flags with a value of 3.

        When no error flags with a value of 3 are found, it should set the
        warning text to None, otherwise it should create a string which tells
        the user what proportion of runs failed.

        :param error_flags: list of error flags in same order as minimizer
        names
        :type list[int]:
        :param minimizer_names: list of minimser names, including duplicates (
            e.g. ["min1", "min1", "min2", "min2"]) each instance represents one
            run of that minimizer
        :type list[str]:

        :return warnings: A dict where the key is the minimizer name, and the
        value is the warning text for that minimizer or None if none is needed
        :rtype list[str,int]:
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
                        f"{n_failed}/{n_runs} problems. Only succesful runs"
                        " have been plotted."
                    )
        return warning_text_by_minimizer

    problem_legend = {}

    def set_focus_for_all_items(self, focus, state):
        """
        Given a focus value and a dictionary of the state of each legend item
        set the focus for every point on the plot, return the plot with the new
        focus set, the updated dictionary with the state of each legend item,
        and the new style for the all/none buttons (which need to lose focus)
        whenever not every item is selected.

        the state dictionary should have the following structure:
        state = {
            "minimizer": {"minimizer_name":True},
            "problem": {"problem_name":True},
        }

        :param focus: The new focus state for all items
        :type bool:
        :param state: Dictionary with the structure described above
        :type dict[str,dict[str,bool]]:

        :return state: the updated state dictionary
        :rtype dict[str,dict[str,bool]]:
        :return all_button_style: the updated style for the select all button
        :rtype dict[str,any]:
        :return none_button_style: the updated style for the select all button
        :rtype dict[str,any]:
        :return plot: the plot after the traces have been updated
        :rtype go.Figure:
        """
        style = (
            self.active_button_style if focus else self.inactive_button_style
        )
        plot = self.plot
        for item_type in state:
            for item in state[item_type]:
                state[item_type][item] = focus
                set_props(self.sanitize_for_id(item), {"style": style})

        plot = self.apply_state(self.plot, state, "all" if focus else "none")

        all_button_style = (
            self.active_button_style if focus else self.inactive_button_style
        )
        none_button_style = (
            self.active_button_style
            if not focus
            else self.inactive_button_style
        )
        return state, all_button_style, none_button_style, plot

    def set_focus_for_group(self, group, state, return_new_state=False):
        pass

    @staticmethod
    def toggle_group_state(group, state):
        """
        Given either a minimizer or a problem and a state dict in the fromat:
        state = {
            "minimizer": {"minimizer_name":True},
            "problem": {"problem_name":True},
        }

        Invert the current state and return the new state, including the
        dictionary with the new state now set

        :param group: The group to find in the state dictionary
        :type str:
        :param state: The state dictionary to query and modify
        :type dict:

        :return new_state: The state of the group after toggling
        :rtype bool:
        :return new_state_dictionary: State, modified with the updated group
        :rtype dict:
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
        state = {
            "minimizer": {"minimizer_name":True},
            "problem": {"problem_name":True},
        }

        :param state: Dictionary with the structure described above
        :type dict[str,dict[str,bool]]:

        :return all_button_style: the updated style for the select all button
        :rtype dict[str,any]:
        :return none_button_style: the updated style for the select all button
        :rtype dict[str,any]:
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
        :type go.Figure:
        :param state: Dictionary of state of each problem, sorted by minimizer
        , problem
        :type dict[str,dict[str,bool]]:
        :param group: The group of points to set visiblity for, either "all" or
        "none", all other values have no effect
        :type str:

        :return plot: The modified plot
        :rtype go.Figure:
        """
        # we do a "in" check with tracename, since the legendgroup contains
        # both the problem and the minimizer in the same string

        valid_group_types = ["all", "none"]
        if group is not None and group not in ["all", "none"]:
            raise ValueError(
                f"Apply state only supports group = {valid_group_types}or None"
                ", '{group}' was provided"
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
                minimizer = t.customdata[0][1]  # type: ignore
                problem = t.customdata[0][2]  # type: ignore
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
        :type:
        :param new_opacity: the opacity after the change
        :type int:
        """
        t.marker.opacity = new_opacity

        if t.text is None or t.text == "":
            return

        marker_text = t.text
        if isinstance(marker_text, np.ndarray):
            marker_text = marker_text.item()

        html_tree = xml_html.fromstring(marker_text)
        html_tree.set("style", f"opacity:{new_opacity}")
        t.text = etree.tostring(html_tree).decode("ascii")

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

    def get_legend(self, symbol_groups, symbol_map, colour_groups, colour_map):
        """
        Given a list of items which should be grouped by either symbol or
        colour, and the colours/ symbols which they should be grouped by
        create a legend using dash html components, that includes the name
        of each legend item and an icon representing each hape or colour.

        :param symbol_groups: The values which are used to group by symbol
        :type list[str]:
        :param symbol_map: A list of available symbols to use for grouping
        :type list[str]:
        :param colour_groups: The values which are used to group by colour
        :type list[str]:
        :param colour_map: A list of available colours to use for grouping
        :type list[str]:

        :return complete_legend: A div containing the created legend
        :type html.Div:
        """

        unique_symbol_groups = list(dict.fromkeys(symbol_groups))
        unique_colour_groups = list(dict.fromkeys(colour_groups))

        legend = []
        legend_status = {"minimizer": {}, "problem": {}}

        problem_legend = []
        problem_legend.append(html.H2("Problem"))

        for i, symbol_mapped_value in enumerate(unique_symbol_groups):
            id = self.sanitize_for_id(symbol_mapped_value)
            legend_item = (
                html.Button(
                    [
                        self.get_point(symbol=symbol_map[i]),
                        f" - {symbol_mapped_value}",
                    ],
                    style=self.active_button_style,
                    id=self.sanitize_for_id(symbol_mapped_value),
                ),
            )
            legend_status["problem"][symbol_mapped_value] = True
            problem_legend.extend(legend_item)
            problem_legend.append(html.Br())

        minimizer_legend = []
        minimizer_legend.append(html.H2("Minimizer"))

        for i, color_mapped_value in enumerate(unique_colour_groups):
            id = self.sanitize_for_id(color_mapped_value)
            legend_item = html.Button(
                [
                    self.get_point(colour=colour_map[i]),
                    f" - {color_mapped_value}",
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

        legend.append(html.Div(problem_legend))
        legend.append(html.Div(minimizer_legend))
        legend.append(dcc.Store(id="legend-status", data=legend_status))

        complete_legend = html.Div(
            [
                html.Div(legend, style={"display": "flex"}),
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
        :type str:

        :return sanitized: Sanitized string
        :rtype str:
        """

        return "".join([char for char in to_sanitize if char.isalnum()])

    @staticmethod
    def get_point(symbol="circle-x", colour="rgba(150,150,150,1)"):
        """
        Get a html div containing a single point, which is an example of the
        provided input values. The point is non interactible, intended for
        use in legends and embeded within other elements.

        :param symbol: Shape to give the point
        :type str:
        :param colour: Colour to give the point
        :type str:

        :return symbol: Div containing the generated symbol
        :rtype html.Div:
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
                "position": "relative",
                "top": "50%",
                "transform": "translateY(25%)",
            },
        )

    def get_all_valid_symbols(self):
        """
        Filter the valid list of symbols for a plotly plot to only those which
        have been determined visually distinct enough to be peresented on the
        plot.

        Filters according to self.is_banned_symbol.

        :return valid_symbols: list of visually distincy symbol names
        :rtype list[str]:
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
        :type str:

        :return is_valid: true if the symbol so not banned
        :rtype bool:
        """

        return all(
            not symbol.startswith(prefix) for prefix in self.banned_prefixes
        )

    @staticmethod
    def get_symbol_sort_key(symbol: str):
        """
        Given a string, return an int priority. This function has been set up
        so that solid colour symbols are favourd over open symbols. It can be
        used to sort a list of symbols into an order based on which suffix
        they contain.

        :param symbol: The string to check
        :type str:

        :return ranking: how early it should appear in the sorted list
        0 being the earliest
        :rtype int:
        """

        # prefer symbols with solid colours
        suffix_ranking = {"dot": 1, "open": 2, "open-dot": 3}
        for suffix in suffix_ranking:
            if symbol.endswith(suffix):
                return suffix_ranking[suffix]
        return 0


class CompareScatterDataModel:
    def __init__(self, results: list[FittingResult]):
        """
        Initialise the data model for the compare scatter. This class sorts
        results by default so that the order of plotting does not change a lot
        between runs.

        :param results: list of Fitting results to use as the basis for this
        data model
        :type list[FittingResult]:
        """
        self.results = results
        # ensure consistent processing between runs
        self.results.sort(key=self.get_sort_key)

    @staticmethod
    def get_sort_key(result: FittingResult):
        return result.name

    def get_values_for_axis(
        self, metric: str, unique=False, **func_kwargs
    ) -> list:
        """
        Given a string (metric), retreive the value of that metric from each
        fitting result. Works for attributes and callables (with args able to
        be passed using func_kwargs).

        Note: this function caches the values provided to it, meaning that
        repeated calls do not cause signifigant slowdown. In the case of
        functions, it caches the function - not the return value, this still
        improves performance, but means that if the function output changes,
        the returned values are still correct.


        :param metric: The metric to get from every result in the model
        :type str:
        :param unique: Whether to return a list of only unique results or
        allow the list to include duplicates
        :type bool:
        :param func_kwargs: The arguments to send if the result is callable
        :type dict:
        """

        # in the case of name and normalised values, a function call is
        # required to retreive the data, so we need to check if we have been
        # passed an attribute or method name

        cache = f"_unique_cache_{metric}" if unique else f"_cache_{metric}"
        cache_data = getattr(self, cache, None)

        if callable(getattr(self.results[0], metric)):
            funcs = []
            # we cache the functions, not the data, as function output might
            # be expected to change
            if cache_data is None:
                for result in self.results:
                    func = getattr(result, metric)
                    funcs.append(func)
                setattr(self, cache, funcs)
            else:
                funcs = cache_data
            values = [func(**func_kwargs) for func in funcs]
            if unique:
                values = list(dict.fromkeys(values))
        else:
            if func_kwargs:
                raise TypeError(
                    f"Attribute {metric} is not callable, but "
                    "kwargs were provided"
                )
            if cache_data is None:
                values = [getattr(result, metric) for result in self.results]
                if unique:
                    values = list(dict.fromkeys(values))
                setattr(self, cache, values)
            else:
                values = cache_data
        return values

    def get_hover_text_for_results(self):
        """
        Get the hover text to display above each result and add the required
        formatting to display nicely on the plot.

        :return hover_text: list of hover text
        :rtype list[str]:
        """

        # call util, and prepend the metrics being plotted
        text_array = [
            [
                get_hover_text(result, include_title=True, newline="<br>")
                + "<extra></extra>"  # removes grey box with trace name
            ]
            for result in self.results
        ]
        return text_array
