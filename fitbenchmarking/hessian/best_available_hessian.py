"""
Module which acts as a analytic Hessian calculator when available, otherwise
uses a trusted software to approximate.
"""

from typing import Any

from fitbenchmarking.hessian.analytic_hessian import Analytic
from fitbenchmarking.hessian.base_hessian import Hessian
from fitbenchmarking.hessian.scipy_hessian import Scipy
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


class BestAvailable(Hessian):
    """
    Class to apply an analytical Hessian if available -- otherwise choose a
    scipy one.
    """

    def __init__(self, problem, jacobian):
        """
        Best available hessian for problems.

        :param problem: The parsed problem.
        :type problem:
            :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
        :param jacobian: The jacobian for the problem
        :type jacobian: subclass of
            :class:`~fitbenchmarking.jacobian.base_jacobian`
        """
        if callable(problem.hessian):
            self.sub_hes = Analytic(problem, jacobian)
            self.sub_hes.method = "default"
        else:
            self.sub_hes = Scipy(problem, jacobian)
            self.sub_hes.method = "2-point"

    def eval(self, params, **kwargs):
        """
        Evaluates Hessian of the model

        :param params: The parameter values to find the Hessian at
        :type params: list

        :return: Computed Hessian
        :rtype: 3D numpy array
        """
        return self.sub_hes.eval(params, **kwargs)

    @property
    def method(self):
        """
        Utility function to get the numerical method

        :return: the names of the parameters
        :rtype: list of str
        """
        return self.sub_hes.method

    @method.setter
    def method(self, value):
        """
        Utility function to set the numerical method

        :param value: the name of the numerical method
        :type value: str
        """
        if value != "default":
            LOGGER.warning(
                "Method cannot be selected for best_available, "
                "using default of %s.",
                self.sub_hes.method,
            )

    def name(self) -> str:
        """
        Get a name for the current status of the hessian.

        :return: A unique name for this hessian/method combination
        :rtype: str
        """
        return "best_available"

    def __getattribute__(self, __name: str) -> Any:
        if __name in ["sub_hes", "method", "name", "eval"]:
            return super().__getattribute__(__name)
        return self.sub_hes.__getattribute__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in ["sub_hes", "name", "eval"]:
            return super().__setattr__(__name, __value)
        if __name == "method":
            if __value != "default":
                LOGGER.warning(
                    "Method cannot be selected for best_available, "
                    "using default of %s.",
                    self.sub_hes.method,
                )
            return None
        return setattr(self.sub_hes, __name, __value)
