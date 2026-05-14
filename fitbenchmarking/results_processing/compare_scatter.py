import plotly.colors
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from plotly.validator_cache import ValidatorCache

from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.misc import get_hover_text

# from fitbenchmarking.utils.fitbm_result import FittingResult


class CompareScatter:
    """
    Class to handle the data processing for a compare scatter
    """

    def __init__(self, results=[]):
        """
        Initialise the compare_scatter class.
        """
        self.results = results
        self.view = CompareScatterView()
        self.model = CompareScatterDataModel(results)

        # self.controller = compare_scatter_controller()
        # most of the interface is just get plot from the view

    def get_layout(self):
        default_x = "norm_runtime"
        default_y = "norm_acc"

        return self.view.get_plot(
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


class CompareScatterView:
    """
    Class to handle the basic plotting of a compare scatter
    """

    # dict of internal Fitting Result attribute names, and the human readable
    # name that should be visible on the user interface

    def __init__(self):
        self.valid_symbols = self.get_all_valid_symbols()

    def get_plot(
        self, x, y, x_title, y_title, tooltips, errors, solvers, problems
    ):
        errors = [
            f"<sup><b>{flag}</b></sup>" if flag != 0 else "" for flag in errors
        ]

        colour_groups = plotly.colors.sample_colorscale(
            colorscale="mrybm",
            # since the scale is cyclical, we take an extra sample to leave
            # some space between the first and last colour
            samplepoints=len(dict.fromkeys(solvers)) + 1,
        )

        valid_symbols = self.get_all_valid_symbols()

        plot = px.scatter(
            x=x,
            y=y,
            color=solvers,
            symbol=problems,
            symbol_sequence=valid_symbols,
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
        return [
            dcc.Graph(figure=plot),
            self.get_legend(
                plot, problems, valid_symbols, solvers, colour_groups
            ),
        ]

    def get_legend(
        self, plot, symbol_groups, symbol_map, colour_groups, colour_map
    ):
        unique_symbol_groups = dict.fromkeys(symbol_groups)
        unique_colour_groups = dict.fromkeys(colour_groups)

        legend = []

        legend.append(html.H1("Problem"))
        for i, symbol_mapped_value in enumerate(unique_symbol_groups):
            legend_item = html.Button(
                [
                    self.get_isolated_symbol(symbol=symbol_map[i]),
                    f" - {symbol_mapped_value}",
                ],
                style={"display": "flex"},
            )
            legend.append(legend_item)
            legend.append(html.Br())

        legend.append(html.H1("Minimizer"))
        for i, color_mapped_value in enumerate(unique_colour_groups):
            legend_item = html.Button(
                [
                    self.get_isolated_symbol(colour=colour_map[i]),
                    f" - {color_mapped_value}",
                ],
                style={"display": "flex"},
            )
            legend.append(legend_item)
            legend.append(html.Br())

        return html.Div(legend)

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

    def get_minimizer_names(self):
        values = [
            result.modified_minimizer_name(True) for result in self.results
        ]
        return values

    def get_report_page_URLs(self):
        pass
        # link_array = []
        # for result in self.results:
        #     link_array.append(result.)
        # return link_array

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
