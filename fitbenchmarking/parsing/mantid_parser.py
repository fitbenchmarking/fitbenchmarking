"""
This file implements a parser for the Mantid data format.
"""
from collections import OrderedDict

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser

import_success = {}
try:
    import mantid.simpleapi as msapi
    import_success['mantid'] = (True, None)
except ImportError as ex:
    import_success['mantid'] = (False, ex)


# pylint: disable=too-many-branches
class MantidParser(FitbenchmarkParser):
    """
    Parser for a Mantid problem definition file.
    """

    def __init__(self, filename, options):
        super().__init__(filename, options, import_success)

    def _create_function(self):
        """
        Processing the function in the Mantid problem definition into a
        python callable.

        :return: A callable function
        :rtype: callable
        """
        # Get mantid to build the function
        ifun = msapi.FunctionFactory.createInitialized(
            self._entries['function'])

        # Extract the parameter info
        all_params = [(ifun.getParamName(i),
                       ifun.getParamValue(i),
                       ifun.isFixed(i))
                      for i in range(ifun.nParams())]

        # This list will be used to input fixed values alongside unfixed ones
        all_params_dict = {name: value
                           for name, value, _ in all_params}

        # Extract starting parameters
        params = {name: value
                  for name, value, fixed in all_params
                  if not fixed}
        # pylint: disable=attribute-defined-outside-init
        self._starting_values = [OrderedDict(params)]

        # Convert to callable
        fit_function = msapi.FunctionWrapper(ifun)

        # Use a wrapper to inject fixed parameters into the function
        def wrapped(x, *p):
            # Use the full param dict from above, but update the non-fixed
            # values
            update_dict = dict(zip(params.keys(), p))
            all_params_dict.update(update_dict)

            return fit_function(x, *all_params_dict.values())

        return wrapped

    def _is_multifit(self) -> bool:
        """
        Returns true if the problem is a multi fit problem.
        """
        return self._entries['input_file'][0] == '['

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.
        """
        return self._starting_values

    def _set_data_points(self, data_points: list, fit_ranges: list) -> None:
        """
        Sets the data points and fit range data in the fitting problem.
        """
        if self.fitting_problem.multifit:
            num_files = len(data_points)
            self.fitting_problem.data_x = [d['x'] for d in data_points]
            self.fitting_problem.data_y = [d['y'] for d in data_points]
            self.fitting_problem.data_e = [d['e'] if 'e' in d else None
                                           for d in data_points]

            if not fit_ranges:
                fit_ranges = [{} for _ in range(num_files)]

            self.fitting_problem.start_x = [f['x'][0] if 'x' in f else None
                                            for f in fit_ranges]
            self.fitting_problem.end_x = [f['x'][1] if 'x' in f else None
                                          for f in fit_ranges]

        else:
            super()._set_data_points(data_points, fit_ranges)

    def _set_additional_info(self) -> None:
        """
        Sets any additional info for a fitting problem.
        """
        self.fitting_problem.additional_info['mantid_equation'] \
            = self._entries['function']

        if self.fitting_problem.multifit:
            self.fitting_problem.additional_info['mantid_ties'] \
                = self._parse_ties()

    def _parse_ties(self) -> list:
        """
        Returns the ties used for a mantid fit function.
        """
        try:
            ties = []
            for t in self._entries['ties'].split(','):
                # Strip out these chars
                for s in '[] "\'':
                    t = t.replace(s, '')
                ties.append(t)

        except KeyError:
            ties = []
        return ties
