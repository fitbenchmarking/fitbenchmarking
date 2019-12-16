"""
Implements the base class for the fitting software controllers.
"""

from abc import ABCMeta, abstractmethod

import numpy as np


class Controller:
    """
    Base class for all fitting software controllers.
    These controllers are intended to be the only interface into the fitting
    software, and should do so by implementing the abstract classes defined
    here.
    """

    __metaclass__ = ABCMeta

    def __init__(self, problem, use_errors):
        """
        Initialise the class.
        Sets up data as defined by the problem and use_errors variables,
        and initialises variables that will be used in other methods.

        :param problem: The parsed problem
        :type problem: fitting_problem (see fitbenchmarking.parsers)
        :param use_errors: Flag to enable errors in the fitting
        :type use_errors: Bool
        """

        # Problem: The problem object from parsing
        self.problem = problem
        # Use Errors: Bool to use errors or not
        self.use_errors = use_errors

        # Data: Data used in fitting. Might be different from problem
        #       if corrections are needed (e.g. startX)
        self.data_x = problem.data_x
        self.data_y = problem.data_y
        self.data_e = problem.data_e
        self._correct_data()

        # Initial Params: The starting values for params when fitting
        self.initial_params = None
        # Staring Valuess: The list of starting parameters
        self.starting_values = problem.starting_values
        # Parameter set: The index of the starting parameters to use
        self.parameter_set = None
        # Minimizer: The current minimizer to use
        self.minimizer = None

        # Final Params: The final values for the params from the minimizer
        self.final_params = None
        # Results: Stores output results using the final parameters in
        #          numpy array
        self.results = None
        # Success: Bool for flagging issues
        self.success = None

    def _correct_data(self):
        """
        Strip data that overruns the start and end x_range,
        and approximate errors if not given.
        Modifications happen on member variables.
        """

        # fix self.data_e
        if self.use_errors:
            if self.data_e is None:
                self.data_e = np.sqrt(abs(self.data_y))

            self.data_e[self.data_e == 0] = \
                np.min(self.data_e[self.data_e != 0]) * 1e-8
        else:
            self.data_e = None

        # impose x ranges
        start_x = self.problem.start_x
        end_x = self.problem.end_x

        if start_x is not None and end_x is not None:
            mask = np.logical_and(self.data_x >= start_x, self.data_x <= end_x)
            self.data_x = self.data_x[mask]
            self.data_y = self.data_y[mask]
            if self.data_e is not None:
                self.data_e = self.data_e[mask]

        # Stores the indices of the sorted data
        self.sorted_index = np.argsort(self.data_x)

    def prepare(self):
        """
        Check that function and minimizer have been set.
        If both have been set, run self.setup().
        """

        if (self.minimizer is not None) and (self.parameter_set is not None):
            self.initial_params = \
                list(self.starting_values[self.parameter_set].values())
            self.setup()
        else:
            raise RuntimeError('Either minimizer or parameter_set is set to'
                               'None.')

    @abstractmethod
    def setup(self):
        """
        Setup the specifics of the fitting

        Anything needed for "fit" should be saved to self.
        """
        raise NotImplementedError

    @abstractmethod
    def fit(self):
        """
        Run the fitting.
        """
        raise NotImplementedError

    @abstractmethod
    def cleanup(self):
        """
        Retrieve the result as a numpy array and store in self.results
        """
        raise NotImplementedError
