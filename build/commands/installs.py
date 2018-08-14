
"""
Module to install external programs not required by the project
7zip
ActiveMQ
ICAT
Mantid
"""
from __future__ import print_function
import logging
import os

# pylint:disable=no-name-in-module,import-error
from distutils.core import Command

from build.utils.common import BUILD_LOGGER


class InstallExternals(Command):
    """
    Command to install all the external requirements for the project
    """
    description = 'Install external dependencies of the project'
    user_options = [('services=', 's',
                     'comma separated list of services to install')]

    def initialize_options(self):
        """ Initialise the services dictionary """
        self.services = {}

    def finalize_options(self):
        """
        If user has provided services format them to dictionary
        If not use all services
        """

        if self.services:
            self.services = self.services.split(",")
            service_dict = {}
            for service_name in self.services:
                service_dict[service_name] = False
            self.services = service_dict
        else:
            self.services = {'activemq': False,
                             'icat': False,
                             'mantid': False}
        if os.name == 'nt' and '7zip' not in self.services:
            self.services['7zip'] = False

    def run(self):
        """
        Validate services to see if any are currently installed
        Install each service required by the project that did not validate
        Re-validate to ensure services are now installed
        """
        #  Validate
        if not self._check_imports():
            return
        from build.install.install_services import install_service
        if not self._check_input():
            return

        BUILD_LOGGER.
        print_and_log("======== Installing external dependencies ==========")

        self.services = self._validate_services(self.services.keys(), quiet=False)
        # Return a list of all non-valid services (those with value of false)
        services_to_install = [service_name for service_name in self.services.keys()
                               if self.services[service_name] is False]
        # Ensure 7zip is installed first
        if '7zip' in services_to_install:
            BUILD_LOGGER.print_and_log("Installing 7zip (required for other installations")
            if install_service('7zip', BUILD_LOGGER) is False:
                print("Unable to install 7zip. Check build logs for more information")
                return
            del self.services['7zip']
            services_to_install.remove('7zip')

        if not services_to_install:
            BUILD_LOGGER.print_and_log("Nothing to install - All given services are valid")
            return

        for service in services_to_install:
            if install_service(service, BUILD_LOGGER) is False:
                print("Unable to install %s. Check build logs for more informaton" % service)
                return

        valid = self._validate_services(services_to_install, quiet=False)
        if False in valid.values():
            BUILD_LOGGER.print_and_log("One or more services did not correctly install:",
                                       logging.ERROR)
            for service_name, _ in valid.items():
                if valid[service_name] is False:
                    BUILD_LOGGER.print_and_log("* %s" % service_name, logging.ERROR)
                BUILD_LOGGER.print_and_log("See build.log for more details.", logging.ERROR)


    @staticmethod
    def _check_imports():
        """
        Check that imports can be performed
        :return: False if imports fail
        """
        try:
            # pylint:disable=unused-variable
            from build.install.install_services import (install_service, validate_input,
                                                        valid_services)
        except ImportError:
            BUILD_LOGGER.print_and_log("Could not import install_services. "
                                       "Have you migrated the test settings correctly?",
                                       logging.ERROR)
            return False
        return True

    def _check_input(self):
        """
        Check the user input is valid
        :return: False if user input is invalid
        """
        from build.install.install_services import valid_services, validate_input
        if not validate_input(self.services, BUILD_LOGGER):
            BUILD_LOGGER.print_and_log("Some services supplied were not valid.\n"
                                       "Valid services are: %s" % valid_services(),
                                       logging.ERROR)
            return False
        return True

    @staticmethod
    def _validate_services(list_of_services, quiet=True):
        """
        Check if services are installed and usable. Current checks:
            7Zip, ActiveMQ, icat, Mantid
        :param quiet: boolean to decide if anything is printed on validation failure
        :return: dictionary of {"service_name": validity(True/False)}
        """
        from build.tests.validate_installs import validate_installs
        print("=======================")
        service_validity = validate_installs(list_of_services)
        if quiet is False:
            for service in service_validity:
                if service_validity[service] is False:
                    BUILD_LOGGER.print_and_log("%s: False" % service, logging.ERROR)
                else:
                    if service == 'mantid' and os.name == 'nt':
                        # not required on windows
                        BUILD_LOGGER.print_and_log("Mantid: Skipped", logging.WARNING)
                    else:
                        BUILD_LOGGER.print_and_log("%s: True" % service)
        print("=======================")
return service_validity
