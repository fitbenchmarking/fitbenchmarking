"""
Module which acts as a analytic Jacobian calculator
"""
from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import NoJacobianError


# pylint: disable=useless-super-delegation
class Analytic(Jacobian):
    """
    Class to apply an analytical Jacobian
    """

    def __init__(self, problem):
        super(Analytic, self).__init__(problem)
        if not callable(problem.jacobian):
            raise NoJacobianError("Problem set selected does not currently "
                                  "support analytic Jacobians")

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of problem.eval_f or a weighted problem.eval_f

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        e = kwargs.get("e", self.problem.data_e)
        jac = self.problem.jacobian(x, params)

        if self.problem.options.use_errors:
            # scales each column of the Jacobian by the weights
            jac = jac / e[:, None]

        return jac
