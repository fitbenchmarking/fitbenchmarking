import plotly.express as px
from dash import dcc

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
        x = "norm_runtime"
        y = "norm_acc"
        return self.view.get_plot(
            x=self.model.get_values_for_axis(x),
            x_title=x,
            y=self.model.get_values_for_axis(y),
            y_title=y,
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

    def get_plot(
        self, x, y, x_title, y_title, tooltips, errors, solvers, problems
    ):
        errors = [
            f"<sup><b>{flag}</b></sup>" if flag != 0 else "" for flag in errors
        ]
        plot = px.scatter(
            x=x,
            y=y,
            color=solvers,
            symbol=problems,
            log_x=True,
            log_y=True,
            custom_data=[tooltips],
            text=errors,
            color_discrete_sequence=px.colors.qualitative.Dark24,
        )
        plot.update_layout(xaxis_title=x_title, yaxis_title=y_title)
        plot.update_layout(hoverlabel={"bgcolor": "white"})
        plot.update_traces(
            hovertemplate="%{customdata[0]}", textposition="middle right"
        )
        return dcc.Graph(figure=plot)


#     def make_html(self):
#         pass

#     def generate_custom_legend(self):
#         # create html element for legend, which groups based on problem set
#         # and based on solver, as two seperate lists.
#         pass


# class compare_scatter_controller:
#     """
#     Class to control the compare_scatter class.
#     """

#     def __init__(self):
#         """
#         Initialise the compare_scatter_controller class.
#         """

#     def process_data_for_plotting(self):
#         # turn the list of results into x : data and y : data for plotting
#         pass

#     @callback()
#     def switch_x_axis(self, metric):
#         pass

#     @callback()
#     def switch_y_axis(self, metric):
#         pass

#     def focus_data(self, problem=None, solver=None):
#         if problem is None and solver is None:
#             pass  # throw an error

#         # function should allow you to select both to isolate a single point
#         # possibly implement by greying everything out, then un greying
#         # the ones we want to keep highlighted


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
            [get_hover_text(result, newline="<br>")] for result in self.results
        ]
        return text_array


#     def get_hover_text_array(self):
#         # return an array of hover text in the same sorted order as the
# results
#         # for example x: [1,2,3]
#         # matches array: ["hover1","hover2","hover3"]
#         pass

#     def get_unique_problems(self):
#         # return an array of problems in the same sorted order as the
# #results
#         # this means that they can be used for grouping
#         # for example x: [1,2,3,4,5,6]
#         # matches array: ["p123","p123","p123","p456","p456","p456"]
#         # where "p123" is a group containing the first second and third
# points
#         pass

#     def get_unique_solvers(self):
#         # return an array of solvers in the same sorted order as the results
#         # this means that they can be used for grouping
#         # for example x: [1,2,3,4]
#         # matches array: ["oddSolver","evenSolver","oddSolver","evenSolver",]
#         # where "oddSolver" is a group containing the only every other point
#         pass
