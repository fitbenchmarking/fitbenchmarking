"""
This file implements a parser for the IVP data format.
"""
from collections import OrderedDict

import importlib
import inspect
import os
import sys
import typing
import numpy as np

from scipy.integrate import solve_ivp

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser
from fitbenchmarking.utils.exceptions import ParsingError


class IVPParser(FitbenchmarkParser):
    """
    Parser for a IVP problem definition file.
    """

    def _create_function(self) -> typing.Callable:
        """
        Process the IVP formatted function into a callable.

        Expected function format:
        function='module=my_python_file,func=my_function_name,
                  step=0.5,p0=0.1,p1...'

        :return: A callable function
        :rtype: callable
        """
        if len(self._parsed_func) > 1:
            raise ParsingError('Could not parse IVP problem. Please ensure '
                               'only 1 function definition is present')

        pf = self._parsed_func[0]
        path = os.path.join(os.path.dirname(self._filename), pf['module'])
        sys.path.append(os.path.dirname(path))
        module = importlib.import_module(os.path.basename(path))
        fun = getattr(module, pf['func'])
        time_step = pf['step']
        sig = inspect.signature(fun)
        # params[0] should be t
        # parmas[1] should be x so start after.
        p_names = list(sig.parameters.keys())[2:]

        # pylint: disable=attribute-defined-outside-init
        self._equation = fun.__name__
        self._starting_values = [OrderedDict([(n, pf[n]) for n in p_names])]

        def fitFunction(x, *p):
            if len(x.shape) == 1:
                x = np.array([x])
            y = np.zeros_like(x)
            for i, inp in enumerate(x):
                soln = solve_ivp(fun=fun,
                                 t_span=[0, time_step],
                                 y0=inp,
                                 args=p,
                                 vectorized=False)
                y[i, :] = soln.y[:, -1]
            return y

        return fitFunction

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
