"""
Implements the base class for the cost function class.
"""

from abc import ABCMeta, abstractmethod
from fitbenchmarking.utils.exceptions import IncompatibleMinimizerError


class CostFunc:
    """
    Base class for the cost functions.
    """

    __metaclass__ = ABCMeta

    def __init__(self, problem):
        """
        Initialise anything that is needed specifically for the new cost
        function.

        :param problem: The parsed problem
        :type problem:
                :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
        """
        # Problem: The problem object from parsing
        self.problem = problem

        # The Jacobian object to evaluate
        self.jacobian = None

        # The Hessian object to evaluate
        self.hessian = None

        # Used to check whether the algorithm type of the
        # selected minimizer is incompatible with the cost function
        self.invalid_algorithm_types = ['ls']

    @abstractmethod
    def eval_cost(self, params, **kwargs):
        """
        Evaluate the cost function

        :param params: The parameters to calculate residuals for
        :type params: list

        :return: evaluated cost function
        :rtype: float
        """
        raise NotImplementedError

    @abstractmethod
    def jac_res(self, params, **kwargs):
        """
        Uses the Jacobian of the model to evaluate the Jacobian of the
        cost function residual, :math:`\\nabla_p r(x,y,p)`, at the
        given parameters.

        :param params: The parameters at which to calculate Jacobians
        :type params: list

        :return: evaluated Jacobian of the residual at each x, y pair
        :rtype: a list of 1D numpy arrays
        """
        raise NotImplementedError

    @abstractmethod
    def jac_cost(self, params, **kwargs):
        """
        Uses the Jacobian of the model to evaluate the Jacobian of the
        cost function, :math:`\\nabla_p F(r(x,y,p))`, at the given
        parameters.

        :param params: The parameters at which to calculate Jacobians
        :type params: list

        :return: evaluated Jacobian of the cost function
        :rtype: 1D numpy array
        """
        raise NotImplementedError

    @abstractmethod
    def hes_res(self, params, **kwargs):
        """
        Uses the Hessian of the model to evaluate the Hessian of the
        cost function residual, :math:`\\nabla_p^2 r(x,y,p)`, at the
        given parameters.

        :param params: The parameters at which to calculate Hessians
        :type params: list

        :return: evaluated Hessian and Jacobian of the residual at
        each x, y pair
        :rtype: tuple(list of 2D numpy arrays, list of 1D numpy arrays)
        """
        raise NotImplementedError

    @abstractmethod
    def hes_cost(self, params, **kwargs):
        """
        Uses the Hessian of the model to evaluate the Hessian of the
        cost function, :math:`\\nabla_p^2 F(r(x,y,p))`, at the given
        parameters.

        :param params: The parameters at which to calculate Hessians
        :type params: list

        :return: evaluated Hessian of the cost function
        :rtype: 2D numpy array
        """
        raise NotImplementedError

    def validate_algorithm_type(self, algorithm_check, minimizer):
        """
        Helper function which checks that the algorithm type of the
        selected minimizer from the options (options.minimizer)
        is incompatible with the selected cost function

        :param algorithm_check: dictionary object containing algorithm
        types and minimizers for selected software
        :type algorithm_check: dict
        :param minimizer: string of minimizers selected from the options
        :type minimizer: str
        """

        for k, v in algorithm_check.items():
            if minimizer in v and k in self.invalid_algorithm_types:
                message = 'The algorithm type of the selected ' \
                          'minimizer, {}, is not compatible with ' \
                          'the selected cost function'.format(minimizer)
                raise IncompatibleMinimizerError(message)
