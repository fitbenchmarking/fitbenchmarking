"""
This file contains a factory implementation for the controllers.
This is used to manage the imports and reduce effort in adding new controllers.
"""

import os
from importlib import import_module
from inspect import getmembers, isabstract, isclass

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import (MissingSoftwareError,
                                              NoControllerError)


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

        :return: Controller class for the problem
        :rtype: fitbenchmarking.fitting.base_controller.Controller subclass
        """

        module_name = '{}_controller'.format(software.lower())

        try:
            module = import_module('.' + module_name, __package__)
        except ImportError as e:
            full_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                     module_name+'.py'))
            if os.path.exists(full_path):
                raise MissingSoftwareError('Requirements are missing for the '
                                           '{} controller: {}'.format(
                                               software, e))
            else:
                raise NoControllerError('Could not find controller for {}. '
                                        'Check the input is correct and try '
                                        'again.'.format(software))

        classes = getmembers(module, lambda m: (isclass(m)
                                                and not isabstract(m)
                                                and issubclass(m, Controller)
                                                and m is not Controller))

        return classes[0][1]
