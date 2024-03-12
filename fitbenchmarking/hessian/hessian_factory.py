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

    module_name = f'{hes_method}_hessian'

    try:
        module = import_module('.' + module_name, __package__)
    except ImportError as e:
        raise NoHessianError('Could not find Hessian class with type as '
                             f'{hes_method}.') from e

    classes = getmembers(module, lambda m: all([
        isclass(m),
        not isabstract(m),
        issubclass(m, Hessian),
        m is not Hessian,
        m.__name__.lower() == hes_method.replace('_', ''),
    ]))

    return classes[0][1]
