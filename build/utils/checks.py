"""
Checks if modules can be imported and if the services inputted by the user
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
        from build.install.install_services import (install_service,
                                                    validate_input,
                                                    valid_services)
    except ImportError:
        BUILD_LOGGER.print_and_log("Could not import install_services. ",
                                    logging.ERROR)
        return False
    return True


def check_input(services):
    """
    Check the user input is valid.
    @returns :: False if user input is invalid
    """

    from build.install.install_services import valid_services, validate_input
    if not validate_input(services, BUILD_LOGGER):
        BUILD_LOGGER.print_and_log("Some services supplied were not valid.\n"
                                    "Valid services are: %s" % valid_services(),
                                    logging.ERROR)
        return False
    return True


def validate_services(list_of_services, quiet=True):
    """
    Check if services are installed and usable.
    Current checks: 7Zip, Mantid

    @param quiet :: boolean to decide if anything is printed
                    on validation failure
    @returns :: dictionary of {"service_name": validity(True/False)}
    """

    print("=======================")
    service_validity = validate_installs(list_of_services)
    if quiet is False:
        for service in service_validity:
            if service_validity[service] is False:
                BUILD_LOGGER.print_and_log("%s: False" % service, logging.INFO)
            else:
                if service == 'mantid' and os.name == 'nt':
                    # not required on windows
                    BUILD_LOGGER.print_and_log("Mantid: Skipped",
                                               logging.WARNING)
                else:
                    BUILD_LOGGER.print_and_log("%s: True" % service)
    print("=======================")
    return service_validity
