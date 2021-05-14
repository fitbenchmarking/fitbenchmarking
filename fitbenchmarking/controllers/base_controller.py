"""
Implements the base class for the fitting software controllers.
"""

from abc import ABCMeta, abstractmethod
import numpy

from fitbenchmarking.utils.exceptions import ControllerAttributeError, \
    UnknownMinimizerError, IncompatibleMinimizerError


class Controller:
    """
    Base class for all fitting software controllers.
    These controllers are intended to be the only interface into the fitting
    software, and should do so by implementing the abstract classes defined
    here.
    """

    __metaclass__ = ABCMeta

    VALID_FLAGS = [0, 1, 2, 3, 4, 5]

    def __init__(self, cost_func):
        """
        Initialise anything that is needed specifically for the
        software, do any work that can be done without knowledge of the
        minimizer to use, or function to fit, and call
        ``super(<software_name>Controller, self).__init__(problem)``
        (the base class's ``__init__`` implementation).
        In this function, you must initialize the a dictionary,
        ``self.algorithm_check``, such that the **keys** are given by:

        - ``all`` - all minimizers
        - ``ls`` - least-squares fitting algorithms
        - ``deriv_free`` - derivative free algorithms (these are algorithms
          that cannot use derivative information. For example, the
          ``Simplex`` method in ``Mantid`` does not require Jacobians, and so
          is derivative free.
        - ``general`` - minimizers which solve a generic `min f(x)`.

        The **values** of the dictionary are given as a list of minimizers
        for that specific controller that fit into each of the above
        categories. See for example the ``GSL`` controller.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        self.cost_func = cost_func
        # Problem: The problem object from parsing
        self.problem = self.cost_func.problem

        # Jacobian: The Jacobian object
        self.jacobian = None

        # Data: Data used in fitting. Might be different from problem
        #       if corrections are needed (e.g. startX)
        self.data_x = self.problem.data_x
        self.data_y = self.problem.data_y
        self.data_e = self.problem.data_e

        # Initial Params: The starting values for params when fitting
        self.initial_params = None
        # Staring Valuess: The list of starting parameters
        self.starting_values = self.problem.starting_values
        # Parameter Bounds: List of tuples of lower and upper bounds
        # for each parameter
        self.value_ranges = self.problem.value_ranges
        # Parameter set: The index of the starting parameters to use
        self.parameter_set = None
        # Minimizer: The current minimizer to use
        self.minimizer = None

        # Final Params: The final values for the params from the minimizer
        self.final_params = None

        # Flag: error handling flag
        self._flag = None

        # Algorithm check: this is used to check whether the selected
        # minimizer/minimizers from the options is within the softwares
        # algorithms. It also used to filter out algorithms based on the keys
        # of the dictionary
        self.algorithm_check = {'all': [None],
                                'ls': [None],
                                'deriv_free': [None],
                                'general': [None]}

        # Used to check whether the selected minimizers is compatible with
        # problems that have parameter bounds
        self.no_bounds_minimizers = []

        # Used to check whether the fitting software has support for
        # bounded problems, set as True if at least some minimizers
        # in the fitting software have support for bounds
        self.support_for_bounds = False

    @property
    def flag(self):
        """
        | 0: `Successfully converged`
        | 1: `Software reported maximum number of iterations exceeded`
        | 2: `Software run but didn't converge to solution`
        | 3: `Software raised an exception`
        | 4: `Solver doesn't support bounded problems`
        | 5: `Solution doesn't respect parameter bounds`
        """

        return self._flag

    @flag.setter
    def flag(self, value):

        if value not in self.VALID_FLAGS:
            raise ControllerAttributeError(
                'controller.flag must be one of {}. Got: {}.'.format(
                    list(self.VALID_FLAGS), value))
        self._flag = int(value)

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
            raise ControllerAttributeError('Either minimizer or parameter_set '
                                           'is set to None.')

    def eval_chisq(self, params, x=None, y=None, e=None):
        """
        Computes the chisq value

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
        out = self.cost_func.eval_cost(params=params, x=x, y=y, e=e)
        return out

    def validate_minimizer(self, minimizer, algorithm_type):
        """
        Helper function which checks that the selected minimizer from the
        options (options.minimizer) exists and whether the minimizer is in
        self.algorithm_check[options.algorithm_type] (this is a list set in
        the controller)

        :param minimizer: string of minimizers selected from the
                          options
        :type minimizer: str
        :param algorithm_type: the algorithm type selected from the options
        :type algorithm_type: str
        """
        minimzer_selection = self.algorithm_check[algorithm_type]
        result = minimizer in minimzer_selection

        if not result:
            message = 'The minimizer selected, {0}, is not within ' \
                'algorithm_check[options.algorithm_type] = {1}\n'.format(
                    minimizer, minimzer_selection)
            raise UnknownMinimizerError(message)

    def check_minimizer_bounds(self, minimizer):
        """
        Helper function which checks whether the selected minimizer from the
        options (options.minimizer) supports problems with parameter bounds

        :param minimizer: string of minimizers selected from the
                          options
        :type minimizer: str
        """

        if self.support_for_bounds is False or \
                minimizer in self.no_bounds_minimizers:
            message = 'The selected minimizer does not currently support ' \
                      'problems with parameter bounds'
            raise IncompatibleMinimizerError(message)

    def check_bounds_respected(self):
        """
            Check whether the selected minimizer has respected
            parameter bounds
        """
        for count, value in enumerate(self.final_params):
            if not self.value_ranges[count][0] <= value \
                    <= self.value_ranges[count][1]:
                self.flag = 5

    def check_attributes(self):
        """
        A helper function which checks all required attributes are set
        in software controllers
        """
        values = {'_flag': int, 'final_params': numpy.ndarray}

        for attr_name, attr_type in values.items():
            attr = getattr(self, attr_name)
            if attr_type != numpy.ndarray:
                if not isinstance(attr, attr_type):
                    raise ControllerAttributeError(
                        'Attribute "{}" in the controller is not the expected '
                        'type. Expected "{}", got {}.'.format(
                            attr_name, attr_type, type(attr)))
            else:
                # Mantid multifit produces final params as a list of final
                # params.
                if not self.problem.multifit:
                    attr = [attr]
                for a in attr:
                    if any(numpy.isnan(n) or numpy.isinf(n) for n in a):
                        raise ControllerAttributeError(
                            'Attribute "{}" in the controller is not the '
                            'expected numpy ndarray of floats. Expected a '
                            'list or numpy ndarray of floats, got '
                            '{}'.format(attr_name, attr))

    @abstractmethod
    def jacobian_information(self):
        """
        Sets up Jacobian information for the controller.

        This should return the following arguments:

        - ``has_jacobian``: a True or False value whether the controller
          requires Jacobian information.
        - ``jacobian_free_solvers``: a list of minimizers in a specific
          software that do not allow Jacobian information to be passed
          into the fitting algorithm. For example in the ``Scipy``
          controller this would return ``Nelder-Mead`` and ``Powell``.

        :return: (``has_jacobian``, ``jacobian_free_solvers``)
        :rtype: (`string`, `list`)
        """
        raise NotImplementedError

    @abstractmethod
    def setup(self):
        """
        Setup the specifics of the fitting.

        Anything needed for "fit" that can only be done after knowing the
        minimizer to use and the function to fit should be done here.
        Any variables needed should be saved to self (as class attributes).

        If a solver supports bounded problems, then this is where
        `value_ranges` should be set up for that specific solver. The default
        format is a list of tuples containing the lower and upper bounds
        for each parameter e.g. [(p1_lb, p2_ub), (p2_lb, p2_ub),...]
        """
        raise NotImplementedError

    @abstractmethod
    def fit(self):
        """
        Run the fitting.

        This will be timed so should include only what is needed
        to fit the data.
        """
        raise NotImplementedError

    @abstractmethod
    def cleanup(self):
        """
        Retrieve the result as a numpy array and store results.

        Convert the fitted parameters into a numpy array, saved to
        ``self.final_params``, and store the error flag as ``self.flag``.

        The flag corresponds to the following messages:

        .. automethod:: fitbenchmarking.controllers.base_controller.Controller.flag()  # noqa: E501
                :noindex:
        """
        raise NotImplementedError
