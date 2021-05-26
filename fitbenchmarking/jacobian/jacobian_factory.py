"""
This file contains a factory implementation for the Jacobians.
This is used to manage the imports and reduce effort in adding new Jacobian
methods.
"""
from importlib import import_module
from inspect import getmembers, isabstract, isclass

from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import NoJacobianError


def create_jacobian(jac_method):
    """
    Create a Jacobian class.

    :param jac_method: Type of Jacobian selected from options
    :type jac_method: str

    :return: Controller class for the problem
    :rtype: fitbenchmarking.jacobian.base_controller.Jacobian subclass
    """

    module_name = '{}_jacobian'.format(jac_method)

    try:
        module = import_module('.' + module_name, __package__)
    except ImportError as e:
        raise NoJacobianError('Could not find Jacobian class with type as '
                              '{}.'.format(jac_method)) from e

    classes = getmembers(module, lambda m: (isclass(m)
                                            and not isabstract(m)
                                            and issubclass(m, Jacobian)
                                            and m is not Jacobian))

    return classes[0][1]
