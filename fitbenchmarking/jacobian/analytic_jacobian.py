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
        problem_formats = ['cutest']
        if self.problem.format not in problem_formats:
            raise NoJacobianError("Currently analytic Jacobians are only "
                                  "implemented for {0}. The problem format "
                                  " here is {1}".format(problem_formats,
                                                        self.problem.format))

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
            n = jac.shape[1]
            for i in range(n):
                jac[:, i] = jac[:, i] / e

        return jac
