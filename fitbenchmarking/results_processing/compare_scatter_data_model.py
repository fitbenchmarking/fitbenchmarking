import numbers
import re
from dataclasses import dataclass

import numpy as np

from fitbenchmarking.utils.fitbm_result import FittingResult


@dataclass(frozen=True)
class CompareScatterDataModel:
    results: list[FittingResult]

    def __post_init__(self):
        self.results.sort(key=self.get_sort_key)

    @staticmethod
    def get_sort_key(result: FittingResult):
        return result.name

    def get_plottable_attributes(self) -> list[str]:
        """
        Get a list of attributes that make logical sense to plot on a scatter
        plot. Works by reading all attributes of the FittingResults and
        removing any which return a non-numeric value.

        :return: list of attributes that can be plotted
        :rtype: list[str]
        """

        plottable_attributes = [
            "accuracy",
            "energy",
            "first_runtime",
            "func_evals",
            "get_n_data_points",
            "get_n_parameters",
            "harmonic_runtime",
            "iteration_count",
            "maximum_runtime",
            "mean_runtime",
            "median_runtime",
            "minimum_runtime",
            "norm_acc",
            "norm_energy",
            "norm_runtime",
            "runtime",
            "trim_runtime",
        ]

        return [
            attribute
            for attribute in plottable_attributes
            if self.list_contains_plottable_types(
                self.get_values_from_results(attribute)
            )
        ]

    _known_mappings = {
        "accuracy": "Accuracy (χ²)",
        "energy": "Energy (kWh)",
        "first_runtime": "First Runtime (s)",
        "func_evals": "N Function Evaluations",
        "harmonic_runtime": "Harmonic Runtime (s)",
        "maximum_runtime": "Maximum Runtime (s)",
        "mean_runtime": "Mean Runtime (s)",
        "median_runtime": "Median Runtime (s)",
        "minimum_runtime": "Minimum Runtime (s)",
        "norm_acc": "Normalised Accuracy",
        "norm_energy": "Normalised Energy",
        "norm_runtime": "Normalised Runtime",
        "runtime": "Runtime (s)",
        "trim_runtime": "Trimmed Mean Runtime (s)",
        "get_n_data_points": "N Data Points",
        "get_n_parameters": "N Parameters",
    }

    def get_readable_attr_name(self, attribute: str):
        """
        Given an attribute name, return a human readable name for use in the
        title text for the plot. This means in title case, with underscores
        replaced with spaces and units added if applicable and known.

        :param attribute: A machine readable name of an attribute
        :type attribute: str

        :return: The name of the attribute in a human readable format
        :rtype: str
        """
        if attribute in self._known_mappings:
            return self._known_mappings[attribute]
        return re.sub("_", " ", attribute).title()

    def get_attr_from_readable_name(self, name: str):
        """
        Given a human readable name, return the attribute name.

        :param name: A human readable name of an attribute
        :type name: str

        :return: The actual attribute name
        :rtype: str
        """
        for attr, readable_name in self._known_mappings.items():
            if readable_name == name:
                return attr
        # If not in known mappings, try to reverse the general conversion
        return name.lower().replace(" ", "_")

    @staticmethod
    def list_contains_plottable_types(values: list):
        """
        Return True if the provided list contains at least one numeric value,
        and is not entirely unplottable (i.e. np.inf)

        :param values: list of values to check
        :type values: list

        :return: if the list can be plotted on a scatter plot
        :rtype: bool
        """
        can_be_plotted = [
            (
                isinstance(value, numbers.Number)
                and not (value is np.nan or value is np.inf)
                and not isinstance(value, bool)
            )
            for value in values
        ]

        return any(can_be_plotted)

    def get_values_from_results(
        self, attribute: str, unique=False, **func_kwargs
    ) -> list:
        """
        Given the name of an attribute or method, retrieve the value of that
        attribute/method from each fitting result. Arguments can be passed to
        methods using func_kwargs.

        :param attribute: The attribute/method to get from every result stored
            in the data model
        :type attribute: str
        :param unique: Whether to return a list of only unique results or
            allow the list to include duplicates
        :type unique: bool
        :param func_kwargs: The arguments to send if the metric is callable
        :type func_kwargs: dict

        :return: List of values retrieved, presented in the order that the
            items appear in the model
        :rtype: list[any]
        """

        # in the case of name and normalized values, a function call is
        # required to retrieve the data, so we need to check if we have been
        # passed an attribute or method name

        values = []
        if attribute is None:
            raise ValueError("Attribute name cannot be None")
        if callable(getattr(self.results[0], attribute)):
            for result in self.results:
                func = getattr(result, attribute)
                values.append(func(**func_kwargs))
            if unique:
                values = list(dict.fromkeys(values))

        else:
            if func_kwargs:
                raise TypeError(
                    f"Attribute {attribute} is not callable, but "
                    "kwargs were provided"
                )

            values = [getattr(result, attribute) for result in self.results]
            if unique:
                values = list(dict.fromkeys(values))
        return values
