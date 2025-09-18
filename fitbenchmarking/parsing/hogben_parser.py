"""
This file implements a parser for HOGBEN problem sets.
"""

import os
import pickle
import typing

import numpy as np

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser


class HogbenParser(FitbenchmarkParser):
    """
    Parser for a Hogben problem definition file.
    """

    def _create_function(self) -> typing.Callable:
        """
        Process the reflectometry model into a callable.

        Expected function format:
        function='function=model.pkl'

        :return: A callable function
        :rtype: callable
        """

        pf = self._parsed_func[0]
        model = os.path.join(
            os.path.dirname(self._filename), "Models", pf["function"]
        )
        with open(model, "rb") as f:
            refnx_model = pickle.load(f)

        self._equation = pf["function"].split(".")[0].replace("_", " ")

        varying_params = refnx_model.parameters.varying_parameters()

        # remove spaces and hyphens from parameter names
        p_names = [
            " ".join(p.name.replace("-", "").split()).replace(" ", "_")
            for p in list(varying_params)
        ]
        svals = np.array(varying_params)

        self._starting_values = [dict(zip(p_names, svals))]

        def fitFunction(x, *params):
            if len(params) == refnx_model.parameters.nvary():
                for idx, param in enumerate(varying_params):
                    param.value = params[idx]
            y = refnx_model(x, p=refnx_model.parameters.pvals)
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
