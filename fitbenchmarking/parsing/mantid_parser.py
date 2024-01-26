"""
This file implements a parser for the Mantid data format.
This parser gives Mantid an advantage for Mantid problem
files, as Mantid does an internal function evaluation.
"""
from fitbenchmarking.parsing.mantiddev_parser import MantidDevParser


class MantidParser(MantidDevParser):

    def _set_additional_info(self) -> None:
        """
        Sets any additional info for a fitting problem.
        """
        super()._set_additional_info()
        self.fitting_problem.additional_info['mantid_equation'] \
            = self._entries['function']
