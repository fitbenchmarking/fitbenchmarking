"""
This file implements a parser for the Mantid data format.
This parser gives Mantid an advantage for Mantid problem
files, as Mantid does an internal function evaluation.
"""

import re
from typing import Union

import numpy as np

from fitbenchmarking.parsing.mantiddev_parser import MantidDevParser
from fitbenchmarking.utils.exceptions import ParsingError


class MantidParser(MantidDevParser):
    """
    Parser for mantid (keeps original behaviour)
    """

    def _set_additional_info(self) -> None:
        """
        Sets any additional info for a fitting problem.
        """
        super()._set_additional_info()
        self.fitting_problem.additional_info["mantid_equation"] = (
            self._entries["function"]
        )

    def _is_multistart(self) -> bool:
        """
        Returns true if the problem needs to be set up for
        multi-start analysis. n_fits must be present in the
        problem definition file. If n_fits is present, then
        parameter_means and parameter_sigmas must also be
        specified. If any of these are missing, a ParsingError
        is raised.

        :return: True if multi start analysis enabled.
        :rtype: bool
        """
        if "n_fits" not in self._entries:
            return False
        else:
            # Verify parameter_means and parameter_sigmas are also
            # specified in the problem definition file
            if "parameter_means" not in self._entries:
                raise ParsingError(
                    "Specify the 'parameter_means' for each parameter "
                    "in the problem defination file to run the multi-"
                    "start analysis. These values are the means of the "
                    "gaussian distributions used to generate the starting "
                    "values of the parameters."
                )
            if "parameter_sigmas" not in self._entries:
                raise ParsingError(
                    "Specify the 'parameter_sigmas' for each parameter "
                    "in the problem defination file to run the multi-"
                    "start analysis. These are the standard deviations "
                    "used to create a gaussian distribution from "
                    "which the starting values will be sampled."
                )
            return True

    def _get_starting_values(self) -> Union[list[float], list[dict]]:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list[float], list[dict]
        """
        if self.fitting_problem.multistart:
            # Parse n_fits, parameter means and sigma values
            n_fits = self._parse_function_value(self._entries["n_fits"])
            parameter_means = self._parse_single_function(
                self._entries["parameter_means"]
            )
            parameter_sigmas = self._parse_single_function(
                self._entries["parameter_sigmas"]
            )

            # Process names
            all_names = list(
                re.findall(r"\{(.*?)\}", self._entries["function"])
            )
            parameter_mean_names = list(parameter_means.keys())
            parameter_sigma_names = list(parameter_sigmas.keys())

            # Check if parameter_means and parameter_sigmas are
            # specified for all variables.
            if missing := set(all_names) - set(parameter_mean_names):
                raise ParsingError(
                    f"The 'parameter_means' for {missing} need to be "
                    "specified for the multi-start analysis."
                )
            if missing := set(all_names) - set(parameter_sigma_names):
                raise ParsingError(
                    f"The 'parameter_sigmas' for {missing} need to be "
                    "specified for the multi-start analysis."
                )

            # Set seed if provided
            if "seed" in self._entries:
                rng = np.random.default_rng(
                    seed=self._parse_function_value(self._entries["seed"])
                )
            else:
                rng = np.random.default_rng()

            # Generate starting values
            starting_values = [{} for _ in range(n_fits)]
            for name in all_names:
                samples = rng.normal(
                    loc=parameter_means[name],
                    scale=parameter_sigmas[name],
                    size=n_fits,
                )
                for ix in range(n_fits):
                    starting_values[ix].update({name: samples[ix]})

            # Update the mantid equation with the starting values
            self._entries["function"] = self._update_mantid_equation(
                starting_values
            )

        else:
            starting_values = super()._get_starting_values()

        return starting_values

    def _update_mantid_equation(self, starting_values) -> list[str]:
        """
        Used to update the mantid equation placeholders
        when the problem is being set up for multi-start
        analysis.

        :return: A list of mantid equations with varying starting values.
        :rtype: list[str]
        """
        equations = []
        for starting_value in starting_values:
            function = self._entries["function"]
            for key, value in starting_value.items():
                function = function.replace(f"{{{key}}}", str(value))
            equations.append(function)
        return equations
