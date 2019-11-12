"""
This file contains a factory implementation for the controllers.
This is used to manage the imports and reduce effort in adding new controllers.
"""

from importlib import import_module
from inspect import isclass, isabstract, getmembers

from fitbenchmarking.fitting.controllers.base_controller import Controller


class ControllerFactory:
    """
    A factory for creating software controllers.
    This has the capability to select the correct controller, import it, and
    generate an instance of it.
    Controllers generated from this must be a subclass of
    base_controller.Controller
    """

    @staticmethod
    def create_controller(software):
        """
        Create a controller that matches the required software.

        :param software: The name of the software to create a controller for
        :type software: string

        :returns: Controller class for the problem
        :rtype: fitbenchmarking.fitting.base_controller.Controller subclass
        """

        module_name = '{}_controller'.format(software.lower())

        try:
            module = import_module('.' + module_name, __package__)
        except ImportError:
            raise ValueError(
                'Could not find controller for {}.'.format(software)
                + 'Check the input is correct and try again.')

        classes = getmembers(module, lambda m: (isclass(m)
                                                and not isabstract(m)
                                                and issubclass(m, Controller)
                                                and m is not Controller))

        return classes[0][1]
