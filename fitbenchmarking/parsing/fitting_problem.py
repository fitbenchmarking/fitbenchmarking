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


class FittingProblem:
    """
    Definition of a fitting problem, normally populated by a parser from a
    problem definition file.

    Types of data:
        - strings: name, type, equation
        - floats: start_x, end_x, ref_residual_sum_sq
        - numpy arrays: data_x, data_y, data_e
        - arrays: starting_values
    """

    def __init__(self):

        # Name (title) of the fitting problem
        self.name = None

        # Equation (function or model) to fit against data
        self.equation = None

        # Define range to fit model data over if different from entire range
        # of data
        self.start_x = None
        self.end_x = None

        # The data
        self.data_x = None
        self.data_y = None
        self.data_e = None

        # Starting values of the fitting parameters
        self.starting_values = None
        self.value_ranges = None

        # Executable param pairs
        self.functions = None

    def eval_f(self, x, params, function_id):
        """
        Function evaluation method

        :param x: x data values
        :type x: numpy array
        :param params: parameter value(s)
        :type params: list
        :param function_id: The index of the function in get_function
        :type function_id: int

        :return: y data values evaluated from the function of the problem
        :rtype: numpy array
        """
        if self.functions is None:
            raise AttributeError('Cannot call function before setting'
                                 + 'functions in object.')
        function = self.functions[function_id][0]
        return function(x, *params)

    def eval_starting_params(self, function_id):
        """
        Evaluate the function using the starting parameters.

        :param function_id: The index of the function in get_function
        :type function_id: int

        :return: Results from evaluation
        :rtype: numpy array
        """
        if self.functions is None:
            raise AttributeError('Cannot call function before setting'
                                 + 'functions in object.')
        function_params = self.functions[function_id][1]
        return self.eval_f(x=self.data_x,
                           params=function_params,
                           function_id=function_id)

    def get_function_def(self, params, function_id):
        """
        Return the function definition in a string format for output

        :param params: The parameters to use in the function string
        :type params: list
        :param function_id: The index of the function in get_function
        :type function_id: int

        :return: Representation of the function
                 example format: 'b1 * (b2+x) | b1=-2.0, b2=50.0'
        :rtype: string
        """
        params = ['{}={}'.format(s[0], p) for s, p
                  in izip_longest(self.starting_values,
                                  params if params is not None else [])]
        param_string = ', '.join(params)

        func_name = self.equation
        return '{} | {}'.format(func_name, param_string)
