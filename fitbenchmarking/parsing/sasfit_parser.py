"""
This file implements a parser for the SASfit data format.
"""

import ctypes
import typing

import numpy as np

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser
from fitbenchmarking.parsing.SASStudio_functions import (
    Plugin,
    Scattering_Contribution,
)


class SASfitParser(FitbenchmarkParser):
    """
    Parser for a SASfit problem definition file.
    """

    _PARAM_IGNORE_LIST = ["name"]

    def _create_function(self) -> typing.Callable:
        """
        Creates callable function for a SASfit problem.

        :return: A callable function
        :rtype: callable
        """

        functions_to_call = []
        all_param_names = []
        scattering_contributions = {}
        param_names = {}
        for func in self._parsed_func:
            func_name = func["name"].replace("_", " ")
            functions_to_call.append(func_name)
            sasfit_plugin = Plugin(func_name)
            func_param_names = list(
                sasfit_plugin.parameter_descriptions.keys()
            )
            param_names[func_name] = func_param_names
            all_param_names.extend(func_param_names)
            scattering_contributions[func_name] = Scattering_Contribution()
            scattering_contributions[func_name].load_form_factor(func_name)

        all_param_values = [
            {
                key: val
                for f in self._parsed_func
                for key, val in f.items()
                if key not in self._PARAM_IGNORE_LIST
            }
        ][0]

        fixed_params = (
            self._parse_fixed_params()[0]
            if "fixed_params" in self._entries
            else {}
        )
        all_param_values |= fixed_params
        is_fixed = [param in fixed_params for param in all_param_names]

        all_params = [
            (n, all_param_values[n], is_fixed[i])
            for i, n in enumerate(all_param_names)
        ]
        starting_params = {
            name: value for name, value, fixed in all_params if not fixed
        }
        self._starting_values = [starting_params]

        def fitFunction(x, *p):
            x = np.atleast_1d(x)
            param_dict = dict(zip(all_param_values.keys(), p))
            y_vals = np.zeros(len(x))
            for f in functions_to_call:
                f_params = [param_dict[name] for name in param_names[f]]
                scattering_contributions[f].set_form_factor_parameters(
                    np.array(f_params)
                )
                for i in range(len(x)):
                    y_vals[i] += scattering_contributions[
                        f
                    ].form_factor_scattering_intensity(
                        ctypes.c_double(x[i]),
                        scattering_contributions[f].form_factor_params,
                    )
            return y_vals

        def wrapped(x, *p):
            update_dict = dict(zip(starting_params.keys(), p))
            all_param_values.update(update_dict)
            return fitFunction(x, *all_param_values.values())

        return wrapped

    def _parse_fixed_params(self) -> list[dict]:
        """parses the problem definition file for a dictionary
        of fixed parameters to the objective function given by the
        keyword \"fixed_params\"

        Returns:
            list[dict]: a list of a dictionary containing keys
            and fixed values of the selected fixed parameters"
        """
        return self._parse_string("fixed_params")

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        return self._starting_values
