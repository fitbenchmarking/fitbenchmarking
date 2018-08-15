"""
Installs all the optional external dependencies of the project giving
the user a choice of what to install.
"""

from __future__ import (absolute_import, division, print_function)

import logging
import os

from distutils.core import Command
from build.utils.common import BUILD_LOGGER
from build.utils import checks
from build.install.install_services import install_service


class InstallExternals(Command):
    """
    A custom command to run Pylint on all Python source files.
    """

    description = 'Install optional external dependencies of the project.\n' \
                  'Currently available: mantid'
    user_options = [('services=', 's',
                     'comma separated list of services to install')]

    def initialize_options(self):
        """
        Initialize services dictionary.
        """
        # Each user option must be listed here with their default value.
        self.services = {}

    def finalize_options(self):
        """
        If user has provided services format them to dictionary.
        If not use all services.
        """

        if self.services:
            self.services = self.services.split(",")
            service_dict = {}
            for service_name in self.services:
                service_dict[service_name] = False
            self.services = service_dict
        else:
            self.services = {'mantid': False}

        if os.name == 'nt' and '7zip' not in self.services:
            self.services['7zip'] = False

    def run(self):
        """
        Validate services to see if any are currently installed
        Install each service required by the project that did not validate
        Re-validate to ensure services are now installed
        """

        self._perform_preliminary_checks()

        BUILD_LOGGER.print_and_log("=== Installing external dependencies ===")
        services_to_install = self._get_valid_services_to_install()

        self._install_7zip(services_to_install)
        self._check_service_dictionary(services_to_install)
        self._install_services(services_to_install)
        self._check_if_invalid_install(services_to_install)

        logging.shutdown()


    def _install_7zip(self, services_to_install):
        if '7zip' in services_to_install:
            BUILD_LOGGER.print_and_log("Installing 7zip")
            if install_service('7zip', BUILD_LOGGER) is False:
                print("Unable to install 7zip. Check build logs for more info")
                return
            del self.services['7zip']
            services_to_install.remove('7zip')

    def _get_valid_services_to_install(self):
        self.services = checks.validate_services(self.services.keys(),
                                                 quiet=False)
        # Return a list of all non-valid services (those with value of false)
        services_to_install = [serv_name for serv_name in self.services.keys()
                               if self.services[serv_name] is False]

        return services_to_install

    def _perform_preliminary_checks(self):
        if not checks.check_imports():
            return
        if not checks.check_input(self.services):
            return

    @staticmethod
    def _install_services(services_to_install):
        for service in services_to_install:
            if install_service(service, BUILD_LOGGER) is False:
                print("Unable to install %s. "
                      "Check build logs for more informaton" % service)
            return

    @staticmethod
    def _check_service_dictionary(services_to_install):
        if not services_to_install:
            BUILD_LOGGER.print_and_log("Nothing to install - "
                                       "All given services are valid")
            return

    @staticmethod
    def _check_if_invalid_install(services_to_install):
        valid = checks.validate_services(services_to_install, quiet=False)
        if False in valid.values():
            BUILD_LOGGER.print_and_log("One or more services did not "
                                       "correctly install:", logging.ERROR)
            for service_name, _ in valid.items():
                if valid[service_name] is False:
                    BUILD_LOGGER.print_and_log("* %s" % service_name,
                                               logging.ERROR)
                BUILD_LOGGER.print_and_log("See build.log for more details.",
                                           logging.ERROR)
