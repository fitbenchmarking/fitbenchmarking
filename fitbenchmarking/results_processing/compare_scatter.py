import re

import numpy as np
import plotly.colors
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html, set_props
from plotly.validator_cache import ValidatorCache

from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.misc import get_hover_text

# from fitbenchmarking.utils.fitbm_result import FittingResult


class CompareScatter:
    """
    Class to handle the data processing for a compare scatter
    """

    def __init__(self, app: Dash, results=[]):
        """
        Initialise the compare_scatter class.
        """
        self.results = results
        self.model = CompareScatterDataModel(results)
        self.view = CompareScatterView()
        self.app = app

        # self.controller = compare_scatter_controller()
        # most of the interface is just get plot from the view

    def add_callbacks(self, app: Dash, legend_items: list):
        if isinstance(self.view.plot, go.Figure):
            for legend_item in legend_items:
                button_id = self.view.sanitize_for_id(legend_item)

                # callback to edit the figure
                app.callback(
                    Output("compare_scatter", "figure", allow_duplicate=True),
                    Input(button_id, "n_clicks"),
                    State("legend-status", "data"),
                    prevent_initial_call=True,
                )(
                    lambda _, state, group=legend_item: self.view.focus_trace(
                        self.view.plot, state, group
                    )
                )

                # callback to edit the legend
                app.callback(
                    Output("legend-status", "data", True),
                    Output(button_id, "style"),
                    Output("all_button", "style", True),
                    Output("none_button", "style", True),
                    Input(button_id, "n_clicks"),
                    State("legend-status", "data"),
                    prevent_initial_call=True,
                )(
                    lambda _, state, group=legend_item: self.view.focus_legend(
                        group, state
                    )
                )

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

        else:
            print("warning plot type is:", type(self.view.plot))

        return app

    def get_layout(self):
        default_x = "norm_runtime"
        default_y = "norm_acc"
        plot = self.view.get_plot(
            x=self.model.get_values_for_axis(default_x),
            x_title=default_x,
            y=self.model.get_values_for_axis(default_y),
            y_title=default_y,
            tooltips=self.model.get_hover_text_for_results(),
            errors=self.model.get_values_for_axis("error_flag"),
            solvers=self.model.get_values_for_axis(
                "modified_minimizer_name", {"with_software": True}
            ),
            problems=self.model.get_values_for_axis("problem_tag"),
        )

        legend_items = self.model.get_unique_values_for_axis("problem_tag")
        legend_items.extend(
            self.model.get_unique_values_for_axis(
                "modified_minimizer_name", {"with_software": True}
            )
        )

        self.app = self.add_callbacks(self.app, legend_items)
        return plot, self.app


class CompareScatterView:
    """
    Class to handle the basic plotting of a compare scatter
    """

    # dict of internal Fitting Result attribute names, and the human readable
    # name that should be visible on the user interface
    def __init__(self):
        self.valid_symbols = self.get_all_valid_symbols()

    active_opacity = 1
    inactive_opacity = 0.3
    active_error_template = (
        f"""<sup style="opacity:{active_opacity}">"""
        """<b>{0}</b></sup>"""
    )
    inactive_error_template = (
        f"""<sup style="opacity:{inactive_opacity}">"""
        """<b>{0}</b></sup>"""
    )

    def get_plot(
        self, x, y, x_title, y_title, tooltips, errors, solvers, problems
    ):
        colour_groups = plotly.colors.sample_colorscale(
            colorscale="mrybm",
            # since the scale is cyclical, we take an extra sample to leave
            # some space between the first and last colour
            samplepoints=len(dict.fromkeys(solvers)) + 1,
        )

        errors = [
            self.active_error_template.format(flag) if flag != 0 else ""
            for flag in errors
        ]
        "('<sup style=\"opacity:', 1, '\"><b>3</b>', '</sup>')"
        plot = px.scatter(
            x=x,
            y=y,
            color=solvers,
            symbol=problems,
            symbol_sequence=self.valid_symbols,
            log_x=True,
            log_y=True,
            custom_data=[tooltips, solvers, problems],
            text=errors,
            color_discrete_sequence=colour_groups,
        )

        plot.update_layout(xaxis_title=x_title, yaxis_title=y_title)
        plot.update_layout(hoverlabel={"bgcolor": "white"})
        plot.update_traces(
            hovertemplate="%{customdata[0]}",
            textposition="middle right",
            marker={
                "line": {
                    "width": 0.6,
                    "color": "#e5ecf6",  # colour of plot background
                }
            },
            showlegend=False,
        )
        self.plot = plot

        legend = self.get_legend(
            symbol_groups=problems,
            symbol_map=self.valid_symbols,
            colour_groups=solvers,
            colour_map=colour_groups,
        )
        self.legend = legend

        return html.Div(
            [
                dcc.Graph(figure=self.plot, id="compare_scatter"),
                self.legend,
            ],
            style={"display": "flex"},
        )

    problem_legend = {}

    def set_focus_for_all_items(self, focus, state):
        style = (
            self.active_button_style if focus else self.inactive_button_style
        )
        plot = self.plot
        for item in state:
            state[item] = focus
            set_props(self.sanitize_for_id(item), {"style": style})

        plot = self.focus_trace(self.plot, state, "all" if focus else "none")

        all_button_style = (
            self.active_button_style if focus else self.inactive_button_style
        )
        none_button_style = (
            self.active_button_style
            if not focus
            else self.inactive_button_style
        )
        return state, all_button_style, none_button_style, plot

    def focus_legend(self, legend_item: str = "", state: dict = {}):

        all_button_style = None
        none_button_style = None
        new_style = None

        state[legend_item] = not state[legend_item]
        new_style = (
            self.active_button_style
            if state[legend_item]
            else self.inactive_button_style
        )

        all_selected = True
        all_deselected = True

        for group in state:
            if not state[group]:
                all_selected = False
            if state[group]:
                all_deselected = False

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

        return state, new_style, all_button_style, none_button_style

    def focus_trace(self, plot: go.Figure, state: dict, group: str):
        # we do a "in" check with tracename, since the legendgroup contains
        # both the problem and the solver in the same string
        select_all = group == "all"
        deselect_all = group == "none"
        bulk_operation = select_all or deselect_all

        for t in plot.data:
            if (
                isinstance(t, go.Scatter)
                and isinstance(t.marker, go.scatter.Marker)
                and isinstance(t.legendgroup, str)
                and (group in t.legendgroup or bulk_operation)
            ):
                if deselect_all or (not bulk_operation and state[group]):
                    t.marker.opacity = self.inactive_opacity
                    marker_text = t.text if t.text is not None else ""

                    if isinstance(marker_text, np.ndarray):
                        marker_text = "".join(marker_text)

                    t.text = re.sub(
                        f"opacity:{self.active_opacity}",
                        f"opacity:{self.inactive_opacity}",
                        str(marker_text),
                    )
                else:
                    t.marker.opacity = self.active_opacity
                    marker_text = t.text if t.text is not None else ""

                    if isinstance(marker_text, np.ndarray):
                        marker_text = "".join(marker_text)

                    t.text = re.sub(
                        f"opacity:{self.inactive_opacity}",
                        f"opacity:{self.active_opacity}",
                        str(marker_text),
                    )
        return plot

    active_button_style = {
        "display": "flex",
        "background-color": "white",
        "border": "none",
        "opacity": 1,
    }

    inactive_button_style = {
        "display": "flex",
        "background-color": "white",
        "border": "none",
        "opacity": 0.5,
    }

    def get_legend(self, symbol_groups, symbol_map, colour_groups, colour_map):

        unique_symbol_groups = dict.fromkeys(symbol_groups)
        unique_colour_groups = dict.fromkeys(colour_groups)

        legend = []
        legend_status = {}
        # legend.append(html.H1("Problem"))
        problem_legend = []
        problem_legend.append(html.H2("Problem"))
        for i, symbol_mapped_value in enumerate(unique_symbol_groups):
            legend_item = html.Button(
                [
                    self.get_isolated_symbol(symbol=symbol_map[i]),
                    f" - {symbol_mapped_value}",
                ],
                style=self.active_button_style,
                id=self.sanitize_for_id(symbol_mapped_value),
            )
            legend_status[symbol_mapped_value] = True
            problem_legend.append(legend_item)
            problem_legend.append(html.Br())

        minimiser_legend = []
        minimiser_legend.append(html.H2("Minimizer"))
        for i, color_mapped_value in enumerate(unique_colour_groups):
            legend_item = html.Button(
                [
                    self.get_isolated_symbol(colour=colour_map[i]),
                    f" - {color_mapped_value}",
                ],
                style=self.active_button_style,
                id=self.sanitize_for_id(color_mapped_value),
            )
            legend_status[color_mapped_value] = True
            minimiser_legend.append(legend_item)
            minimiser_legend.append(html.Br())

        legend.append(html.Div(problem_legend))
        legend.append(html.Div(minimiser_legend))
        minimiser_legend.append(
            html.Div(
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
        )
        legend.append(dcc.Store(id="legend-status", data=legend_status))

        return html.Div(legend, style={"display": "flex"})

    @staticmethod
    def sanitize_for_id(to_sanitize: str):
        return "".join([char for char in to_sanitize if char.isalnum()])

    @staticmethod
    def get_isolated_symbol(symbol="circle-x", colour="rgba(150,150,150,1)"):
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
            margin={"l": 0, "r": 0, "t": 2, "b": 0},
            width=15,
            height=15,
        )
        return dcc.Graph(figure=fig, config={"staticPlot": True})

    def get_all_valid_symbols(self):
        validator = ValidatorCache.get_validator("scatter.marker", "symbol")
        # the validator returns values in the format:
        # int(ID), str(ID), str(name)
        # we only want one of the three to eliminate duplicates, so we select
        # every third value (starting from the third so that we have the
        # strings for debugging)
        valid_symbols = validator.values[2::3]
        valid_symbols.sort(key=self.get_symbol_sort_key)
        valid_symbols = list(filter(self.is_banned_symbol, valid_symbols))
        return valid_symbols

    # some types of symbols (specifically the ones with rotations) repeat
    # too frequently with only minor changes, which reduces readability, so we
    # need to remove them before display
    @staticmethod
    def is_banned_symbol(symbol: str):
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
        return all(not symbol.startswith(prefix) for prefix in banned_prefixes)

    @staticmethod
    def get_symbol_sort_key(symbol: str):
        # prefer symbols with solid colours
        suffix_ranking = {"dot": 1, "open": 2, "open-dot": 3}
        for suffix in suffix_ranking:
            if symbol.endswith(suffix):
                return suffix_ranking[suffix]
        return 0


class CompareScatterDataModel:
    def __init__(self, results: list[FittingResult]):
        self.results = results
        # ensure consistent processing between runs
        self.results.sort(key=self.get_sort_key)

    @staticmethod
    def get_sort_key(result: FittingResult):
        return result.name

    def get_values_for_axis(self, metric: str, func_kwargs={}) -> list:
        # in the case of name and normalised values, a function call is
        # required to retreive the data, so we need to check if we have been
        # passed an attribute or method name
        if callable(getattr(self.results[0], metric)):
            funcs = [getattr(result, metric) for result in self.results]
            values = [func(**func_kwargs) for func in funcs]
        else:
            values = [getattr(result, metric) for result in self.results]
        return values

    def get_unique_values_for_axis(self, metric: str, func_kwargs={}) -> list:
        # in the case of name and normalised values, a function call is
        # required to retreive the data, so we need to check if we have been
        # passed an attribute or method name

        cache = f"_unique_cache_{metric}"
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
            values = list(dict.fromkeys(values))
        else:
            if cache_data is None:
                values = [getattr(result, metric) for result in self.results]
                values = list(dict.fromkeys(values))
                setattr(self, cache, values)
            else:
                values = cache_data
        return values

    def get_minimizer_names(self):
        values = [
            result.modified_minimizer_name(True) for result in self.results
        ]
        return values

    def get_report_page_URLs(self):
        pass

    def get_hover_text_for_results(self):
        # call util, and prepend the metrics being plotted
        text_array = [
            [
                get_hover_text(result, include_title=True, newline="<br>")
                + "<extra></extra>"
            ]  # removes grey box with trace name from plot
            for result in self.results
        ]
        return text_array
