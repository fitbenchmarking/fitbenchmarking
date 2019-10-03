from __future__ import (absolute_import, division, print_function)
from abc import ABCMeta, abstractmethod


class BaseFittingProblem(object):
    """
    Definition of a base class implementation of the fitting test problem,
    normally loaded from a problem definition file.

    Types of data:
        - strings: name, type, equation
        - floats: start_x, end_x, ref_residual_sum_sq
        - numpy arrays: data_x, data_y, data_e
        - arrays: starting_values
    """
    __metaclass__ = ABCMeta

    def __init__(self, fname):

        # Initializes base class with filename
        self._fname = fname

        # Name (title) of the fitting problem
        self._name = None
        # Equation (function or model) to fit against data
        self._equation = None
        # Define range to fit model data over if different from entire range of data
        self._start_x = None
        self._end_x = None

        # Starting values of the fitting parameters
        self._starting_values = None
        # The data
        self._data_x = None
        self._data_y = None
        self._data_e = None

        # Initialize contents of file. Here included to reduce I/O, i.e.
        # read file content once and then process as needed
        self._contents = None
        self._starting_value_ranges = None

    def read_file(self):
        self._contents = open(self._fname, "r")

    def close_file(self):
        self._contents.close()

    def eval_f(self, x, params, function_id):
        """
        Function evaluation method

        :param x: x data values
        :param params: parameter value(s)
        :param function_id: The index of the function in get_function

        :return: y data values evaluated from the function of the problem
        """

        func_def = self.get_function()
        function = func_def[function_id][0]
        return function(x, *params)

    def eval_starting_params(self, function_id):
        """
        Evaluate the function using the starting parameters.

        @returns :: A numpy array of results from evaluation
        """

        function_params = self.get_function()[function_id][1]
        return self.eval_f(x=self.data_x,
                           params=function_params,
                           function_id=function_id)

    @abstractmethod
    def get_function(self):
        """
        Return the function definitions.

        @returns :: list of callable-parameter pairs
        """
        pass

    def get_function_def(self, params, function_id):
        """
        Return the function definition in a string format for output

        @param params :: The list of parameters to use in the function string
        @param function_id :: The index of the function in get_function

        @returns :: A string with a representation of the function
                    example format: 'b1 * (b2+x) | b1=-2.0, b2=50.0'
        """
        names = [s[0] for s in self._starting_values]
        if params is None:
            params = (None for _ in names)
        params = ['{}={}'.format(n, p) for n, p in zip(names, params)]
        param_string = ', '.join(params)

        func_name = self._equation  # self.get_function()[function_id][2]
        return '{} | {}'.format(func_name, param_string)

    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self, value):
        self._fname = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def equation(self):
        return self._equation

    @equation.setter
    def equation(self, value):
        self._equation = value

    @property
    def start_x(self):
        return self._start_x

    @start_x.setter
    def start_x(self, value):
        self._start_x = value

    @property
    def end_x(self):
        return self._end_x

    @end_x.setter
    def end_x(self, value):
        self._end_x = value

    @property
    def starting_values(self):
        return self._starting_values

    @starting_values.setter
    def starting_values(self, value):
        self._starting_values = value

    @property
    def data_x(self):
        return self._data_x

    @data_x.setter
    def data_x(self, value):
        self._data_x = value

    @property
    def data_y(self):
        return self._data_y

    @data_y.setter
    def data_y(self, value):
        self._data_y = value

    @property
    def data_e(self):
        return self._data_e

    @data_e.setter
    def data_e(self, value):
        self._data_e = value

    @property
    def contents(self):
        return self._contents

    @contents.setter
    def contents(self, value):
        self._contents = value

    @property
    def starting_value_ranges(self):
        return self._starting_value_ranges

    @starting_value_ranges.setter
    def starting_value_ranges(self, value):
        self._starting_value_ranges = value

    def __new__(cls, *args, **kwargs):
        if cls is BaseFittingProblem:
            raise TypeError("Base class {} may not be instantiated".format(cls))
        return object.__new__(cls, *args, **kwargs)
