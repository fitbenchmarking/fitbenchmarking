"""
Checks if modules can be imported and if the packages inputted by the user
can be installed.
"""
from __future__ import (absolute_import, division, print_function)

import os
import logging
from build.utils.common import BUILD_LOGGER
from build.utils.validate_installs import validate_installs

def check_imports():
    """
    Check that imports can be performed.
    @returns :: False if imports fail
    """
    try:
        # pylint:disable=unused-variable
        from build.install.install_packages import (install_package,
                                                    validate_input,
                                                    valid_packages)
    except ImportError:
        BUILD_LOGGER.print_and_log("Could not import install_packages. ",
                                    logging.ERROR)
        return False
    return True


def check_input(packages):
    """
    Check the user input is valid.
    @returns :: False if user input is invalid
    """

    from build.install.install_packages import valid_packages, validate_input
    if not validate_input(packages, BUILD_LOGGER):
        BUILD_LOGGER.print_and_log("Some packages supplied were not valid.\n"
                                    "Optional valid packages are: %s" % valid_packages(),
                                    logging.ERROR)
        return False
    return True


def validate_packages(list_of_packages, quiet=True):
    """
    Check if packages are installed and usable.
    Current checks: 7Zip, Mantid

    @param quiet :: boolean to decide if anything is printed
                    on validation failure
    @returns :: dictionary of {"package_name": validity(True/False)}
    """

    print("=======================")
    package_validity = validate_installs(list_of_packages)
    if quiet is False:
        for package in package_validity:
            if package_validity[package] is False:
                BUILD_LOGGER.print_and_log("%s: False" % package, logging.INFO)
            else:
                if package == 'mantid' and os.name == 'nt':
                    # not required on windows
                    BUILD_LOGGER.print_and_log("Mantid: Skipped",
                                               logging.WARNING)
                else:
                    BUILD_LOGGER.print_and_log("%s: True" % package)
    print("=======================")
    return package_validity
