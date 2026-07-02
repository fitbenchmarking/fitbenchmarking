import re
import time
import unittest
from typing import cast
from unittest.mock import Mock, patch

import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html
from parameterized import parameterized
from plotly.validator_cache import ValidatorCache

from fitbenchmarking.results_processing.compare_scatter import (
    CompareScatter,
    CompareScatterDataModel,
    CompareScatterView,
)
from fitbenchmarking.results_processing.test_files.cs_test_data import (
    LEGEND,
)
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


def make_mock_fitting_result(i):
    mock_result = Mock(spec=FittingResult)
    mock_result.name = f"mock_result_{i}"
    mock_result.modified_minimizer_name = lambda with_software=False: (
        f"mock_solver_{i}"
        if not with_software
        else f"mock_solver_{i}_software"
    )
    mock_result.fitting_report_link = "test/support_pages/test_link"
    return cast("FittingResult", mock_result)


class CompareScatterTests(unittest.TestCase):
    @staticmethod
    def _get_mock_constructor_params():
        app = Mock(spec=Dash)
        options = Mock(spec=Options)
        test_data = []
        for i in range(2):
            # we need to set this since the model tries to access the name for
            # sorting
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
        app, options, test_data = self._get_mock_constructor_params()
        for mock_result in test_data:
            mock_result.fitting_report_link = "test/support_pages/test_link"
        cs = CompareScatter(app, options, test_data)

        urls = cs.get_fitting_report_urls()

        self.assertEqual(urls[0], "support_pages/test_link")
        self.assertEqual(urls[1], "support_pages/test_link")

    def test_get_fitting_report_urls_returns_index_when_none_provided(self):
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

    # TODO: split this into one per callback - should include the following:
    # all button, none button, mock, testMinimiser, clickthrough link,
    @patch(
        "fitbenchmarking.results_processing.compare_scatter"
        ".CompareScatterView.get_per_minimizer_errors_and_runs"
    )
    def test_add_callbacks_adds_callbacks(self, mock_errors_and_runs: Mock):
        app, options, test_data = self._get_mock_constructor_params()
        test_data[0].error_flag = 0
        test_data[1].error_flag = 3

        mock_errors_and_runs.return_value = (
            {"mock_solver_0": 0, "mock_solver_1": 1},
            None,
        )

        cs = CompareScatter(app, options, test_data)
        cs.view.plot = Mock(spec=go.Figure)
        cs.add_callbacks(app, ["mock_solver_0", "mock_solver_1"])

        self.assertEqual(app.callback.call_count, 4)

        events = app.callback.call_args_list

        my_minimizer_callback_args = events[0][0][0]
        test_minimizer_callback_args = events[1][0][0]
        none_button_callback_args = events[2][0]
        all_button_callback_args = events[3][0]

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
            Input("compare_scatter", "figure"),
        )

    def test_get_layout(self):
        app, options, test_data = self._get_mock_constructor_params()
        cs = CompareScatter(app, options, test_data)
        cs.view = Mock(spec=CompareScatterView)
        cs.view.plot = go.Figure()
        cs.model = Mock(spec=CompareScatterDataModel)
        cs.model.get_values_for_axis.return_value = []

        _, app_returned = cs.get_layout()
        self.assertEqual(app_returned, app)

        call_args = cs.model.get_values_for_axis.call_args_list

        self.assertEqual(call_args[0].args[0], "norm_runtime")
        self.assertEqual(call_args[1].args[0], "norm_acc")
        self.assertEqual(call_args[2].args[0], "error_flag")
        self.assertEqual(call_args[3].args[0], "modified_minimizer_name")
        self.assertEqual(call_args[3].kwargs["with_software"], True)
        self.assertEqual(call_args[4].args[0], "problem_tag")
        self.assertEqual(call_args[5].args[0], "fitting_report_link")
        self.assertEqual(call_args[6].args[0], "modified_minimizer_name")
        self.assertEqual(call_args[6].kwargs["with_software"], True)
        self.assertEqual(call_args[6].kwargs["unique"], True)
        self.assertEqual(call_args[7].args[0], "problem_tag")
        self.assertEqual(call_args[7].kwargs["unique"], True)


class CompareScatterDataModelTests(unittest.TestCase):
    empty_data = []
    single_result_dataset = [make_mock_fitting_result(1)]
    many_result_dataset = [make_mock_fitting_result(i) for i in range(100)]
    duplicate_name_dataset = [
        make_mock_fitting_result(1),
        make_mock_fitting_result(1),
    ]

    @parameterized.expand(
        [
            ("empty_data", empty_data),
            ("single_result_dataset", single_result_dataset),
            ("many_result_dataset", many_result_dataset),
        ]
    )
    def test_model_is_order_independent(self, test_case_name, dataset):
        data_model = CompareScatterDataModel(dataset)
        data_model_from_reversed = CompareScatterDataModel(
            list(reversed(dataset))
        )
        data_model_from_suffled = CompareScatterDataModel(
            np.random.Generator(np.random.PCG64())
            .permutation(dataset)
            .tolist()
        )

        self.assertEqual(data_model.results, data_model_from_reversed.results)
        self.assertEqual(data_model.results, data_model_from_suffled.results)

    def test_results_sorted_by_name(self):
        sort_value = CompareScatterDataModel([]).get_sort_key(
            self.single_result_dataset[0]
        )

        self.assertEqual(sort_value, self.single_result_dataset[0].name)

    def test_get_values_for_axis_works_for_attributes(self):
        model = CompareScatterDataModel(self.many_result_dataset)
        values = model.get_values_for_axis("name")
        self.assertEqual(
            values, [result.name for result in self.many_result_dataset]
        )

    def test_get_values_for_axis_works_for_callables(self):
        model = CompareScatterDataModel(self.many_result_dataset)
        values = model.get_values_for_axis("modified_minimizer_name")
        self.assertEqual(
            values,
            [
                result.modified_minimizer_name()
                for result in self.many_result_dataset
            ],
        )

    def test_get_values_for_axis_respects_callable_arguments(self):
        model = CompareScatterDataModel(self.many_result_dataset)
        values = model.get_values_for_axis(
            "modified_minimizer_name", with_software=True
        )
        self.assertEqual(
            values,
            [
                result.modified_minimizer_name(with_software=True)
                for result in self.many_result_dataset
            ],
        )

    # This test is non deterministic
    @parameterized.expand(["name", "modified_minimizer_name"])
    def test_get_values_cache_is_faster(self, axis):
        model = CompareScatterDataModel(self.many_result_dataset)

        start = time.perf_counter()
        _ = model.get_values_for_axis(axis)
        end = time.perf_counter()

        first_duration = end - start

        start = time.perf_counter()
        _ = model.get_values_for_axis(axis)
        end = time.perf_counter()

        second_duration = end - start

        self.assertLess(second_duration, first_duration)

    def test_get_values_caches_data(self):
        model = CompareScatterDataModel(self.many_result_dataset)

        _ = model.get_values_for_axis("name")

        cache = model.__getattribute__("_cache_name")

        self.assertIsInstance(cache, list)
        self.assertEqual(len(cache), len(self.many_result_dataset))

    def test_get_values_for_axis_caches_functors_not_return_values(self):
        model = CompareScatterDataModel(self.single_result_dataset)

        first_values = model.get_values_for_axis("modified_minimizer_name")

        # kwargs do not impact the location of the cache, so this simulates
        # a change in return value without the cache key changing
        values_after_result_change = model.get_values_for_axis(
            "modified_minimizer_name", with_software=True
        )

        # if we cached the return values, the output would be the same for both
        self.assertNotEqual(first_values, values_after_result_change)

    def test_get_unique_values_gets_unique_values(self):
        model = CompareScatterDataModel(self.duplicate_name_dataset)
        unique_values = model.get_values_for_axis("name", unique=True)
        self.assertEqual(unique_values, ["mock_result_1"])

    def test_get_unique_values_uses_different_cache(self):
        model = CompareScatterDataModel(self.duplicate_name_dataset)

        unique_values = model.get_values_for_axis("name", unique=True)
        cache = model.__getattribute__("_unique_cache_name")

        self.assertEqual(unique_values, cache)

    @patch("fitbenchmarking.results_processing.compare_scatter.get_hover_text")
    def test_get_hover_text_for_results(self, mock_get_hover_text: Mock):
        mock_get_hover_text.return_value = "Hover Text"
        model = CompareScatterDataModel(self.single_result_dataset)

        hover_text = model.get_hover_text_for_results()

        mock_get_hover_text.assert_called_once_with(
            self.single_result_dataset[0], include_title=True, newline="<br>"
        )

        self.assertEqual(hover_text, [["Hover Text" + "<extra></extra>"]])


class CompareScatterViewTests(unittest.TestCase):
    @staticmethod
    def _create_test_plot(view=CompareScatterView(), errors=[0, 1, 2, 3]):
        return view.get_plot(
            x=[1, 2, 3, 4],
            y=[1, 2, 3, 4],
            x_title="test_x_axis",
            y_title="test_y_axis",
            tooltips=[
                ["tooltip_1"],
                ["tooltip_2"],
                ["tooltip_3"],
                ["tooltip_4"],
            ],
            errors=errors,
            minimizers=["solver_1", "solver_1", "solver_2", "solver_2"],
            problems=["problem_1", "problem_2", "problem_1", "problem_2"],
            report_pages=[
                "/solver_1/problem_1",
                "/solver_2/problem_2",
                "/solver_3/problem_1",
                "/solver_4/problem_2",
            ],
        )

    def test_constructor_sets_valid_symbols(self):
        view = CompareScatterView()
        validator = ValidatorCache.get_validator("scatter.marker", "symbol")
        all_possible_symbols = validator.values[2::3]

        # we dont actually want to specify the exact list here since that would
        # just be a duplicate of the list in the class, instead we just check
        # that any filtering was applied

        # every prefix in the list of banned prefixes matches at least one real
        # prefix returned by the validator
        for prefix in view.banned_prefixes:
            self.assertTrue(
                any(
                    symbol.startswith(prefix)
                    for symbol in all_possible_symbols
                )
            )

        # every banned prefix is no longer present in the valid symbols
        self.assertTrue(
            all(
                not symbol.startswith(prefix)
                for prefix in view.banned_prefixes
                for symbol in view.valid_symbols
            )
        )

    def test_sanitize_for_id(self):
        view = CompareScatterView()
        sanitized = view.sanitize_for_id("my(test_name) j:best,h:best")
        self.assertEqual(sanitized, "mytestnamejbesthbest")

    # some of the logic assumes that this is true so we need to test it
    def test_sanitize_for_id_is_idempotent(self):
        view = CompareScatterView()
        sanitized = view.sanitize_for_id("my(test_name) j:best,h:best")
        self.assertEqual(sanitized, view.sanitize_for_id(sanitized))

    def test_get_point(self):
        plot_div = CompareScatterView.get_point("circle", "rgba(0,255,0,1)")
        self.assertIsInstance(plot_div, html.Div)
        self.assertIsInstance(plot_div.children[0], dcc.Graph)

        plot = plot_div.children[0]

        # check that the plot cannot be interacted with
        self.assertEqual(plot.config, {"staticPlot": True})

        # check that only one trace is added
        self.assertEqual(len(plot.figure.data), 1)

        # check that the symbol and colour are set correctly
        self.assertEqual(plot.figure.data[0].marker.color, "rgba(0,255,0,1)")
        self.assertEqual(plot.figure.data[0].marker.symbol, "circle")

    def test_get_legend_contains_important_details(self):
        view = CompareScatterView()
        legend = view.get_legend(
            symbol_groups=["symbol_group_1", "symbol_group_2"],
            symbol_map=["cross", "square"],
            colour_groups=["colour_group_1", "colour_group_2"],
            colour_map=["rgba(255,0,0,1)", "rgba(0,255,0,1)"],
        )

        legend_string = str(legend)

        # the legend should contain one example of each colour from the map
        num_red = len(re.findall("rgba\\(255,0,0,1\\)", legend_string))
        self.assertEqual(num_red, 1)
        num_green = len(re.findall("rgba\\(0,255,0,1\\)", legend_string))
        self.assertEqual(num_green, 1)

        # the legend should contain one circle for each colour
        num_circle = len(re.findall("circle", legend_string))
        self.assertEqual(num_circle, 2)

        # the legend should contain one example of each symbol from the map
        num_cross = len(re.findall("cross", legend_string))
        self.assertEqual(num_cross, 1)
        num_square = len(re.findall("square", legend_string))
        self.assertEqual(num_square, 1)

        # each colour and symbol group should appear twice, once in the data
        # store, and once as the visible text for the legend
        num_c_grp_1 = len(re.findall("colour_group_1", legend_string))
        self.assertEqual(num_c_grp_1, 2)
        num_c_grp_2 = len(re.findall("colour_group_2", legend_string))
        self.assertEqual(num_c_grp_2, 2)
        num_s_grp_1 = len(re.findall("symbol_group_1", legend_string))
        self.assertEqual(num_s_grp_1, 2)
        num_s_grp_2 = len(re.findall("symbol_group_2", legend_string))
        self.assertEqual(num_s_grp_2, 2)

        # convert the legend to a string so that we can check that it contains
        # the expected information without caring about specific structure

    def test_get_legend_returns_correct_structure(self):
        # if it is all contained within a div, then the way we insert it into
        # other parts of the code should not need to change
        view = CompareScatterView()
        legend = view.get_legend(
            symbol_groups=["symbol_group_1", "symbol_group_2"],
            symbol_map=["cross", "square"],
            colour_groups=["colour_group_1", "colour_group_2"],
            colour_map=["rgba(255,0,0,1)", "rgba(0,255,0,1)"],
        )
        self.assertIsInstance(legend, html.Div)

        # assert that the legend should be the same structure as expected
        # note that this test will fail even if the change is intentional, so
        # test_get_legend_contains_important_details does an extra sanity check

        legend_without_whitespace = re.sub("\\s+", "", str(legend))
        expected_legend_without_whitespace = re.sub("\\s+", "", str(LEGEND))

        self.assertEqual(
            legend_without_whitespace,
            expected_legend_without_whitespace,
            f"instead of the expected legend we got: {legend!s}",
        )

    def test_get_plot_has_expected_structure(self):
        pass
        # See issue #1633

    def test_toggle_group_state_works_for_problems(self):
        view = CompareScatterView()

        default_state_dict = {
            "minimizer": dict.fromkeys(["solver_1"], True),
            "problem": dict.fromkeys(["problem_1"], True),
        }

        # Test that it can set the state to False
        group_state, state_dict = view.toggle_group_state(
            "problem_1", default_state_dict
        )

        self.assertEqual(group_state, False)
        self.assertEqual(state_dict["problem"]["problem_1"], False)

        # Test that it can set the state to True
        group_state, state_dict = view.toggle_group_state(
            "problem_1", state_dict
        )

        self.assertEqual(group_state, True)
        self.assertEqual(state_dict["problem"]["problem_1"], True)

    def test_toggle_group_state_throws_when_item_not_found(self):
        view = CompareScatterView()

        default_state_dict = {
            "minimizer": dict.fromkeys(["solver_1"], True),
            "problem": dict.fromkeys(["problem_1"], True),
        }

        self.assertRaises(
            ValueError,
            view.toggle_group_state,
            "thing that does not exist",
            default_state_dict,
        )

    def test_toggle_group_state_works_for_minimizers(self):
        view = CompareScatterView()

        default_state_dict = {
            "minimizer": dict.fromkeys(["mySolver"], True),
            "problem": dict.fromkeys(["myProblem"], True),
        }

        group_state, state_dict = view.toggle_group_state(
            "mySolver", default_state_dict
        )

        self.assertEqual(group_state, False)
        self.assertEqual(state_dict["minimizer"]["mySolver"], False)

        group_state, state_dict = view.toggle_group_state(
            "mySolver", state_dict
        )

        self.assertEqual(group_state, True)
        self.assertEqual(state_dict["minimizer"]["mySolver"], True)

    def test_get_warning_text(self):
        view = CompareScatterView()
        minimizers = ["noFails", "someFails", "someFails", "allFails"]
        flags = [0, 0, 3, 3]
        warning = view.get_warning_text_for_results(flags, minimizers)

        self.assertIn("noFails", warning)
        self.assertIn("someFails", warning)
        self.assertIn("allFails", warning)

        self.assertIsNone(warning["noFails"])
        self.assertEqual(
            warning["someFails"],
            (
                "Warning: this minimizer failed to run on "
                "1/2 problems. Only succesful runs"
                " have been plotted."
            ),
        )
        self.assertEqual(
            warning["allFails"],
            (
                "Warning: this minimizer failed to run on every "
                "problem and could not be plotted."
            ),
        )

    @parameterized.expand(
        [
            (0, 10),
            (5, 10),
            (10, 10),
            (0, 1),
        ]
    )
    def test_get_per_minimizer_errors_and_runs_counts(self, errors, runs):
        view = CompareScatterView()
        minimizers = ["myBadMinim"] * runs
        flags = [3] * errors + [0] * (runs - errors)
        errors_by_minimizer, runs_by_minimizer = (
            view.get_per_minimizer_errors_and_runs(flags, minimizers)
        )
        self.assertIn("myBadMinim", errors_by_minimizer)
        self.assertIn("myBadMinim", runs_by_minimizer)
        self.assertEqual(errors_by_minimizer["myBadMinim"], errors)
        self.assertEqual(runs_by_minimizer["myBadMinim"], runs)

    def test_get_per_minimizer_errors_order_independent(self):
        view = CompareScatterView()
        minimizers = ["myBadMinim"] * 3
        flag_orders = [
            [3, 0, 0],
            [0, 3, 0],
            [0, 0, 3],
        ]
        for flag_order in flag_orders:
            errors_by_minimizer, _ = view.get_per_minimizer_errors_and_runs(
                flag_order, minimizers
            )
            self.assertIn("myBadMinim", errors_by_minimizer)
            self.assertEqual(errors_by_minimizer["myBadMinim"], 1)

    def test_get_per_minimizer_runs_counts_multiple_minimizers(self):
        view = CompareScatterView()
        minimizers = (
            ["myBadMinim"] * 3 + ["myOkMinim"] * 1 + ["myOtherMinim"] * 6
        )
        flags = [0] * 10
        errors_by_minimizer, runs_by_minimizer = (
            view.get_per_minimizer_errors_and_runs(flags, minimizers)
        )
        self.assertIn("myBadMinim", errors_by_minimizer)
        self.assertIn("myOkMinim", errors_by_minimizer)
        self.assertIn("myOtherMinim", errors_by_minimizer)
        self.assertIn("myBadMinim", runs_by_minimizer)
        self.assertIn("myOkMinim", runs_by_minimizer)
        self.assertIn("myOtherMinim", runs_by_minimizer)

        self.assertEqual(runs_by_minimizer["myBadMinim"], 3)
        self.assertEqual(runs_by_minimizer["myOkMinim"], 1)
        self.assertEqual(runs_by_minimizer["myOtherMinim"], 6)

    def test_create_warning_toasts(self):
        view = CompareScatterView()
        warnings = {
            "noFails": None,
            "someFails": "1/2 failed",
            "allFails": "all failed",
        }
        toasts = view.create_warning_toasts(warnings)

        self.assertEqual(len(toasts), 2)
        self.assertEqual(toasts[0].id, "allFails_toast")
        self.assertEqual(toasts[0].children, "all failed")
        self.assertEqual(toasts[1].id, "someFails_toast")
        self.assertEqual(toasts[1].children, "1/2 failed")

    @parameterized.expand(
        [
            (
                "active_all_false",
                True,
                {
                    "minimizer": {"mySolver": False, "otherSolver": False},
                    "problem": {"problem1": False, "problem2": False},
                },
            ),
            (
                "active_mixed_states",
                True,
                {
                    "minimizer": {"mySolver": True, "otherSolver": False},
                    "problem": {"problem1": True, "problem2": False},
                },
            ),
            (
                "active_all_true",
                True,
                {
                    "minimizer": {"mySolver": True, "otherSolver": True},
                    "problem": {"problem1": True, "problem2": True},
                },
            ),
            (
                "inactive_all_false",
                False,
                {
                    "minimizer": {"mySolver": False, "otherSolver": False},
                    "problem": {"problem1": False, "problem2": False},
                },
            ),
            (
                "inactive_mixed_states",
                False,
                {
                    "minimizer": {"mySolver": True, "otherSolver": False},
                    "problem": {"problem1": True, "problem2": False},
                },
            ),
            (
                "inactive_all_true",
                False,
                {
                    "minimizer": {"mySolver": True, "otherSolver": True},
                    "problem": {"problem1": True, "problem2": True},
                },
            ),
        ],
    )
    @patch("dash.callback_context.set_props")
    def test_set_focus_for_all(
        self, _, new_focus, existing_state, set_props_mock: Mock
    ):
        view = CompareScatterView()
        minimizers = ["mySolver", "mySolver", "otherSolver", "otherSolver"]
        problems = ["problem1", "problem2", "problem1", "problem2"]
        _ = self._create_test_plot(view)

        state, all_button_style, none_button_style, _ = (
            view.set_focus_for_all_items(new_focus, existing_state)
        )

        expected_state = {
            "minimizer": dict.fromkeys(minimizers, new_focus),
            "problem": dict.fromkeys(problems, new_focus),
        }

        self.assertEqual(state, expected_state)

        if new_focus:
            self.assertEqual(all_button_style, view.active_button_style)
            self.assertEqual(none_button_style, view.inactive_button_style)
        else:
            self.assertEqual(all_button_style, view.inactive_button_style)
            self.assertEqual(none_button_style, view.active_button_style)

        set_props_mock.assert_called()

    def test_set_trace_opacity(self):
        view = CompareScatterView()
        plot_div = self._create_test_plot(view, errors=[1, 1, 1, 1])

        trace = plot_div.children[1].figure.data[0]
        view.set_trace_opacity(trace, 0)
        self.assertEqual(trace.marker["opacity"], 0)
        self.assertEqual(trace.text, '<sup style="opacity:0"><b>1</b></sup>')
        view.set_trace_opacity(trace, 1)
        self.assertEqual(trace.marker["opacity"], 1)
        self.assertEqual(trace.text, '<sup style="opacity:1"><b>1</b></sup>')
        view.set_trace_opacity(trace, 0.5)
        self.assertEqual(trace.marker["opacity"], 0.5)
        self.assertEqual(trace.text, '<sup style="opacity:0.5"><b>1</b></sup>')

    @parameterized.expand(["all", "none"])
    @patch(
        "fitbenchmarking.results_processing.compare_scatter.CompareScatterView.set_trace_opacity"
    )
    def test_apply_state_focus(self, select, mock_trace_opacity: Mock):
        view = CompareScatterView()

        num_traces = 10

        view.plot = Mock(spec=go.Figure)
        view.plot.data = [Mock(spec=go.Trace)] * num_traces

        start_state = {
            "minimizer": dict.fromkeys(["test"] * num_traces, True),
            "problem": dict.fromkeys(["test"] * num_traces, True),
        }

        new_opacity = (
            view.active_opacity if select == "all" else view.inactive_opacity
        )

        # check that it can be called to focus
        for i in range(num_traces):
            _ = view.apply_state(view.plot, start_state, select)
            self.assertEqual(
                mock_trace_opacity.call_count, (i + 1) * num_traces
            )
            self.assertEqual(mock_trace_opacity.call_args.args[1], new_opacity)

        mock_trace_opacity.assert_called()

    @parameterized.expand([True, False])
    @patch(
        "fitbenchmarking.results_processing.compare_scatter.CompareScatterView.set_trace_opacity"
    )
    def test_apply_state(self, start_state, mock_trace_opacity: Mock):
        view = CompareScatterView()
        _ = self._create_test_plot(view)

        minimizers = ["solver_1", "solver_2", "solver_3", "solver_4"]
        problems = ["problem_1", "problem_2", "problem_1", "problem_2"]
        expected_state = {
            "minimizer": dict.fromkeys(minimizers, start_state),
            "problem": dict.fromkeys(problems, start_state),
        }

        new_opacity = (
            view.active_opacity if start_state else view.inactive_opacity
        )

        # check that it can be called to focus
        for i, trace in enumerate(minimizers + problems):
            _ = view.apply_state(view.plot, expected_state)
            # should be called once for each trace
            self.assertEqual(mock_trace_opacity.call_count, (i + 1) * 4)
            self.assertEqual(mock_trace_opacity.call_args.args[1], new_opacity)

        mock_trace_opacity.assert_called()
