"""
This file implements a parser for the SASfit data format.
"""

import ctypes
import importlib.util
import os
import re
import sys
import typing
from itertools import repeat
from pathlib import Path

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

    Two styles of ``function`` entry are supported:

    * a series of SASfit plugin names and their parameters, e.g.
      ``function = 'name=polynom,p0=0.0;name=Gaussian__coil,Rg=4.0'``
    * a single python module, named the same way, e.g.
      ``function = 'name=functions/multifit.py,Rg=4.0'``, where the name is
      a path relative to the problem definition file. This is intended for
      models which cannot easily be expressed as a sum of SASfit plugins,
      such as fits where a size distribution, a form factor and a
      structure factor are combined across several datasets.

    The ``fixed_params`` entry holds the parameters which are not fitted.
    For a multifit problem it may give one set of them per dataset,
    separated by semi-colons, so that a parameter which the experiment
    fixes to a different value in each dataset (the solvent scattering
    length density of a contrast variation series, say) can be held at its
    own value in each of them.
    """

    _PARAM_IGNORE_LIST = ["name"]

    def __init__(self, filename, options):
        super().__init__(filename, options)

        # populated by ``_load_function_module`` when the ``function`` entry
        # points at a python module rather than a list of SASfit plugins
        self._function_module = None

    def _is_python_function(self) -> bool:
        """
        Returns true if the ``function`` entry names a python module rather
        than a set of SASfit plugins.

        :raises ParsingError: If a python module is combined with any other
                              function.
        :return: True if the function is defined in a python module.
        :rtype: bool
        """
        names = [str(func.get("name", "")) for func in self._parsed_func or []]
        modules = [name for name in names if name.endswith(".py")]

        if modules and len(names) > 1:
            raise ParsingError(
                f"The function module '{modules[0]}' cannot be combined with "
                "other functions; it must be the only one in the 'function' "
                "entry of the problem definition file."
            )
        return bool(modules)

    def _load_function_module(self):
        """
        Import the python module named by the ``function`` entry. The path is
        taken to be relative to the directory holding the problem definition
        file.

        :raises ParsingError: If the module cannot be found or imported.
        :return: The imported module
        :rtype: ModuleType
        """
        if self._function_module is not None:
            return self._function_module

        module_path = (
            Path(self._filename).parent / self._parsed_func[0]["name"]
        )
        if not module_path.is_file():
            raise ParsingError(
                f"Could not find the function module '{module_path}' "
                "given in the problem definition file."
            )

        spec = importlib.util.spec_from_file_location(
            module_path.stem, module_path
        )
        if spec is None or spec.loader is None:
            raise ParsingError(f"Could not import '{module_path}'.")

        module = importlib.util.module_from_spec(spec)
        # register the module so that dataclasses/pickling inside it behave
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        if not hasattr(module, "fit_function"):
            raise ParsingError(
                f"The function module '{module_path}' must define a "
                "'fit_function(x, **params)' callable."
            )

        self._function_module = module
        return module

    def _get_equation(self) -> str:
        """
        Returns the equation in the problem definition file.

        :return: The equation in the problem definition file.
        :rtype: str
        """
        if self._is_python_function():
            module = self._load_function_module()
            return getattr(module, "equation", super()._get_equation())
        return super()._get_equation()

    def _create_function(self) -> typing.Callable:
        """
        Creates callable function for a SASfit problem.

        The same function describes every dataset of a multifit problem; what
        differs between the datasets is the values of the parameters it is
        given. Datasets which hold a parameter at a different fixed value
        get their own function, see ``_create_dataset_functions``.

        :return: A callable function
        :rtype: callable
        """
        return self._create_function_with(self._fixed_params()[0])

    def _create_dataset_functions(self) -> list[typing.Callable] | None:
        """
        Creates one callable per dataset for a multifit problem which holds
        a parameter at a different fixed value in each of its datasets.

        :return: One callable per dataset, or None if the same fixed
                 parameters are used for every dataset
        :rtype: list of callable, or None
        """
        fixed_params = self._fixed_params()
        if len(fixed_params) == 1:
            return None
        return [self._create_function_with(fixed) for fixed in fixed_params]

    def _create_function_with(self, fixed_params: dict) -> typing.Callable:
        """
        Creates a callable function for one dataset of a SASfit problem,
        holding the given parameters at the values given there.

        :param fixed_params: The parameters which are not fitted, and the
                             value each of them is held at
        :type fixed_params: dict

        :return: A callable function
        :rtype: callable
        """
        if self._is_python_function():
            return self._create_function_from_module(fixed_params)
        return self._create_function_from_plugins(fixed_params)

    def _create_function_from_module(
        self, fixed_params: dict
    ) -> typing.Callable:
        """
        Creates a callable function from the ``fit_function`` of the python
        module named in the ``function`` entry.

        As for the plugins, the parameters are the ones named in the
        ``function`` entry, and those in ``fixed_params`` are held at the
        value given there. They are passed on to ``fit_function`` by name.

        :param fixed_params: The parameters which are not fitted, and the
                             value each of them is held at
        :type fixed_params: dict

        :return: A callable function
        :rtype: callable
        """
        fit_function = self._load_function_module().fit_function

        params_to_fit_dict = self._get_starting_values()[0]
        all_params_dict = params_to_fit_dict | fixed_params

        def wrapped(x, *p):
            params = all_params_dict | dict(zip(params_to_fit_dict, p))
            return fit_function(x, **params)

        return wrapped

    def _create_function_from_plugins(
        self, fixed_params: dict
    ) -> typing.Callable:
        """
        Creates callable function from the SASfit plugins named in the
        ``function`` entry of the problem definition file.

        :param fixed_params: The parameters which are not fitted, and the
                             value each of them is held at
        :type fixed_params: dict

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

        # combine the fitted and the fixed params into the dict of all
        # params to be passed to the fit function
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

    def _fixed_params(self) -> list[dict]:
        """
        The parameters which are not fitted, and the value each of them is
        held at, for each dataset of the problem.

        The ``fixed_params`` entry holds either one set of fixed
        parameters, which is then used for every dataset, or, for a
        multifit problem, one set per dataset separated by semi-colons,
        e.g. ``fixed_params = 'eta_solv=1.8;eta_solv=1.9'``. The latter is
        how a parameter which the experiment fixes to a different value in
        each dataset is given.

        :raises ParsingError: If the number of sets of fixed parameters is
                              neither one nor the number of datasets, or if
                              the sets do not fix the same parameters.
        :return: One set of fixed parameters, or one per dataset
        :rtype: list of dict
        """
        if "fixed_params" not in self._entries:
            return [{}]

        fixed_params = self._parse_fixed_params()
        if len(fixed_params) == 1:
            return fixed_params

        dataset_count = len(self._get_input_file_names())
        if len(fixed_params) != dataset_count:
            raise ParsingError(
                "The 'fixed_params' entry of the problem definition file "
                f"gives {len(fixed_params)} sets of fixed parameters, but "
                f"the problem has {dataset_count} dataset(s). Give either "
                "one set, which is then used for every dataset, or one set "
                "per dataset, separated by semi-colons."
            )

        # the parameters which are fitted have to be the same for every
        # dataset, so the same parameters have to be fixed in each of them
        names = [tuple(fixed) for fixed in fixed_params]
        if len(set(names)) != 1:
            raise ParsingError(
                "Every set of fixed parameters in the 'fixed_params' entry "
                "of the problem definition file must fix the same "
                f"parameters. Got {[list(n) for n in names]}."
            )

        return fixed_params

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        fixed_params = self._fixed_params()[0]
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

    def _set_data_points(self, data_points: list, fit_ranges: list) -> None:
        """
        Sets the data points and fit range data in the fitting problem.

        A problem with several input files keeps one entry per dataset, the
        same shape the mantid parser uses for a multifit.

        :param data_points: A list of data points.
        :type data_points: list
        :param fit_ranges: A list of fit ranges.
        :type fit_ranges: list
        """
        if not self._is_multifit():
            super()._set_data_points(data_points, fit_ranges)
            return

        self.fitting_problem.data_x = [d["x"] for d in data_points]
        self.fitting_problem.data_y = [d["y"] for d in data_points]
        self.fitting_problem.data_e = [d.get("e", None) for d in data_points]

        if not fit_ranges:
            fit_ranges = list(repeat({}, len(data_points)))

        self.fitting_problem.start_x = [
            f["x"][0] if "x" in f else None for f in fit_ranges
        ]
        self.fitting_problem.end_x = [
            f["x"][1] if "x" in f else None for f in fit_ranges
        ]

    def _set_additional_info(self) -> None:
        """
        Sets any additional info for a fitting problem.
        """
        if self.fitting_problem.multifit:
            self.fitting_problem.additional_info["ties"] = re.findall(
                r"['\"](.*?)['\"]", self._entries.get("ties", "")
            )
