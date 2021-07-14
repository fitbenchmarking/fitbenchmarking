"""
Implements the base class for the Hessian.
"""
from abc import ABCMeta, abstractmethod
from numpy import array_equal


class Hessian:
    """
    Base class for Hessian.
    """
    __metaclass__ = ABCMeta

    def __init__(self, cost_func):
        """
        Base class for the Hessians

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        self.cost_func = cost_func
        self.problem = self.cost_func.problem
        self.jacobian = None

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

    @abstractmethod
    def eval_cost(self, params, **kwargs):
        """
        Evaluates Hessian of the cost function

        :param params: The parameter values to find the Hessian at
        :type params: list

        :return: Computed derivative of the cost function
        :rtype: numpy array
        """
        raise NotImplementedError

    def cached_func_values(self, cached_dict, eval_model, params, **kwargs):
        """
        Computes function values using cached or function evaluation

        :param cached_dict: Cached function values
        :type cached_dict: dict
        :param eval_modelunc: Function to find the Hessian for
        :type eval_modelunc: Callable
        :param params: The parameter values to find the Hessian at
        :type params: list

        :return: Function evaluation
        :rtype: numpy array
        """
        if array_equal(params, cached_dict['params']):
            value = cached_dict['value']
        else:
            value = eval_model(params, **kwargs)
        return value
