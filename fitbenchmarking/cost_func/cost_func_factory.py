"""
This file contains a factory implementation for the available cost functions
within FitBenchmarking.
"""
from importlib import import_module
from inspect import getmembers, isabstract, isclass

from fitbenchmarking.cost_func.base_cost_func import CostFunc
from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.utils.exceptions import CostFuncError


def create_cost_func(cost_func_type):
    """
    Create a cost function class class.

    :param cost_func_type: Type of cost function selected from options
    :type cost_func_type: str

    :return: Cost function class for the problem
    :rtype: fitbenchmarking.cost_func.base_cost_func.CostFunc subclass
    """

    module_name = '{}_cost_func'.format(cost_func_type)

    try:
        module = import_module('.' + module_name, __package__)
    except ImportError as e:
        raise CostFuncError('Could not find Cost function class with type as '
                            '{}.'.format(cost_func_type)) from e
    classes = getmembers(module, lambda m: (isclass(m)
                                            and not isabstract(m)
                                            and issubclass(m, CostFunc)
                                            and m is not CostFunc
                                            and m is not BaseNLLSCostFunc))

    return classes[0][1]
