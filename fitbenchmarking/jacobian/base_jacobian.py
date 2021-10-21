"""
Implements the base class for the Jacobian.
"""
from abc import ABCMeta, abstractmethod
from numpy import array_equal


class Jacobian:
    """
    Base class for Jacobian.
    """
    __metaclass__ = ABCMeta

    # Problem formats that are incompatible with certain Jacobians
    INCOMPATIBLE_PROBLEMS = {}

    def __init__(self, cost_func):
        """
        Base class for the Jacobians

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        self.cost_func = cost_func
        self.problem = self.cost_func.problem

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
