"""
Implements the base class for the Jacobian.
"""
from abc import ABCMeta, abstractmethod


class Jacobian:
    """
    Base class for Jacobian.
    """
    __metaclass__ = ABCMeta

    # Problem formats that are incompatible with certain Jacobians
    INCOMPATIBLE_PROBLEMS = {}

    def __init__(self, problem):
        """
        Base class for the Jacobians

        :param problem: The parsed problem.
        :type problem:
        :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
        """
        self.problem = problem

        self.use_default_jac = False
        self._method = None

    @abstractmethod
    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of the model, :math:`\\nabla_p f(x,p)`,
        at the point given by the parameters.

        :param params: The parameter values at which to evaluate the Jacobian
        :type params: list

        :return: Computed Jacobian
        :rtype: numpy array
        """
        raise NotImplementedError

    @property
    def method(self):
        """
        Utility function to get the numerical method

        :return: the names of the parameters
        :rtype: list of str
        """
        return self._method

    @method.setter
    def method(self, value):
        """
        Utility function to set the numerical method

        :param value: the name of the numerical method
        :type value: str
        """
        self._method = value

    def name(self) -> str:
        """
        Get a name for the current status of the jacobian.

        :return: A unique name for this jacobian/method combination
        :rtype: str
        """
        return f'{self.__class__.__name__.lower()} {self.method}'
