from dash import html

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
        # self.model = compare_scatter_data_model(results)
        # self.controller = compare_scatter_controller()
        # most of the interface is just get plot from the view

    def get_layout(self):
        return self.view.get_plot(self.results)


class CompareScatterView:
    """
    Class to handle the basic plotting of a compare scatter
    """

    def get_plot(self, results):
        return html.Div(str(results))


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


# class compare_scatter_data_model:
#     # def __init__(self, results: list[FittingResult]):
#     #    self.results = results

#     def get_values_for_axis(self, metric):
#         pass

#     def add_clickthrough_links(self):
#         pass

#     def get_hover_text_for_result(self, result):
#         # call util, and prepend the metrics being plotted
#         pass

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
