"""
This file implements a parser for the quickBayes data format.
"""
import typing
import numpy as np
from quickBayes.functions.qse_function import QSEFunction
from quickBayes.functions.BG import FlatBG
from quickBayes.functions.qldata_function import QlDataFunction


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
        
        inf = np.inf
        bg.set_bounds([-inf], [inf])
        fit_function = QlDataFunction(bg, True, res_x, res_y, -.4, .4)
        fit_function.add_single_lorentzian()
        #fit_function = QSEFunction(bg, True, res_x, res_y, -.4, .4)
        #fit_function.add_single_SE()
        fit_function.set_delta_bounds([-inf, -inf], [inf, inf])
        fit_function.set_delta_guess([0.02, -0.06])
        fit_function.set_func_guess([.12, -0.06, 0.02])
        fit_function.set_func_bounds([-inf, -inf, -inf], [inf, inf, inf])
        #fit_function.set_func_guess([.12, -0.06, 31.5, .7])
        #fit_function.set_func_bounds([0.0, -0.4, 1, .0], [10, 0.4, 100, 1])
        # manually set stuff
        self._equation = 'qse'
        tmp_dict = fit_function.report({}, *fit_function.get_guess())


        #self._starting_values = [{'N1_f1_BG_constant':0.0,
        #                            'N1_f2_f1_Amplitude': .02,
        #                            'N1_f2_f1_Centre': -0.06,
        #                            'N1_f2_f2_Amplitude': .12,
        #                            'N1_f2_f2_tau': 31.5,
        #                            'N1_f2_f2_beta': .7}]
 
        self._starting_values = [{'N1:f1_BG_constant':0.0,
                                  'N1:f2_f1_Amplitude': .02,
                                  'N1:f2_f1_Centre': -0.06,
                                  'N1:f2_f2_Amplitude': .12,
                                  'N1:f2_f2_Gamma': 0.02,
                                  }]
        
        self.fitting_problem._starting_values = self._starting_values
        #self.fitting_problem.set_value_ranges(ranges)
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
