"""
This file contains a factory implementation for the Jacobians.
This is used to manage the imports and reduce effort in adding new Jacobian
methods.
"""
from importlib import import_module
from inspect import getmembers, isabstract, isclass

from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import NoJacobianError


def create_jacobian(options):
    """
    Create a Jacobian class.

    :param options: FitBenchmarking options object
    :type options: fitbenchmarking.utils.Options

    :return: Controller class for the problem
    :rtype: fitbenchmarking.jacobian.base_controller.Jacobian subclass
    """
    jac_method = options.jac_method
    num_method = options.num_method

    module_name = f'{jac_method}_jacobian' if jac_method == 'analytic' \
        else f'{jac_method}_{num_method}_jacobian'

    try:
        module = import_module('.' + module_name, __package__)
    except ImportError:
        raise NoJacobianError(f'Could not find Jacobian class with type as '
                              f'{jac_method} and numerical method as '
                              f'{num_method}.')

    classes = getmembers(module, lambda m: (isclass(m)
                                            and not isabstract(m)
                                            and issubclass(m, Jacobian)
                                            and m is not Jacobian))

    return classes[0][1]
