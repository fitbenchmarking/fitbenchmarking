"""
This file contains a factory implementation for the Jacobians.
This is used to manage the imports and reduce effort in adding new Jacobian
methods.
"""
from importlib import import_module
from inspect import getmembers, isabstract, isclass

from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import NoJacobianError


def create_jacobian(jac_method, num_method):
    """
    Create a Jacobian class.

    :param jac_method: Type of Jacobian selected from options
    :type jac_method: str
    :param num_method: Type of numerical method selected from options
    :type num_method: str

    :return: Controller class for the problem
    :rtype: fitbenchmarking.jacobian.base_controller.Jacobian subclass
    """

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


def get_jacobian_options(options):
    """
    Converts Jacobian options set in the options file into a list

    :param options: FitBenchmarking options object
    :type options: fitbenchmarking.utils.Options

    :return: List of Jacobians used in the fitting
    :rtype: list
    """

    jacobian_list = []
    for jac_method in options.jac_method:
        if jac_method == 'analytic':
            jacobian_list.append([jac_method, ''])
        else:
            for num_method in options.num_method:
                jacobian_list.append([jac_method, num_method])
    return jacobian_list
