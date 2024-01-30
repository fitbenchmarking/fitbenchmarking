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
    """

    def _create_function(self) -> typing.Callable:
        """
        Process the import into a callable.

        Expected function format:
        function='module=functions/py_funcs,func=model'

        :return: A callable function
        :rtype: callable
        """

        pf = self._parsed_func[0]
        path = os.path.join(os.path.dirname(self._filename), pf['module'])
        sys.path.append(os.path.dirname(path))
        module = import_module(os.path.basename(path))
        fun = getattr(module, pf['func'])
        sig = inspect.signature(fun)
        # parmas[0] should be x so start after.
        p_names = list(sig.parameters.keys())[1:]

        # pylint: disable=attribute-defined-outside-init
        self._equation = fun.__name__
        self._starting_values = [{n: pf[n] for n in p_names}]
        return fun

    def _get_equation(self) -> str:
        """
        Returns the equation in the problem definition file.

        :return: The equation in the problem definition file.
        :rtype: str
        """
        return self._parsed_func[0]['func']

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        return self._starting_values
