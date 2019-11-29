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
    """
    Definition of a fitting problem, normally populated by a parser from a
    problem definition file.

    Types of data:
        - strings: name, equation
        - floats: start_x, end_x
        - numpy arrays: data_x, data_y, data_e
        - arrays: starting_values, value_ranges, functions
    """

    def __init__(self):

        # Name (title) of the fitting problem
        # str
        self.name = None

        # Equation (function or model) to fit against data
        # string
        self.equation = None

        # Define range to fit model data over if different from entire range
        # of data
        # floats
        self.start_x = None
        self.end_x = None

        # The data
        # numpy array of floats
        self.data_x = None
        self.data_y = None
        self.data_e = None

        # Starting values of the fitting parameters
        # list of dict -> [{p1_name: p1_val1, p2_name: p2_val1, ...},
        #                  {p1_name: p1_val2, ...},
        #                  ...]
        self.starting_values = None
        # dict -> {p1_name: [p1_min, p1_max], ...}
        self.value_ranges = None

        # Callable function
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

        if x is None and y is None:
            x = self.data_x
            y = self.data_y
            if e is None:
                e = self.data_e
            else:
                raise ValueError('Residuals cannot be computed with errors'
                                 'and with given arguments. Please specify'
                                 'x and y.')
        elif x is None or y is None:
            raise ValueError('Residuals could not be computed with only one'
                             'of x and y')

        result = y - self.eval_f(params=params, x=x)
        if e is not None:
            result = result / e
        return result

    def eval_j(self, params, func=None, **kwargs):
        """
        Approximate the jacobian using scipy for a given function at a given
        point.

        :param params: The parameter values to find the jacobian at
        :type params: list
        :param func: Function to find the jacobian for, defaults to self.eval_r
        :type func: Callable, optional
        :return: Approximation of the jacobian
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
