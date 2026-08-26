import unittest
import uuid
from typing import cast
from unittest import mock
from unittest.mock import Mock, patch

import plotly.graph_objects as go
from dash import Dash, Input, Output, State

from fitbenchmarking.results_processing.compare_scatter import (
    CompareScatter,
    CompareScatterDataModel,
    CompareScatterView,
)
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


def make_mock_fitting_result(i, alternate_minimizer_name_output=False):
    """
    Create a mock fitting result and populate the name and fitting_report_link
    attributes. Also implement a basic lambda for modified_minimizer_name.
    """
    mock_result = Mock(spec=FittingResult)
    mock_result.name = f"mock_result_{i}"
    mock_result.modified_minimizer_name = lambda with_software=False: (
        f"mock_solver_{i}"
        if not with_software
        else f"mock_solver_{i}_software"
    )

    # alternate_minimizer_name_output is used to change the output of
    # modified_minimizer_name
    if alternate_minimizer_name_output:
        mock_result.modified_minimizer_name = lambda with_software=False: str(
            uuid.uuid4()
        )
    mock_result.fitting_report_link = "test/support_pages/test_link"
    return cast("FittingResult", mock_result)


class CompareScatterTests(unittest.TestCase):
    @staticmethod
    def _get_mock_constructor_params():
        """
        get a tuple of parameters which should represent the minimum to make
        a compare scatter with two points.

        App and options are Mocks of Dash and Options.
        """
        app = Mock(spec=Dash)
        options = Mock(spec=Options)
        test_data = []
        for i in range(2):
            mock_result = make_mock_fitting_result(i)
            test_data.append(mock_result)

        return app, options, test_data

    def test_constructor_sets_attributes(self):
        app, options, test_data = self._get_mock_constructor_params()
        compare_scatter = CompareScatter(app, options, test_data)

        self.assertEqual(compare_scatter.results, test_data)
        self.assertEqual(compare_scatter.app, app)
        self.assertEqual(compare_scatter.options, options)
        self.assertIsInstance(compare_scatter.model, CompareScatterDataModel)
        self.assertIsInstance(compare_scatter.view, CompareScatterView)

    def test_get_fitting_report_urls_sets_url_correctly(self):
        """
        The paths provided from the fitting_report_link attribute of Fitting
        Reports need to be processed before use as a URL, ensure that that
        processing happens correctly.
        """

        app, options, test_data = self._get_mock_constructor_params()
        for mock_result in test_data:
            mock_result.fitting_report_link = "test/support_pages/test_link"
        cs = CompareScatter(app, options, test_data)

        urls = cs.get_fitting_report_urls()

        self.assertEqual(urls[0], "support_pages/test_link")
        self.assertEqual(urls[1], "support_pages/test_link")

    def test_get_fitting_report_urls_returns_index_page_when_none_provided(
        self,
    ):
        """
        The fitting report should return to the index when no report link could
        be found for the result
        """

        app, options, test_data = self._get_mock_constructor_params()
        for mock_result in test_data:
            mock_result.fitting_report_link = ""
        cs = CompareScatter(app, options, test_data)

        urls = cs.get_fitting_report_urls()

        self.assertEqual(urls[0], "index.html")
        self.assertEqual(urls[1], "index.html")

    @patch(
        "fitbenchmarking.results_processing.compare_scatter"
        ".CompareScatterView.get_per_minimizer_errors_and_runs"
    )
    def test_item_should_have_warning_toast(self, mock_errors_and_runs: Mock):
        """
        Verify that item_should_have_warning toast is able to identify solvers
        with at least one fail.
        """
        app, options, test_data = self._get_mock_constructor_params()

        test_data[0].error_flag = 0
        test_data[1].error_flag = 3

        mock_errors_and_runs.return_value = (
            {"mock_solver_0": 0, "mock_solver_1": 1},
            None,
        )

        cs = CompareScatter(app, options, test_data)
        self.assertFalse(cs.item_should_have_warning_toast("mock_solver_0"))
        self.assertTrue(cs.item_should_have_warning_toast("mock_solver_1"))

    @patch(
        "fitbenchmarking.results_processing.compare_scatter"
        ".CompareScatterView.get_per_minimizer_errors_and_runs"
    )
    def test_add_callbacks_adds_callbacks(self, mock_errors_and_runs: Mock):
        """
        test that add callbacks adds callbacks with all of the expected inputs
        and outputs
        """

        app, options, test_data = self._get_mock_constructor_params()
        test_data[0].error_flag = 0
        test_data[1].error_flag = 3

        mock_errors_and_runs.return_value = (
            {"mock_solver_0": 0, "mock_solver_1": 1},
            None,
        )

        cs = CompareScatter(app, options, test_data)
        cs.view.plot = Mock(spec=go.Figure())

        cs.add_callbacks(cs.view.plot, ["mock_solver_0", "mock_solver_1"])

        self.assertEqual(app.callback.call_count, 8)

        events = app.callback.call_args_list

        my_minimizer_callback_args = events[0][0][0]
        test_minimizer_callback_args = events[1][0][0]
        none_button_callback_args = events[2][0]
        all_button_callback_args = events[3][0]
        x_dropdown_callback_args = events[4][0]
        y_dropdown_callback_args = events[5][0]
        x_log_axis_callback_args = events[6][0]
        y_log_axis_callback_args = events[7][0]

        self.assertEqual(
            my_minimizer_callback_args[0], Output("compare_scatter", "figure")
        )
        self.assertEqual(
            my_minimizer_callback_args[1], Output("legend-status", "data")
        )
        self.assertEqual(
            my_minimizer_callback_args[2], Output("mocksolver0", "style")
        )
        self.assertEqual(
            my_minimizer_callback_args[3], Output("all_button", "style")
        )
        self.assertEqual(
            my_minimizer_callback_args[4], Output("none_button", "style")
        )
        self.assertEqual(
            my_minimizer_callback_args[5], Input("mocksolver0", "n_clicks")
        )
        self.assertEqual(
            my_minimizer_callback_args[6], State("legend-status", "data")
        )

        self.assertEqual(
            test_minimizer_callback_args[0],
            Output("compare_scatter", "figure"),
        )
        self.assertEqual(
            test_minimizer_callback_args[1], Output("legend-status", "data")
        )
        self.assertEqual(
            test_minimizer_callback_args[2], Output("mocksolver1", "style")
        )
        self.assertEqual(
            test_minimizer_callback_args[3], Output("all_button", "style")
        )
        self.assertEqual(
            test_minimizer_callback_args[4], Output("none_button", "style")
        )
        self.assertEqual(
            test_minimizer_callback_args[5],
            Output("mocksolver1_toast", "is_open"),
        )
        self.assertEqual(
            test_minimizer_callback_args[6], Input("mocksolver1", "n_clicks")
        )
        self.assertEqual(
            test_minimizer_callback_args[7], State("legend-status", "data")
        )

        self.assertEqual(
            none_button_callback_args[0], Output("legend-status", "data", True)
        )
        self.assertEqual(
            none_button_callback_args[1], Output("all_button", "style", True)
        )
        self.assertEqual(
            none_button_callback_args[2], Output("none_button", "style", True)
        )
        self.assertEqual(
            none_button_callback_args[3],
            Output("compare_scatter", "figure", True),
        )
        self.assertEqual(
            none_button_callback_args[4], Input("none_button", "n_clicks")
        )
        self.assertEqual(
            none_button_callback_args[5], State("legend-status", "data")
        )

        self.assertEqual(
            all_button_callback_args[0], Output("legend-status", "data", True)
        )
        self.assertEqual(
            all_button_callback_args[1], Output("all_button", "style", True)
        )
        self.assertEqual(
            all_button_callback_args[2], Output("none_button", "style", True)
        )
        self.assertEqual(
            all_button_callback_args[3],
            Output("compare_scatter", "figure", True),
        )
        self.assertEqual(
            all_button_callback_args[4], Input("all_button", "n_clicks")
        )
        self.assertEqual(
            all_button_callback_args[5], State("legend-status", "data")
        )

        self.assertEqual(
            x_dropdown_callback_args[0],
            Output("compare_scatter", "figure", True),
        )
        self.assertEqual(
            x_dropdown_callback_args[1], Input("x-dropdown", "value")
        )
        self.assertEqual(
            y_dropdown_callback_args[0],
            Output("compare_scatter", "figure", True),
        )
        self.assertEqual(
            y_dropdown_callback_args[1], Input("y-dropdown", "value")
        )

        self.assertEqual(
            x_log_axis_callback_args[0],
            Output("compare_scatter", "figure", True),
        )
        self.assertEqual(
            x_log_axis_callback_args[1], Input("x-log-axis", "value")
        )
        self.assertEqual(
            y_log_axis_callback_args[0],
            Output("compare_scatter", "figure", True),
        )
        self.assertEqual(
            y_log_axis_callback_args[1], Input("y-log-axis", "value")
        )

        self.assertEqual(app.clientside_callback.call_count, 2)

        clientside_callback_events = app.clientside_callback.call_args_list
        clickthrough_link_callback_args = clientside_callback_events[0][0]
        resize_observer_callback_args = clientside_callback_events[1][0]

        self.assertEqual(
            clickthrough_link_callback_args[1],
            Output("dummy-click", "children"),
        )
        self.assertEqual(
            clickthrough_link_callback_args[2],
            Input("compare_scatter", "clickData"),
        )

        self.assertEqual(
            resize_observer_callback_args[1],
            Output("dummy-height", "children"),
        )
        self.assertEqual(
            resize_observer_callback_args[2],
            Input("resize-timer", "n_intervals"),
        )

    def test_get_layout_uses_correct_information(self):
        """
        Check that get Layout gets the correct pieces of information from the
        data model
        """

        app, options, test_data = self._get_mock_constructor_params()
        cs = CompareScatter(app, options, test_data)
        cs.view = Mock(spec=CompareScatterView)
        cs.view.plot = go.Figure()
        cs.model = Mock(spec=CompareScatterDataModel)
        cs.model.get_values_from_results.return_value = []
        cs.model.get_plottable_attributes.return_value = []

        _, app_returned = cs.get_layout()
        self.assertEqual(app_returned, app)

        cs.model.get_values_from_results.assert_has_calls(
            [
                mock.call("hover_text", style="html", include_title=True),
                mock.call("norm_runtime"),
                mock.call("norm_acc"),
                mock.call("error_flag"),
                mock.call("modified_minimizer_name", with_software=True),
                mock.call("problem_tag"),
                mock.call("fitting_report_link"),
                mock.call(
                    "modified_minimizer_name", with_software=True, unique=True
                ),
                mock.call("problem_tag", unique=True),
            ]
        )
