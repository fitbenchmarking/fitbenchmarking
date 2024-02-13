"""
This file implements a parser for the quickBayes data format.
"""
import typing
import numpy as np
from quickBayes.functions.qse_function import QSEFunction
from quickBayes.functions.BG import FlatBG


from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser


class quickBayesParser(FitbenchmarkParser):
    """
    Parser for a Mantid problem definition file.
    """

    def __init__(self, filename, options):
        super().__init__(filename, options)

    def parse(self):

        fp = super().parse()
        return fp


    def _create_function(self) -> typing.Callable:
        """
        Processing the function in the Mantid problem definition into a
        python callable.

        :return: A callable function
        :rtype: callable
        """
        # Get file for resolution
        data = self._entries['function']
        # load resolution file
        res = np.loadtxt(data, delimiter='\t')
        res_x = np.zeros(len(res))
        res_y = np.zeros(len(res))
        for j in range(len(res)):
            res_x[j] = res[j][0]
            res_y[j] = res[j][1]

        # make function
        bg = FlatBG()
        fit_function = QSEFunction(bg, True, res_x, res_y, -.4, .4)
        fit_function.add_single_SE()
        
        # manually set stuff
        self._equation = 'qse'
        self._starting_values = [{'BGConstant':0.0,
                                  'Amplitude': .02,
                                  'Centre': -0.06,
                                  'Amplitude2': .12,
                                  'tau': 31.5,
                                  'beta': .7}]

        return fit_function

    def _get_equation(self, *args, **kwargs):
        """
        Override the default function parsing as this is offloaded to mantid.
        """
        return self._equation


    def _parse_single_function(cls, func: str) -> dict:
        return {}

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        return self._starting_values
