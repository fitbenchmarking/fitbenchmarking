"""
Module which calculates numdifftools finite difference approximations
"""
import numdifftools as nd

from fitbenchmarking.hessian.base_hessian import Hessian


class Numdifftools(Hessian):
    """
    Implements numdifftools (https://numdifftools.readthedocs.io/en/latest/)
    finite difference approximations to the derivative
    """

    def eval(self, params, **kwargs):
        """
        Evaluates Hessian of problem.eval_model, returning the value
        \nabla^2_p f(x, p)

        :param params: The parameter values to find the Hessian at
        :type params: list

        :return: Approximation of the Hessian
        :rtype: 3D numpy array
        """
        x = kwargs.get("x", self.problem.data_x)

        def jac_func(params):
            return self.jacobian.eval(params, x=x).T
        hes_func = nd.Jacobian(jac_func, method=self.method)
        hes = hes_func(params)

        # ensure Hessian is symmetric
        return 0.5*(hes+hes.transpose(1, 0, 2))
