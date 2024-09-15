"""
Module which acts as a analytic Jacobian calculator when available, otherwise
uses a trusted software to approximate.
"""

from typing import Any

from fitbenchmarking.jacobian.analytic_jacobian import Analytic
from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


class BestAvailable(Jacobian):
    """
    Class to apply an analytical Jacobian if available -- otherwise choose a
    scipy one.
    """

    def __init__(self, problem):
        if callable(problem.jacobian):
            self.sub_jac = Analytic(problem)
            self.sub_jac.method = "default"
        else:
            self.sub_jac = Scipy(problem)
            self.sub_jac.method = "2-point"

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of the model, :math:`\\nabla_p f(x,p)`,
        at the point given by the parameters.

        :param params: The parameter values at which to evaluate the Jacobian
        :type params: list

        :return: Computed Jacobian
        :rtype: numpy array
        """
        return self.sub_jac.eval(params, **kwargs)

    @property
    def method(self):
        """
        Utility function to get the numerical method

        :return: the names of the parameters
        :rtype: list of str
        """
        return self.sub_jac.method

    @method.setter
    def method(self, value):
        """
        Utility function to set the numerical method

        :param value: the name of the numerical method
        :type value: str
        """
        if value != "default":
            LOGGER.warning(
                "Method cannot be selected for best_available, using default of %s.",
                self.sub_jac.method,
            )

    def name(self) -> str:
        """
        Get a name for the current status of the jacobian.

        :return: A unique name for this jacobian/method combination
        :rtype: str
        """
        return "best_available"

    def __getattribute__(self, __name: str) -> Any:
        if __name in ["sub_jac", "method", "name", "eval"]:
            return super().__getattribute__(__name)
        return self.sub_jac.__getattribute__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in ["sub_jac", "name", "eval"]:
            return super().__setattr__(__name, __value)
        if __name == "method":
            if __value != "default":
                LOGGER.warning(
                    "Method cannot be selected for best_available, "
                    "using default of %s.",
                    self.sub_jac.method,
                )
            return None
        return setattr(self.sub_jac, __name, __value)
