import time
import unittest
from typing import cast
from unittest.mock import Mock, patch

import numpy as np
from dash import Dash
from parameterized import parameterized

from fitbenchmarking.results_processing.compare_scatter import (
    CompareScatter,
    CompareScatterDataModel,
)
from fitbenchmarking.utils.fitbm_result import FittingResult


def make_mock_fitting_result(number, alternate_return_value=False):
    mock_result = Mock(spec=FittingResult)
    mock_result.name = f"Result_{number}"
    mock_result.id = number

    if not alternate_return_value:
        mock_result.modified_minimizer_name = lambda with_software=False: (
            f"{number}_with_software" if with_software else f"{number}"
        )
    else:
        mock_result.modified_minimizer_name = lambda _: (
            "different_return_value"
        )

    return cast("FittingResult", mock_result)


class CompareScatterTests(unittest.TestCase):
    empty_data = []
    single_result_dataset = [make_mock_fitting_result(1)]
    many_result_dataset = [make_mock_fitting_result(i) for i in range(100)]
    dummy_dash_app = Dash()
    dummy_options = None

    @patch(
        "fitbenchmarking.results_processing.compare_scatter.CompareScatterDataModel"
    )
    @patch(
        "fitbenchmarking.results_processing.compare_scatter.CompareScatterView"
    )
    def test_constructor_sets_attributes(self, mock_view, mock_model):

        compare_scatter = CompareScatter(
            self.dummy_dash_app, self.dummy_options, self.empty_data
        )

        mock_view.assert_called_once()
        mock_model.assert_called_once_with(self.empty_data)
        self.assertEqual(compare_scatter.results, self.empty_data)
        self.assertEqual(compare_scatter.app, self.dummy_dash_app)


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
            "modified_minimizer_name", {"with_software": True}
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
        model = CompareScatterDataModel(self.many_result_dataset)

        first_values = model.get_values_for_axis("modified_minimizer_name")

        # kwargs do not impact the location of the cache, so this simulates
        # a change in return value without the cache key changing
        values_after_result_change = model.get_values_for_axis(
            "modified_minimizer_name", {"with_software": True}
        )

        # if we cached the return values, the output would be the same for both
        self.assertNotEqual(first_values, values_after_result_change)

    def test_get_unique_values_gets_unique_values(self):
        model = CompareScatterDataModel(self.duplicate_name_dataset)
        unique_values = model.get_unique_values_for_axis("name")
        self.assertEqual(unique_values, ["Result_1"])

    def test_get_unique_values_uses_different_cache(self):
        model = CompareScatterDataModel(self.duplicate_name_dataset)

        unique_values = model.get_unique_values_for_axis("name")
        cache = model.__getattribute__("_unique_cache_name")

        self.assertEqual(unique_values, cache)

    @patch("fitbenchmarking.results_processing.compare_scatter.get_hover_text")
    def test_get_hover_text_for_results(self, mock_get_hover_text):
        mock_get_hover_text.return_value = "Hover Text"
        model = CompareScatterDataModel(self.single_result_dataset)

        hover_text = model.get_hover_text_for_results()

        mock_get_hover_text.assert_called_once_with(
            self.single_result_dataset[0], include_title=True, newline="<br>"
        )

        self.assertEqual(hover_text, [["Hover Text" + "<extra></extra>"]])
