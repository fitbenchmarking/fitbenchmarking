"""
This file implements a parser for the Mantid data format.
This version is for developers. Unlike the mantid_parser
this version removes the advantage for function evaluations
by forcing mantid to use the same one as other software. 
However, Mantid still has an advantage for Jacobian 
evaluations - using the same problem in both mantid and
nist formats gives mantiddev different rankings in terms of
speed. 
"""
import typing

import mantid.simpleapi as msapi
from mantid.api import FunctionDomain1DVector as FDV
from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser
import numpy as np

class MantidDevParser(FitbenchmarkParser):
    """
    Parser for a Mantid problem definition file.
    """
    def _set_additional_info(self) -> None:
        """
        Sets any additional info for a fitting problem.
        """
        #self.fitting_problem.additional_info['mantid_equation'] \
        #    = self._entries['function']

        if self.fitting_problem.multifit:
            self.fitting_problem.additional_info['mantid_ties'] \
                = self._parse_ties()

    def parse(self):

        fp = super().parse()

        self._set_jacobian(fp)
        return fp

    def _set_jacobian(self, fp) -> None:
        """
        Sometimes mantid will give the error 
        RuntimeError: Integration is not implemented for this function.
        this try except tests if the error occurs and then only 
        assigns the jacobian if it passes.
        :param fp: fitting problem
        """
        # need to trim x data to the correct range for Jacobian
        i0 = 0
        iN = len(fp.data_x)
        if fp.start_x:
            i0 = np.argmax(fp.data_x >= fp.start_x)
        if fp.end_x:
            # returns a list of lists if more than one match, otherwise an int is returned
            iN = np.where(fp.data_x <= fp.end_x)
            if not isinstance(iN, int):
                iN = iN[0][-1]

        x_data = fp.data_x
        x_data = x_data[i0:iN + 1]
        
        # cache the x values for later
        self._cache_x = FDV(x_data)
        self._N_x = len(x_data)
        self._jac = np.zeros((self._N_x, len(self._params_dict.keys())))

        try:
            _ = self._jacobian(x_data, self._params_dict.values())
            fp.jacobian = self._jacobian
        except RuntimeError:

            return

    def _jacobian(self, x, *args):
        """
        Extracts the Jacobian from Mantid 
        WARNING: Gaussians are known to be incorrect

        :param x: the x values for the problem (assume they have not changed)
        :param args: the input parameters for the fit
        :return a matrix of the Jacobian
        """
        for param, key in zip(*args, self._params_dict.keys()):
            self._mantid_function[key] = param
        # get mantid Jacobian
        J = self._mantid_function.functionDeriv(self._cache_x)
        # set np Jacobian values
        for i in range(self._N_x):
            for j in range(len(self._params_dict.keys())):
                self._jac[i, j] = J.get(i, j)
        return self._jac
        

    def _update_params(self, *p):
        update_dict = dict(zip(self._params_dict.keys(), p))
        self._params_dict.update(update_dict)
        return self._params_dict
        
    def _create_function(self) -> typing.Callable:
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
        self._equation = ifun.name()
        self._starting_values = [params]
        # pylint: enable=attribute-defined-outside-init

        # Convert to callable
        fit_function = msapi.FunctionWrapper(ifun)
        # need these for jacobian
        self._mantid_function = fit_function
        self._params_dict = params
        ## Use a wrapper to inject fixed parameters into the function
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

        :return: True if the problem is a multi fit problem.
        :rtype: bool
        """
        return self._entries['input_file'][0] == '['

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        return self._starting_values

    def _set_data_points(self, data_points: list, fit_ranges: list) -> None:
        """
        Sets the data points and fit range data in the fitting problem.

        :param data_points: A list of data points.
        :type data_points: list
        :param fit_ranges: A list of fit ranges.
        :type fit_ranges: list
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

    def _parse_ties(self) -> list:
        """
        Returns the ties used for a mantid fit function.

        :return: A list of ties used for a mantid fit function.
        :rtype: list
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

    def _parse_function(self, *args, **kwargs):
        """
        Override the default function parsing as this is offloaded to mantid.
        """
        return []

    def _get_equation(self, *args, **kwargs):
        """
        Override the default function parsing as this is offloaded to mantid.
        """
        return self._equation