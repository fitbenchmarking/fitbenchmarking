import inspect
import os

from dash import Dash, Input, Output, State

import fitbenchmarking
from fitbenchmarking.results_processing.compare_scatter_data_model import (
    CompareScatterDataModel,
)
from fitbenchmarking.results_processing.compare_scatter_view import (
    CompareScatterView,
)


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

        multiple_cost_funcs_in_use = (
            len(self.model.get_values_from_results("costfun_tag", unique=True))
            > 1
        )

        hover_text = [
            text + "<extra></extra>"
            for text in self.model.get_values_from_results(
                "hover_text",
                include_title=True,
                style="html",
                include_cost_func=multiple_cost_funcs_in_use,
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
