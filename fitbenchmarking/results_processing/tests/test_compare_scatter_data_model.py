import time
import unittest

import numpy as np
from parameterized import parameterized

from fitbenchmarking.results_processing.compare_scatter import (
    CompareScatterDataModel,
)
from fitbenchmarking.results_processing.tests.test_compare_scatter import (
    make_mock_fitting_result,
)


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

    # This test is non deterministic
    @parameterized.expand(["name", "modified_minimizer_name"])
    def test_get_values_from_results_cache_is_faster(self, axis):
        """
        This performs a check to see if the time taken to retrieve a result
        using get_values_from_results is lower the second time it is run.

        This is important to test, because if it does not actually provide
        any performance improvement, then it is adding unnecessary complexity.

        This test is non deterministic, but should only fail in exceptional
        circumstances, since testing on my machine showed that the caching
        gives a 4x performance improvement in practice.
        """

        model = CompareScatterDataModel(self.many_result_dataset)

        start = time.perf_counter()
        _ = model.get_values_from_results(axis)
        end = time.perf_counter()

        first_duration = end - start

        start = time.perf_counter()
        _ = model.get_values_from_results(axis)
        end = time.perf_counter()

        second_duration = end - start

        self.assertLess(second_duration, first_duration)

    def test_get_values_from_results_caches_functors_not_return_values(self):
        """
        When provided with a metric that links to a callable on a Fitting
        Result, get_values_from_results should cache a reference to the
        callable and not the result of the callable itself.

        This means that if the return values of the callable change, then
        the data returned by the function should still be valid.
        """

        model = CompareScatterDataModel(self.single_result_dataset)

        # the alternate function returns a newly generated uuid each call,
        # representing a change in return value
        model.results = [
            make_mock_fitting_result(1, alternate_minimizer_name_output=True)
        ]

        first_values = model.get_values_from_results("modified_minimizer_name")
        values_after_result_change = model.get_values_from_results(
            "modified_minimizer_name"
        )

        # if we cached the return values, the output would be the same for both
        self.assertNotEqual(first_values, values_after_result_change)

    def test_get_values_from_results_gets_unique_values_if_specified(self):
        model = CompareScatterDataModel(self.duplicate_name_dataset)
        unique_values = model.get_values_from_results("name", unique=True)
        self.assertEqual(unique_values, ["mock_result_1"])
