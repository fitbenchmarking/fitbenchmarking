"""
Installs all the optional external dependencies of the project giving
the user a choice of what to install. See help for setup.py for user choices.
"""

from __future__ import (absolute_import, division, print_function)

import logging
import os

from distutils.core import Command
from build.utils.common import BUILD_LOGGER
from build.utils import checks
from build.install.install_packages import install_package


class InstallExternals(Command):
    """
    Enables commands to install externals for fit benchmarking.
    """

    description = 'Install optional external dependencies of the project.\n' \
                  'Currently available: mantid'
    user_options = [('packages=', 's',
                     'comma separated list of packages to install')]

    def initialize_options(self):
        """
        Initialize packages dictionary.
        """
        # Each user option must be listed here with their default value.
        self.packages = {}

    def finalize_options(self):
        """
        If user has provided packages format them to dictionary.
        If not use all packages.
        """

        if self.packages:
            self.packages = self.packages.split(",")
            package_dict = {}
            for package_name in self.packages:
                package_dict[package_name] = False
            self.packages = package_dict
        else:
            self.packages = {'mantid': False}

        if os.name == 'nt' and '7zip' not in self.packages:
            self.packages['7zip'] = False

    def run(self):
        """
        Validate packages to see if any are currently installed
        Install each package required by the project that did not validate
        Re-validate to ensure packages are now installed
        """

        self._perform_preliminary_checks()

        BUILD_LOGGER.print_and_log("=== Installing external dependencies ===")
        packages_to_install = self._get_valid_packages_to_install()

        # explanation for installing the below is in build.install.install_packages
        self._install_7zip(packages_to_install)
        self._check_package_dictionary(packages_to_install)
        self._install_packages(packages_to_install)
        self._check_if_invalid_install(packages_to_install)

        logging.shutdown()


    def _get_valid_packages_to_install(self):
        self.packages = checks.validate_packages(self.packages.keys(),
                                                 quiet=False)
        # Return a list of all non-valid packages (those with value of false)
        packages_to_install = [serv_name for serv_name in self.packages.keys()
                               if self.packages[serv_name] is False]

        return packages_to_install

    def _install_7zip(self, packages_to_install):
        if '7zip' in packages_to_install:
            BUILD_LOGGER.print_and_log("Installing 7zip")
            if install_package('7zip', BUILD_LOGGER) is False:
                print("Unable to install 7zip. Check build logs for more info")
                return
            del self.packages['7zip']
            packages_to_install.remove('7zip')

    def _perform_preliminary_checks(self):
        if not checks.check_imports():
            return
        if not checks.check_input(self.packages):
            return

    @staticmethod
    def _install_packages(packages_to_install):
        for package in packages_to_install:
            if install_package(package, BUILD_LOGGER) is False:
                print("Unable to install %s. "
                      "Check build logs for more informaton" % package)
            return

    @staticmethod
    def _check_package_dictionary(packages_to_install):
        if not packages_to_install:
            BUILD_LOGGER.print_and_log("Nothing to install - "
                                       "All given packages are valid")
            return

    @staticmethod
    def _check_if_invalid_install(packages_to_install):
        valid = checks.validate_packages(packages_to_install, quiet=False)
        if False in valid.values():
            BUILD_LOGGER.print_and_log("One or more packages did not "
                                       "correctly install:", logging.ERROR)
            for package_name, _ in valid.items():
                if valid[package_name] is False:
                    BUILD_LOGGER.print_and_log("* %s" % package_name,
                                               logging.ERROR)
                BUILD_LOGGER.print_and_log("See build.log for more details.",
                                           logging.ERROR)
