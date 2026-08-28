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
        ".CompareScatter.add_resize_callback"
    )
    @patch(
        "fitbenchmarking.results_processing.compare_scatter"
        ".CompareScatter.add_clickthrough_link_callback"
    )
    @patch(
        "fitbenchmarking.results_processing.compare_scatter"
        ".CompareScatter.add_log_axis_button_callbacks"
    )
    @patch(
        "fitbenchmarking.results_processing.compare_scatter"
        ".CompareScatter.add_axis_dropdown_callbacks"
    )
    @patch(
        "fitbenchmarking.results_processing.compare_scatter"
        ".CompareScatter.add_all_none_button_callbacks"
    )
    @patch(
        "fitbenchmarking.results_processing.compare_scatter"
        ".CompareScatter.add_legend_callbacks"
    )
    def test_add_callbacks_adds_callbacks(
        self,
        mock_add_legend_callbacks: Mock,
        mock_add_all_none_button_callbacks: Mock,
        mock_add_axis_dropdown_callbacks: Mock,
        mock_add_log_axis_button_callbacks: Mock,
        mock_add_clickthrough_link_callback: Mock,
        mock_add_resize_callback: Mock,
    ):
        """
        test that add callbacks calls all of the helper functions
        """
        app, options, test_data = self._get_mock_constructor_params()
        cs = CompareScatter(app, options, test_data)
        legend_items = ["mock_solver_0", "mock_solver_1"]

        cs.add_callbacks(legend_items)

        mock_add_legend_callbacks.assert_called_once_with(legend_items)
        mock_add_all_none_button_callbacks.assert_called_once()
        mock_add_axis_dropdown_callbacks.assert_called_once()
        mock_add_log_axis_button_callbacks.assert_called_once()
        mock_add_clickthrough_link_callback.assert_called_once()
        mock_add_resize_callback.assert_called_once()

    def test_add_resize_callback_uses_correct_io(self):
        app, options, test_data = self._get_mock_constructor_params()

        cs = CompareScatter(app, options, test_data)

        cs.add_resize_callback()

        clientside_callback_events = app.clientside_callback.call_args_list
        resize_observer_callback_args = clientside_callback_events[0][0]

        self.assertEqual(
            resize_observer_callback_args[2],
            Input("resize-timer", "n_intervals"),
        )

    def test_add_clickthrough_link_callback_uses_correct_io(self):
        app, options, test_data = self._get_mock_constructor_params()

        cs = CompareScatter(app, options, test_data)

        cs.add_clickthrough_link_callback()

        clientside_callback_events = app.clientside_callback.call_args_list
        clickthrough_link_callback_args = clientside_callback_events[0][0]

        self.assertEqual(
            clickthrough_link_callback_args[1],
            Output("dummy-click", "children"),
        )
        self.assertEqual(
            clickthrough_link_callback_args[2],
            Input("compare_scatter", "clickData"),
        )

    def test_add_log_axis_button_callbacks_uses_correct_io(self):
        app, options, test_data = self._get_mock_constructor_params()

        cs = CompareScatter(app, options, test_data)

        cs.add_log_axis_button_callbacks()

        events = app.callback.call_args_list
        x_log_axis_callback_args = events[0][0]
        y_log_axis_callback_args = events[1][0]

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

    def test_add_axis_dropdown_callbacks_uses_correct_io(self):
        app, options, test_data = self._get_mock_constructor_params()

        cs = CompareScatter(app, options, test_data)

        cs.add_axis_dropdown_callbacks()

        events = app.callback.call_args_list
        x_dropdown_callback_args = events[0][0]
        y_dropdown_callback_args = events[1][0]
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

    def test_add_all_none_button_callbacks_uses_correct_io(self):
        app, options, test_data = self._get_mock_constructor_params()
        cs = CompareScatter(app, options, test_data)
        cs.view.plot = Mock(spec=go.Figure())

        cs.add_all_none_button_callbacks()

        events = app.callback.call_args_list
        none_button_callback_args = events[0][0]
        all_button_callback_args = events[1][0]

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

    @patch(
        "fitbenchmarking.results_processing.compare_scatter"
        ".CompareScatterView.get_per_minimizer_errors_and_runs"
    )
    def test_add_legend_callbacks_uses_correct_io(
        self, mock_errors_and_runs: Mock
    ):
        app, options, test_data = self._get_mock_constructor_params()
        cs = CompareScatter(app, options, test_data)
        test_data[0].error_flag = 0
        test_data[1].error_flag = 3
        cs.view.plot = Mock(spec=go.Figure())

        mock_errors_and_runs.return_value = (
            {test_data[0].name: 0, test_data[1].name: 1},
            None,
        )

        cs.add_legend_callbacks([test_data[0].name, test_data[1].name])

        events = app.callback.call_args_list
        solver0_callback_args = events[0][0][0]
        solver1_callback_args = events[1][0][0]

        solver0_id = cs.view.sanitize_for_id(test_data[0].name)
        solver1_id = cs.view.sanitize_for_id(test_data[1].name)

        self.assertIn(
            Output("legend-status", "data", True), solver0_callback_args
        )
        self.assertIn(
            Output("compare_scatter", "figure", allow_duplicate=True),
            solver0_callback_args,
        )
        self.assertIn(Output(solver0_id, "style"), solver0_callback_args)
        self.assertIn(
            Output("all_button", "style", True), solver0_callback_args
        )
        self.assertIn(
            Output("none_button", "style", True), solver0_callback_args
        )
        self.assertIn(Input(solver0_id, "n_clicks"), solver0_callback_args)
        self.assertIn(State("legend-status", "data"), solver0_callback_args)

        self.assertIn(
            Output("compare_scatter", "figure", allow_duplicate=True),
            solver1_callback_args,
        )
        self.assertIn(
            Output("legend-status", "data", True), solver1_callback_args
        )
        self.assertIn(Output(solver1_id, "style"), solver1_callback_args)
        self.assertIn(
            Output("all_button", "style", True), solver1_callback_args
        )
        self.assertIn(
            Output("none_button", "style", True), solver1_callback_args
        )
        self.assertIn(
            Output(f"{solver1_id}_toast", "is_open", True),
            solver1_callback_args,
        )
        self.assertIn(Input(solver1_id, "n_clicks"), solver1_callback_args)
        self.assertIn(State("legend-status", "data"), solver1_callback_args)

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
