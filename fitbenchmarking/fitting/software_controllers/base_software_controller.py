
from abc import ABCMeta, abstractmethod


class BaseSoftwareController():

    __metaclass__ = ABCMeta

    def __init__(self, problem, use_errors):
        """
        Initialise the class.
        """

        # Problem: The problem object from parsing
        self.problem = problem
        # Use Errors: Bool to use errors or not
        self.use_errors = use_errors

        # Functions: The functions to fit
        self.functions = problem.get_function()

        # Data: Data used in fitting. Might be different from problem
        #       if corrections are needed (e.g. startX)
        self.data_x = None
        self.data_y = None
        self.data_e = None

        # Initial Params: The starting values for params when fitting
        self.initial_params = None
        # Function: The current function to fit (from functions)
        self.function = None
        # Minimizer: The current minimizer to use
        self.minimizer = None

        # Final Params: The final values for the params from the minimizer
        self.final_params = None
        # Results: Stores output results using the final parameters in 
        #          numpy array
        self.results = None
        # Success: Bool for flagging issues
        self.success = None

    def prepare(self, minimizer=None, function_id=None):
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
        Setup the specifics of the fitting

        Anything needed for "fit" should be saved to self.

        :returns: None
        :rtype: None
        """
        pass

    @abstractmethod
    def fit(self):
        """
        Run the fitting.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Retrieve the result as a numpy array and store in self.results
        """
        pass
