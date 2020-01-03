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

    @property
    def param_names(self):
        """
        Utility function to get the parameter names

        :return: the neames of the parameters
        :rtype: [type]
        """
        if self._param_names is None:
            self._param_names = list(self.starting_values[0].keys())
        return self._param_names

    @param_names.setter
    def param_names(self, value):
        raise ValueError('This property should not be set manually')

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
            raise AttributeError('Cannot call function before setting'
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
            raise ValueError('Residuals could not be computed with only one'
                             'of x and y')

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
        if x is None and y is None and e is None:
            x = self.data_x
            y = self.data_y
            e = self.data_e

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
            raise AttributeError('Cannot call function before setting'
                                 'starting values.')
        return self.eval_f(self.starting_values[param_set].values())

    def get_function_def(self, params):
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

        func_name = self.equation
        return '{} | {}'.format(func_name, param_string)

    def verify(self):
        """
        Basic check that minimal set of attributes have been set.

        Raise AttributeError if object is not properly initialised.
        """

        values = {'data_x': np.ndarray,
                  'data_y': np.ndarray,
                  'starting_values': list}

        for attr_name, attr_type in values.items():
            attr = getattr(self, attr_name)
            if not isinstance(attr, attr_type):
                raise TypeError('Attribute "{}" is not the expected type.'
                                'Expected "{}", got {}.'.format(attr_name,
                                                                attr_type,
                                                                type(attr)
                                                                ))
        if self.function is None:
            raise TypeError('Attribute "function" has not been set.')
