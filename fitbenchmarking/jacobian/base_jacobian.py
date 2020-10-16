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

    def __init__(self, cost_func):
        """
        Base class for the Jacobians

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        self.cost_func = cost_func
        self.problem = self.cost_func.problem

        self._method = None

    @abstractmethod
    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of the model

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Computed Jacobian
        :rtype: numpy array
        """
        return NotImplementedError

    @abstractmethod
    def eval_cost(self, params, **kwargs):
        """
        Evaluates Jacobian of the cost function

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Computed derivative of the cost function
        :rtype: numpy array
        """
        return NotImplementedError

    def cached_func_values(self, cached_dict, eval_model, params, **kwargs):
        """
        Computes function values using cached or function evaluation

        :param cached_dict: Cached function values
        :type cached_dict: dict
        :param eval_modelunc: Function to find the Jacobian for
        :type eval_modelunc: Callable
        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Function evaluation
        :rtype: numpy array
        """
        if array_equal(params, cached_dict['params']):
            value = cached_dict['value']
        else:
            value = eval_model(params, **kwargs)
        return value

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
        Utility function to get the numerical method

        :param value: the name of the numerical method
        :type value: str
        """
        self._method = value
