"""
Module which acts as a analytic Jacobian calculator
"""
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import NoJacobianError


# pylint: disable=useless-super-delegation
class Analytic(Jacobian):
    """
    Class to apply an analytical Jacobian
    """

    def __init__(self, problem):
        super(Analytic, self).__init__(problem)
        problem_formats = ['cutest']
        if self.problem.format not in problem_formats:
            raise NoJacobianError("Currently analytic Jacobians are only "
                                  "implemented for {0}. The problem format "
                                  " here is {1}".format(problem_formats,
                                                        self.problem.format))

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        jac = self.problem.jacobian(x, params)
        return jac
