"""
Implements the base class for the Hessian.
"""
from abc import ABCMeta, abstractmethod


class Hessian:
    """
    Base class for Hessian.
    """
    __metaclass__ = ABCMeta

    def __init__(self, problem):
        """
        Base class for the Hessians

        :param problem: The parsed problem.
        :type problem:
        :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
        :param jacobian: Jaocbian object
        :type jacobian:
        fitbenchmarking.jacobian.<jac_method>_jacobian.<jac_method>
        """
        self.problem = problem

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
