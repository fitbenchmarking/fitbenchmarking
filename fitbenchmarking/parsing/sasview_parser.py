"""
This file implements a parser for the SASView data format.
"""
import typing

from sasmodels.bumps_model import Experiment, Model
from sasmodels.core import load_model
from sasmodels.data import empty_data1D

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser


class SASViewParser(FitbenchmarkParser):
    """
    Parser for a SASView problem definition file.
    """

    def _create_function(self) -> typing.Callable:
        """
        Creates callable function for a SASView problem.

        :return: A callable function
        :rtype: callable
        """
        equation = self._parsed_func[0]['name']
        starting_values = self._get_starting_values()
        param_names = list(starting_values[0].keys())

        def fitFunction(x, *tmp_params):

            model = load_model(equation)

            data = empty_data1D(x)
            param_dict = dict(zip(param_names, tmp_params))

            model_wrapper = Model(model, **param_dict)
            func_wrapper = Experiment(data=data, model=model_wrapper)

            return func_wrapper.theory()

        return fitFunction
