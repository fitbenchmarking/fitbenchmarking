
from abc import ABCMeta, abstractmethod

import numpy as np


class BaseSoftwareController():
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
        """

        # Problem: The problem object from parsing
        self.problem = problem
        # Use Errors: Bool to use errors or not
        self.use_errors = use_errors

        # Functions: The functions to fit
        self.functions = problem.get_function()

        # Data: Data used in fitting. Might be different from problem
        #       if corrections are needed (e.g. startX)
        self.data_x = problem.data_x
        self.data_y = problem.data_y
        self.data_e = problem.data_e
        self._correct_data()

        # Initial Params: The starting values for params when fitting
        self.initial_params = None
        # Function: The current function to fit (from functions)
        self.function = None
        self.function_id = None
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
        xdata = self.data_x
        ydata = self.data_y
        sigma = self.data_e

        # fix sigma
        if self.use_errors:
            if sigma is None:
                sigma = np.sqrt(abs(ydata))

            sigma[sigma == 0] = 1e-8
        else:
            sigma = None

        # impose x ranges
        start_x = self.problem.start_x
        end_x = self.problem.end_x

        if start_x is not None and end_x is not None:
            mask = np.logical_and(xdata >= start_x, xdata <= end_x)
            xdata = xdata[mask]
            ydata = ydata[mask]
            if sigma is not None:
                sigma = sigma[mask]

        # store
        self.data_x = xdata
        self.data_y = ydata
        self.data_e = sigma

    def prepare(self, minimizer=None, function_id=None):
        """
        Set the minimizer, function_id, or both.
        If both have been set, run self.setup().

        :param minimizer: The name of the minimizer to use
        :type minimizer: String
        :param function_id: The index of the function to fit
        :type function_id: Int
        """
        if minimizer is not None:
            self.minimizer = minimizer
        if function_id is not None:
            func = self.functions[function_id]
            self.function_id = function_id
            self.function = func[0]
            self.initial_params = func[1]

        if (self.minimizer is not None) and (self.function_id is not None):
            self.setup()

    @abstractmethod
    def setup(self):
        """
        ABSTRACT METHOD
        Setup the specifics of the fitting

        Anything needed for "fit" should be saved to self.

        :returns: None
        :rtype: None
        """
        pass

    @abstractmethod
    def fit(self):
        """
        ABSTRACT METHOD
        Run the fitting.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        ABSTRACT METHOD
        Retrieve the result as a numpy array and store in self.results
        """
        pass
