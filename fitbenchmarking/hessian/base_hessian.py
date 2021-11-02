"""
Implements the base class for the Hessian.
"""
from abc import ABCMeta, abstractmethod


class Hessian:
    """
    Base class for Hessian.
    """
    __metaclass__ = ABCMeta

    # Problem formats that are incompatible with certain Hessians
    INCOMPATIBLE_PROBLEMS = {}

    def __init__(self, problem):
        """
        Base class for the Hessians

        :param problem: The parsed problem.
        :type problem:
        :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
        """
        self.problem = problem

        self._method = None

    @abstractmethod
    def eval(self, params, **kwargs):
        """
        Evaluates Hessian of the model

        :param params: The parameter values to find the Hessian at
        :type params: list

        :return: Computed Hessian
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
