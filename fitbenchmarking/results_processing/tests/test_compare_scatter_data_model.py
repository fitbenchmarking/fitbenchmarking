import unittest
from dataclasses import dataclass
from unittest.mock import Mock

import numpy as np
from parameterized import parameterized

from fitbenchmarking.results_processing.compare_scatter import (
    CompareScatterDataModel,
)
from fitbenchmarking.results_processing.tests.test_compare_scatter import (
    make_mock_fitting_result,
)
from fitbenchmarking.utils.fitbm_result import FittingResult


class CompareScatterDataModelTests(unittest.TestCase):
    empty_data = []
    single_result_dataset = [make_mock_fitting_result(1)]
    many_result_dataset = [make_mock_fitting_result(i) for i in range(10)]
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
        """
        The compare scatter should have the exact same output, whatever order
        the results are provided in. This means that it should behave more
        consistently when loading from a checkpoint or using multiple softwares
        """

        data_model = CompareScatterDataModel(dataset)
        data_model_from_reversed = CompareScatterDataModel(
            list(reversed(dataset))
        )
        data_model_from_shuffled = CompareScatterDataModel(
            np.random.Generator(np.random.PCG64())
            .permutation(dataset)
            .tolist()
        )

        self.assertEqual(data_model.results, data_model_from_reversed.results)
        self.assertEqual(data_model.results, data_model_from_shuffled.results)

    def test_results_sorted_by_name(self):
        """
        The results stored in the data model need to be sorted to ensure that
        nothing changes about the ordering between runs. Currently name is used
        as a sorting value, bit it could be anything else, as long as it is
        consistent.
        """
        sort_value = CompareScatterDataModel([]).get_sort_key(
            self.single_result_dataset[0]
        )
        self.assertEqual(sort_value, self.single_result_dataset[0].name)

    def test_get_values_from_results_works_for_attributes(self):
        """
        Check that we can get the values from an attribute of a FittingResult
        using get_values_from_results
        """
        model = CompareScatterDataModel(self.many_result_dataset)
        values = model.get_values_from_results("name")
        self.assertEqual(
            values, [result.name for result in self.many_result_dataset]
        )

    def test_get_values_from_results_works_for_callables(self):
        """
        get_values_from_results can be provided with an axis name that links to
        a callable on a fitting result. This checks that it does not fail
        when provided with one, and outputs the correct result.
        """
        model = CompareScatterDataModel(self.many_result_dataset)
        values = model.get_values_from_results("modified_minimizer_name")
        self.assertEqual(
            values,
            [
                result.modified_minimizer_name()
                for result in self.many_result_dataset
            ],
        )

    def test_get_values_from_results_respects_callable_arguments(self):
        """
        get_values_from_results for axis can be provided with an axis name that
        links to a callable on a fitting result. This means that we need to
        also be able to pass parameters to that callable and verify that those
        arguments were included in the call.
        """

        model = CompareScatterDataModel(self.many_result_dataset)
        values = model.get_values_from_results(
            "modified_minimizer_name", with_software=True
        )
        self.assertEqual(
            values,
            [
                result.modified_minimizer_name(with_software=True)
                for result in self.many_result_dataset
            ],
        )

    def test_get_values_from_results_gets_unique_values_if_specified(self):
        model = CompareScatterDataModel(self.duplicate_name_dataset)
        unique_values = model.get_values_from_results("name", unique=True)
        self.assertEqual(unique_values, ["mock_result_1"])

    def test_list_contains_plottable_types_returns_false_if_np_inf(self):
        """
        list_contains_plottable_types should return false if provided with a
        list of all np.inf, as they cannot be plotted despite being "number"
        """

        self.assertFalse(
            CompareScatterDataModel.list_contains_plottable_types(
                [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf]
            )
        )

    def test_list_contains_plottable_types_returns_false_if_non_numeric(self):
        """
        list_contains_plottable_types should return false if provided with a
        list containing data which is not an instance of numbers.number
        """
        self.assertFalse(
            CompareScatterDataModel.list_contains_plottable_types(
                ["test", "test", "test", "test"]
            )
        )

    def test_list_contains_plottable_types_returns_true_if_any_numeric(self):
        """
        list_contains_plottable_types should return true if provided with a
        list containing any data which is an instance of numbers.number
        """
        self.assertTrue(
            CompareScatterDataModel.list_contains_plottable_types(
                [123, 456.123, np.float64(789)]
            )
        )

    def test_get_plottable_attributes_returns_expected_attributes(
        self,
    ):
        """
        Test that get_plottable_attributes returns attributes that are numeric
        and not excluded.

        Note that the function being tested will iterate through and execute
        every method on every class in the provided results list. This means
        that normal mocking cannot be used since normal mock classes will have
        methods like `assert_called_once_with` which would be executed (causing
        the test to fail).

        To circumvent this problem, a model class (`StubResult`) has been
        created to represent the final state we want the fitting result to be
        in. A mock fitting result has then been created with its __dir__
        function, its attributes and its methods replaced with those defined
        in the `StubResult` class.
        """

        # Configure the test data
        @dataclass
        class StubResult:
            # attributes which can be plotted:
            plottable_attrib = 1
            numpy_plottable_attrib = np.float16(1)

            def plottable_method():
                return 1

            # attributes which cannot be plotted:
            def unplottable_method_because_params_required(required_param):
                return required_param

            name = "test"
            unplottable_beacause_infinite = np.inf
            unplottable_beacause_wrong_type = "not a number"
            _unplottable_beacause_private = None

            def unplottable_method_because_wrong_rtype():
                return "not a number"

            # manually blacklisted attributes
            error_flag = 1

            def get_n_data_points():
                return 1

            def get_n_parameters():
                return 1

            def init_blank():
                return 1

        # Create the overwritten mock FittingResult
        mock_fitting_result = Mock(spec=FittingResult)
        mock_fitting_result.__dir__ = lambda _=mock_fitting_result: dir(
            StubResult
        )

        for attr in dir(mock_fitting_result):
            if attr.startswith("__"):
                continue
            setattr(mock_fitting_result, attr, getattr(StubResult, attr))

        # Ignore type because it is a StubResult not a FittingResult
        model = CompareScatterDataModel([mock_fitting_result])  # type: ignore

        attributes = model.get_plottable_attributes()

        self.assertListEqual(
            ["numpy_plottable_attrib", "plottable_attrib", "plottable_method"],
            attributes,
        )
