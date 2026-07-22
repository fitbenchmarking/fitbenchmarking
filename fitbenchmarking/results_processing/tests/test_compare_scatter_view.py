import re
import unittest
from unittest import mock
from unittest.mock import Mock, patch

import plotly.graph_objects as go
from dash import dcc, html
from parameterized import parameterized
from plotly.validator_cache import ValidatorCache

from fitbenchmarking.results_processing.compare_scatter import (
    CompareScatterView,
)


class CompareScatterViewTests(unittest.TestCase):
    @staticmethod
    def _create_test_plot(view=CompareScatterView(), errors=[0, 1, 2, 3]):
        """
        Create a plot using CompareScatterView.get plot, default values are
        as follows:
        Minimizers: solver_1, solver_2
        Problems: problem_1, problem_2
        Tooltips: tooltip_1, tooltip_2, tooltip_3, tooltip_4
        x axis title: test_x_axis
        y axis title: test_y_axis
        x axis values: 1, 2, 3, 4
        y axis values: 1, 2, 3, 4
        error flags: 0, 1, 2, 3
        """
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
        """
        To improve the readability of the compare scatter, the class needs
        to filter out the symbols that look too similar.
        """

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
        """
        To ensure that no special characters break the html IDs given to
        elements on the compare scatter, non alphanumeric characters must be
        filtered out from their names
        """

        view = CompareScatterView()
        sanitized = view.sanitize_for_id("my(test_name) j:best,h:best")
        self.assertEqual(sanitized, "mytestnamejbesthbest")

    # some of the logic assumes that this is true so we need to test it
    def test_sanitize_for_id_is_idempotent(self):
        """
        Some of the compare scatter class was written with the assumption that
        if called on an ID which has already been sanitized, this function will
        not make any modification to the output so we need to test this
        behavior
        """

        view = CompareScatterView()
        sanitized = view.sanitize_for_id("my(test_name) j:best,h:best")
        self.assertEqual(sanitized, view.sanitize_for_id(sanitized))

    def test_get_point(self):
        """
        get_point is used to return the example points which are used for the
        values in the legend. Since they are intended to just be demonstrators
        for the colour and shape selected, they shouldn't be able to be
        interacted with, as that could make the buttons act in unexpected ways.
        """

        plot_div = CompareScatterView.get_point("circle", "rgba(0,255,0,1)")
        self.assertIsInstance(plot_div, html.Div)
        self.assertIsInstance(plot_div.children[0], dcc.Graph)

        plot = plot_div.children[0]

        self.assertEqual(plot.config, {"staticPlot": True})

        # check that only one trace is added
        self.assertEqual(len(plot.figure.data), 1)

        # check that the symbol and colour are set correctly
        self.assertEqual(plot.figure.data[0].marker.color, "rgba(0,255,0,1)")
        self.assertEqual(plot.figure.data[0].marker.symbol, "circle")

    def test_get_legend_contains_important_details(self):
        """
        Test that the legend contains all of the details provided to it. Does
        not check if the structure of the legend has changed.
        """
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
        pass
        # See issue #1633

    def test_get_plot_has_expected_structure(self):
        pass
        # See issue #1633

    def test_toggle_group_state_works_for_problems(self):
        """
        The compare scatter view uses a dictionary containing the state of all
        minimizers and problems represented on the legend. This test checks
        that the function toggle group state is able to find a problem in the
        dict and toggle its state value.
        """
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

    def test_toggle_group_state_works_for_minimizers(self):
        """
        The compare scatter view uses a dictionary containing the state of all
        minimizers and problems represented on the legend. This test checks
        that the function toggle group state is able to find a minimizer in the
        dict and toggle its state value.
        """
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

    def test_get_warning_text_for_results(self):
        """
        Tests that get_warning_text_for_results provides the correct output
        when given minimizers which either never failed to run, or failed to
        run some of the time, or failed to run all of the time.
        """
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
                "1/2 problems. Only successful runs"
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
        """
        Tests that when provided with a list containing any number of
        minimizers that threw an error and any number of runs of each
        minimizer, get_per_minimizer_errors_and_runs will return the correct
        numbers, including in edge/corner cases.
        """
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
        """
        Test that the counting mechanism used in
        get_per_minimizer_errors_and_runs works regardless of the order of
        results (since test_get_per_minimizer_errors_and_runs_counts always
        generates flags in the same order so does not cover this)
        """

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
        """
        Verify that when more than one minimizer is provided to
        get_per_minimizer_errors_and_runs, the function is capable of counting
        each minimizer separately.
        """
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
        self.assertTrue(
            any(
                toast.id == "allFails_toast" and toast.children == "all failed"
                for toast in toasts
            )
        )
        self.assertTrue(
            any(
                toast.id == "someFails_toast"
                and toast.children == "1/2 failed"
                for toast in toasts
            )
        )

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
        """
        Ensure that the function called when the All/None buttons are clicked
        updates the "Focus" (i.e. if a minimizer/problem is selected on the
        legend) for every minimizer and problem
        """
        view = CompareScatterView()
        minimizers = ["mySolver", "mySolver", "otherSolver", "otherSolver"]
        problems = ["problem1", "problem2", "problem1", "problem2"]

        view.plot = Mock(spec=go.Figure)

        # there should be one trace for each problem on each minimiser
        view.plot.data = [go.Scatter()] * (len(minimizers) * len(problems))
        for mock_trace in view.plot.data:
            mock_trace.marker = {"opacity": 1}

        state, all_button_style, none_button_style, _ = (
            view.set_focus_for_all_items(view.plot, new_focus, existing_state)
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
    def test_apply_state_to_all_or_none(
        self, select, mock_trace_opacity: Mock
    ):
        """
        test that when apply_state is called with the value all or none, it
        sets the opacity/focus for every trace on the plot
        """
        view = CompareScatterView()

        num_traces = 10

        view.plot = Mock(spec=go.Figure)
        view.plot.data = [Mock(spec=go.Trace)] * num_traces

        start_state = {
            "minimizer": {"test": True},
            "problem": {"test": True},
        }

        new_opacity = (
            view.active_opacity if select == "all" else view.inactive_opacity
        )

        for i in range(num_traces):
            _ = view.apply_state(view.plot, start_state, select)
            self.assertEqual(
                mock_trace_opacity.call_count, (i + 1) * num_traces
            )
            self.assertEqual(
                mock_trace_opacity.call_args,
                mock.call(view.plot.data[i], new_opacity),
            )

    @parameterized.expand([True, False])
    @patch(
        "fitbenchmarking.results_processing.compare_scatter.CompareScatterView.set_trace_opacity"
    )
    def test_apply_state(self, start_state, mock_trace_opacity: Mock):
        """
        test that when apply_state is called without the value all or none, it
        sets the opacity/focus to match the provided state dictionary
        """
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
