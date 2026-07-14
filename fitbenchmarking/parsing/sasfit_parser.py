"""
This file implements a parser for the SASfit data format.
"""

import ctypes
import os
import typing

import numpy as np

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser
from fitbenchmarking.utils.exceptions import ParsingError

# check that SASFIT_LOCATION environment variable is set
# before importing SASStudio functions
if "SASFIT_LOCATION" not in os.environ:
    raise ParsingError(
        "SASFIT_LOCATION environment variable is not set."
        " Please set it to the location of the SASfit installation."
    )

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
        scattering_contributions = {}
        param_names = {}

        # loop over each SASfit plugin included in the problem definition file
        for func in self._parsed_func:
            # some SASfit functions have spaces in their names, but the
            # problem definition file uses double underscores instead of spaces
            func_name = func["name"].replace("__", " ")
            functions_to_call.append(func_name)
            sasfit_plugin = Plugin(func_name)
            func_param_names = list(
                sasfit_plugin.parameter_descriptions.keys()
            )
            param_names[func_name] = func_param_names
            scattering_contributions[func_name] = Scattering_Contribution()
            scattering_contributions[func_name].load_form_factor(func_name)

        # parse fixed params to create dict of all params
        # to be passed to the fit function
        fixed_params = (
            self._parse_fixed_params()[0]
            if "fixed_params" in self._entries
            else {}
        )
        params_to_fit_dict = self._get_starting_values()[0]
        all_params_dict = params_to_fit_dict | fixed_params

        def fitFunction(x, *p):
            x = np.atleast_1d(x)
            updated_params_dict = dict(zip(all_params_dict.keys(), p))
            y_vals = np.zeros(len(x))
            for plugin in functions_to_call:
                f_params = [
                    updated_params_dict[name] for name in param_names[plugin]
                ]
                scattering_contributions[plugin].set_form_factor_parameters(
                    np.array(f_params)
                )
                # SASfit functions are not vectorized,
                # so we need to loop over the x values
                for i, x_val in enumerate(x):
                    y_vals[i] += scattering_contributions[
                        plugin
                    ].form_factor_scattering_intensity(
                        ctypes.c_double(x_val),
                        scattering_contributions[plugin].form_factor_params,
                    )
            return y_vals

        # wrap the function to update the parameter dictionary with
        # the current values of the parameters being fitted
        def wrapped(x, *p):
            update_dict = dict(zip(params_to_fit_dict.keys(), p))
            all_params_dict.update(update_dict)
            return fitFunction(x, *all_params_dict.values())

        return wrapped

    def _parse_fixed_params(self) -> list[dict]:
        """parses the problem definition file for a dictionary
        of fixed parameters to the objective function given by the
        keyword \"fixed_params\"

        Returns:
            list[dict]: a list of a dictionary containing keys
            and fixed values of the selected fixed parameters.
        """
        return self._parse_string("fixed_params")

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        fixed_params = (
            self._parse_fixed_params()[0]
            if "fixed_params" in self._entries
            else {}
        )
        # ensure that starting values only contains parameters that
        # are not included in the fixed_params list
        return [
            {
                k: v
                for func in self._parsed_func
                for k, v in func.items()
                if k not in self._PARAM_IGNORE_LIST and k not in fixed_params
            }
        ]
