"""
Module which calculates SciPy finite difference approximations
"""
import numpy as np
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.jacobian.base_jacobian import Jacobian


# pylint: disable=useless-super-delegation
class Scipy(Jacobian):
    """
    Implements SciPy finite difference approximations to the derivative
    """

    # Problem formats that are incompatible with certain Scipy Jacobians
    INCOMPATIBLE_PROBLEMS = {"cs": ["mantid"]}

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        func = self.cost_func.eval_r
        f0 = self.cached_func_values(self.cost_func.cache_rx,
                                     func,
                                     params,
                                     **kwargs)
        jac = approx_derivative(func, params, method=self.method,
                                rel_step=None, f0=f0,
                                bounds=(-np.inf, np.inf),
                                kwargs=kwargs)
        return jac

    def eval_cost(self, params, **kwargs):
        """
        Evaluates derivative of the cost function

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Computed derivative of the cost function
        :rtype: numpy array
        """
        func = self.cost_func.eval_cost
        r0 = self.cached_func_values(self.cost_func.cache_cost_x,
                                     func,
                                     params,
                                     **kwargs)
        jac = approx_derivative(func, params, method=self.method,
                                rel_step=None, f0=r0,
                                bounds=(-np.inf, np.inf),
                                kwargs=kwargs)
        return jac
