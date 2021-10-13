"""
Implements the base class for the Jacobian.
"""
from abc import ABCMeta, abstractmethod
from numpy import array_equal, ascontiguousarray


def make_contiguous(eval_func):
    """
    Returns a wrapper function which ensures the numpy array returned
    from an eval function is contiguous in memory.

    :param eval_func: The eval or eval_cost function of a Jacobian.
    :type eval_func: A callable function.

    :return: A wrapper function around the eval method.
    :rtype: A callable function.
    """
    def eval_wrapper(params, **kwargs):
        return ascontiguousarray(eval_func(params, **kwargs))
    return eval_wrapper


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

        self.use_default_jac = False
        self._method = None

        # Make sure the returned jacobian array is contiguous in memory.
        # Some fitting packages use C or FORTRAN to manipulate memory,
        # such as Levmar, which can return a bad fit if the jacobian is
        # stored in non-contiguous memory.
        self.eval = make_contiguous(self.eval)
        self.eval_cost = make_contiguous(self.eval_cost)

    @abstractmethod
    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of the model

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Computed Jacobian
        :rtype: numpy array
        """
        raise NotImplementedError

    @abstractmethod
    def eval_cost(self, params, **kwargs):
        """
        Evaluates Jacobian of the cost function

        :param params: The parameter values to find the Jacobian at
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
        Utility function to set the numerical method

        :param value: the name of the numerical method
        :type value: str
        """
        self._method = value
