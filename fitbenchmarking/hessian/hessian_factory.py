"""
This file contains a factory implementation for the Hessians.
This is used to manage the imports and reduce effort in adding new Hessian
methods.
"""
from importlib import import_module
from inspect import getmembers, isabstract, isclass

from fitbenchmarking.hessian.base_hessian import Hessian
from fitbenchmarking.utils.exceptions import NoHessianError


def create_hessian(hes_method):
    """
    Create a Hessian class.

    :param hes_method: Type of Hessian selected from options
    :type hes_method: str

    :return: Controller class for the problem
    :rtype: fitbenchmarking.hessian.base_controller.Hessian subclass
    """

    module_name = '{}_hessian'.format(hes_method)

    try:
        module = import_module('.' + module_name, __package__)
    except ImportError as e:
        raise NoHessianError('Could not find Hessian class with type as '
                             '{}.'.format(hes_method)) from e

    classes = getmembers(module, lambda m: (isclass(m)
                                            and not isabstract(m)
                                            and issubclass(m, Hessian)
                                            and m is not Hessian))

    return classes[0][1]
