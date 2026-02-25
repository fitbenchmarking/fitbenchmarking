"""
This file implements a parser for the SASfit data format.
"""

import typing

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser


class SASfitParser(FitbenchmarkParser):
    """
    Parser for a SASfit problem definition file.
    """

    def _create_function(self) -> typing.Callable:
        """
        Creates callable function for a SASfit problem.

        :return: A callable function
        :rtype: callable
        """

        # need to handle multiple equations, for multiple models + background?
        equation = self._parsed_func[0]["name"]

        starting_values = self._get_starting_values()
        param_names = list(starting_values[0].keys())

        # need to be able to call SASfit model e.g. generalized Gaussian coil
