"""
Module which calculates numdifftools finite difference approximations
"""
import numdifftools as nd
import numpy as np

from fitbenchmarking.jacobian.base_jacobian import Jacobian

# pylint: disable=useless-super-delegation
class numdifftools(Jacobian):
    """
    Implements numdifftools (https://numdifftools.readthedocs.io/en/latest/)
    finite difference approximations to the derivative
    """

    def __init__(self, cost_func):
        """
        initializes the numdifftools jacobian
        """
        super(numdifftools, self).__init__(cost_func)        

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of the fucntion

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        
        # Use the default numdifftools derivatives
        jac_func = nd.Jacobian(self.cost_func.eval_r, \
                            method=self.method)
        jac = jac_func(params)
        return jac

    def eval_cost(self, params, **kwargs):
        """
        Evaluates derivative of the cost function

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Computed derivative of the cost function
        :rtype: numpy array
        """
        # Use the default numdifftools derivatives
        jac_cost = nd.Jacobian(self.cost_func.eval_cost, \
                               method=self.method)

        jac = jac_cost(params)
        return jac

