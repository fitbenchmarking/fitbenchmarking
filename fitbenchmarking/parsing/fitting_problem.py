"""
Implements the FittingProblem class, this will be the object that inputs are
parsed into before being passed to the controllers
"""

from __future__ import (absolute_import, division, print_function)

try:
    from itertools import izip_longest
except ImportError:
    # python3
    from itertools import zip_longest as izip_longest
import numpy as np
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.utils.exceptions import FittingProblemError


class FittingProblem:
    r"""
    Definition of a fitting problem, which will be populated by a parser from a
    problem definition file.

    This defines a fitting problem where, given a set of :math:`n` data points
    :math:`(x_i,y_i)`, associated errors :math:`e_i`, and a model
    function :math:`f(x,p)`, we find the optimal parameters in the
    least-squares sense by solving:

    .. math:: \min_p \sum_{i=1}^n \left( \frac{y_i - f(x_i, p)}{e_i} \right)^2

    where :math:`p` is a vector of length :math:`m`, and we start from a given
    intial guess for the optimal parameters.
    """

    def __init__(self):

        #: *string* Name (title) of the fitting problem
        self.name = None

        #: *string* Equation (function or model) to fit against data
        self.equation = None

        #: *float* The start of the range to fit model data over
        #: (if different from entire range)
        self.start_x = None

        #: *float* The end of the range to fit model data over
        #: (if different from entire range) (/float/)
        self.end_x = None

        #: *numpy array* The x-data
        self.data_x = None

        #: *numpy array* The y-data
        self.data_y = None

        #: *numpy array* The errors
        self.data_e = None

        #: *list of dict*
        #: Starting values of the fitting parameters
        #:
        #: e.g.
        #: :code:`[{p1_name: p1_val1, p2_name: p2_val1, ...},
        #: {p1_name: p1_val2, ...}, ...]`
        self.starting_values = None

        #: *dict*
        #: Smallest and largest values of interest in the data
        #:
        #: e.g.
        #: :code:`{p1_name: [p1_min, p1_max], ...}`
        self.value_ranges = None

        #: Callable function
        self.function = None

        self._param_names = None

        # the sanitised name strips out commas and white spaces which is used
        # to define the plot and html links
        self._sanitised_name = None

        # The index for sorting the data (used in plotting)
        self.sorted_index = None

    @property
    def param_names(self):
        """
        Utility function to get the parameter names

        :return: the names of the parameters
        :rtype: list of str
        """
        if self._param_names is None:
            self._param_names = list(self.starting_values[0].keys())
        return self._param_names

    @param_names.setter
    def param_names(self, value):
        raise FittingProblemError('param_names should not be edited')

    @property
    def sanitised_name(self):
        """
        Sanitise the problem name ito one which can be used as a filename.
        
        :return: sanitised name
        :rtype: str
        """
        if not self._sanitised_name:
            self._sanitised_name = self.name
            self._sanitised_name = self._sanitised_name.replace(',', '')
            self._sanitised_name = self._sanitised_name.replace(' ', '_')
        return self._sanitised_name

    @sanitised_name.setter
    def sanitised_name(self, value):
        raise FittingProblemError('sanitised_name should not be edited')

    def eval_f(self, params, x=None):
        """
        Function evaluation method

        :param params: parameter value(s)
        :type params: list
        :param x: x data values or None, if None this uses self.data_x
        :type x: numpy array

        :return: y data values evaluated from the function of the problem
        :rtype: numpy array
        """
        if self.function is None:
            raise FittingProblemError('Cannot call function before setting '
                                      'function.')
        if x is None:
            x = self.data_x
        return self.function(x, *params)

    def eval_r(self, params, x=None, y=None, e=None):
        """
        Calculate residuals and weight them if using errors

        :param params: The parameters to calculate residuals for
        :type params: list
        :param x: x data points, defaults to self.data_x
        :type x: numpy array, optional
        :param y: y data points, defaults to self.data_y
        :type y: numpy array, optional
        :param e: error at each data point, defaults to self.data_e
        :type e: numpy array, optional

        :return: The residuals for the datapoints at the given parameters
        :rtype: numpy array
        """

        if x is None and y is None and e is None:
            x = self.data_x
            y = self.data_y
            e = self.data_e
        elif x is None or y is None:
            raise FittingProblemError('Residuals could not be computed with '
                                      'only one of x and y.')

        result = y - self.eval_f(params=params, x=x)
        if e is not None:
            result = result / e
        return result

    def eval_r_norm(self, params, x=None, y=None, e=None):
        """
        Evaluate the square of the L2 norm of the residuals

        :param params: The parameters to calculate residuals for
        :type params: list
        :param x: x data points, defaults to self.data_x
        :type x: numpy array, optional
        :param y: y data points, defaults to self.data_y
        :type y: numpy array, optional
        :param e: error at each data point, defaults to self.data_e
        :type e: numpy array, optional

        :return: The sum of squares of residuals for the datapoints at the
                 given parameters
        :rtype: numpy array
        """
        r = self.eval_r(params=params, x=x, y=y, e=e)
        return np.dot(r, r)

    def eval_j(self, params, func=None, **kwargs):
        """
        Approximate the Jacobian using scipy for a given function at a given
        point.

        :param params: The parameter values to find the Jacobian at
        :type params: list
        :param func: Function to find the Jacobian for, defaults to self.eval_r
        :type func: Callable, optional

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        if func is None:
            func = self.eval_r

        return approx_derivative(func, params, kwargs=kwargs)

    def eval_starting_params(self, param_set):
        """
        Evaluate the function using the starting parameters.

        :param param_set: The index of the parameter set in starting_params
        :type param_set: int

        :return: Results from evaluation
        :rtype: numpy array
        """
        if self.starting_values is None:
            raise FittingProblemError('Cannot call function before setting '
                                      'starting values.')
        return self.eval_f(self.starting_values[param_set].values())

    def get_function_params(self, params):
        """
        Return the function definition in a string format for output

        :param params: The parameters to use in the function string
        :type params: list

        :return: Representation of the function
                 example format: 'b1 * (b2+x) | b1=-2.0, b2=50.0'
        :rtype: string
        """
        params = ['{}={}'.format(n, p) for n, p
                  in izip_longest(self.param_names,
                                  params if params is not None else [])]
        param_string = ', '.join(params)

        return param_string

    def verify(self):
        """
        Basic check that minimal set of attributes have been set.

        Raise FittingProblemError if object is not properly initialised.
        """

        values = {'data_x': np.ndarray,
                  'data_y': np.ndarray,
                  'starting_values': list}

        for attr_name, attr_type in values.items():
            attr = getattr(self, attr_name)
            if not isinstance(attr, attr_type):
                raise FittingProblemError(
                    'Attribute "{}" is not the expected type. Expected "{}", '
                    'got "{}".'.format(attr_name, attr_type, type(attr)))
        if self.function is None:
            raise FittingProblemError('Attribute "function" has not been set.')

    def correct_data(self, use_errors):
        """
        Strip data that overruns the start and end x_range,
        and approximate errors if not given.
        Modifications happen on member variables.

        :param use_errors: Specify whether to set data_e or not
        :type use_errors: bool 
        """

        # fix self.data_e
        if use_errors:
            if self.data_e is None:
                self.data_e = np.sqrt(abs(self.data_y))

            # The values of data_e are used to divide the residuals.
            # If these are (close to zero), then this blows up.
            # This is particularly a problem if trying to fit
            # counts, which may follow a Poisson distribution.
            #
            # Fix this by cutting values less than a certain value
            trim_value = 1.0e-8
            self.data_e[self.data_e < trim_value] = trim_value
        else:
            self.data_e = None

        # impose x ranges
        if self.start_x is not None and self.end_x is not None:
            mask = np.logical_and(self.data_x >= self.start_x,
                                  self.data_x <= self.end_x)
            self.data_x = self.data_x[mask]
            self.data_y = self.data_y[mask]
            if self.data_e is not None:
                self.data_e = self.data_e[mask]

        # Stores the indices of the sorted data
        self.sorted_index = np.argsort(self.data_x)
