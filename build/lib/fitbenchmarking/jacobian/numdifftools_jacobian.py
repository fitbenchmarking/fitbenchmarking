"""
Module which calculates numdifftools finite difference approximations
"""
import numdifftools as nd

from fitbenchmarking.jacobian.base_jacobian import Jacobian


class Numdifftools(Jacobian):
    """
    Implements numdifftools (https://numdifftools.readthedocs.io/en/latest/)
    finite difference approximations to the derivative
    """

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of the function

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """

        # Use the default numdifftools derivatives
        #
        # Note that once jac_func is set up, it can be called
        # multiple times by giving it params.
        # We tested moving the call to nd.Jacobian into
        # __init__ to see if this was a large overhead, but it
        # seemed not to make a difference.
        # Details of the experiment are in the GitHub issue.
        jac_func = nd.Jacobian(self.problem.eval_model,
                               method=self.method)
        return jac_func(params)
