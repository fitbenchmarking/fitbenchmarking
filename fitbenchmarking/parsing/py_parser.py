"""
This file implements a parser for python problem sets.
"""

import inspect
import os
import sys
import typing
from importlib import import_module

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser


class PyParser(FitbenchmarkParser):
    """
    Parser for a python problem definition file.
    The python function should be formatted as
      f(x, var1, var2, var3 ... fixed_parameters: dict)
    """

    def _parse_fixed_params(self) -> list[dict]:
        """parses the problem definition file for a dictionary
        of fixed parameters to the objective function given by the
        keyword \"fixed_params\"

        Returns:
            list[dict]: a list of a dictionary containing keys
            and fixed values of the selected fixed parameters"
        """
        return self._parse_string("fixed_params")

    def _create_function(self) -> typing.Callable:
        """
        Process the import into a callable.
        Expected function format:
        function='module=functions/py_funcs,func=model'
        :return: A callable function
        :rtype: callable
        """
        # import the objective function
        pf: dict = self._parsed_func[0]
        path = os.path.join(os.path.dirname(self._filename), pf["module"])
        sys.path.append(os.path.dirname(path))
        module = import_module(os.path.basename(path))
        fun = getattr(module, pf["func"])
        self._equation = fun.__name__

        sig = inspect.signature(fun)
        # params[0] should be x so start after.
        all_param_names = list(sig.parameters.keys())[1:]

        fixed_params = (
            self._parse_fixed_params()[0]
            if "fixed_params" in self._entries
            else {}
        )
        pf |= fixed_params
        is_fixed = [param in fixed_params for param in all_param_names]

        all_params = [
            (all_param_names[i], pf[n], is_fixed[i])
            for i, n in enumerate(all_param_names)
        ]

        # This list will be used to input fixed values alongside unfixed ones
        all_params_dict = {name: value for name, value, _ in all_params}

        starting_params = {
            name: value for name, value, fixed in all_params if not fixed
        }
        self._starting_values = [starting_params]

        def wrapped(x, *p):
            """
            Only update non-fixed parameters
            """
            update_dict = dict(zip(starting_params.keys(), p))
            all_params_dict.update(update_dict)

            return fun(x, *all_params_dict.values())

        return wrapped

    def _get_equation(self) -> str:
        """
        Returns the equation in the problem definition file.

        :return: The equation in the problem definition file.
        :rtype: str
        """
        return self._equation

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        return self._starting_values
