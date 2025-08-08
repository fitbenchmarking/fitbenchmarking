"""
This file implements a parser for python problem sets.
"""
import os
import sys
import typing
from functools import partial
from importlib import import_module

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser


class PyParser(FitbenchmarkParser):
    """
    Parser for a python problem definition file.
    The python function should be formatted as
      f(x, var1, var2, var3 ... fixed_parameters: dict)
    """

    def _parse_fixed_args(self) -> list[dict]:
        return self._parse_string("fixed_arguments")

    def _parse_variables(self) -> list[dict]:
        return self._parse_string("variable_arguments")

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
        path = os.path.join(os.path.dirname(self._filename), pf['module'])
        sys.path.append(os.path.dirname(path))
        module = import_module(os.path.basename(path))
        fun = getattr(module, pf['func'])

        # get the fixed and variable function arguments
        self.fixed_args: dict = self._parse_fixed_args()[0]

        # define function which fixes variables
        reduced_fun = partial(fun, fixed_parameters=self.fixed_args)
        self._equation = fun.__name__

        # set variable parameters starting values
        self._starting_values = self._parse_variables()
        print(self._starting_values)
        return reduced_fun

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
