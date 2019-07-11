"""
Python wrappers to windows/linux install scripts for external dependencies
"""
import logging
import os

from build.settings import INSTALL_DIRS
from build.utils.process_runner import run_process_and_log

PATH_TO_DIR = os.path.dirname(os.path.realpath(__file__))


def valid_packages():
    """
    @returns :: A list of all valid packages for the operating system
    """
    valid = ['mantid']
    if os.name == 'nt':
        valid.append('7zip')
    return valid


def validate_input(list_of_packages, logger):
    """
    Ensure that all the package names provided by the user are valid.

    @param list_of_packages :: List of user provided packages
    @param logger :: Handle to the Build logger
    @returns :: True: All packages are valid
                False: Will print and log invalid package(s)
    """
    valid_packages_list = valid_packages()
    all_packages_valid = True
    for package in list_of_packages:
        if package.lower() not in valid_packages_list:
            logger.print_and_log("\"%s\" not recognised as a valid package "
                                 "for this operating system." % package,
                                 logging.ERROR)
            all_packages_valid = False
    return all_packages_valid


def install_package(package_name, log_handler):
    """
    Given a package name, find the correct install script,
    run it and return boolean for success.
    @param package_name :: The name of the package to install
    @param log_handler :: Handler for logging build info
    @returns :: True: exit code of installation script was 0
                False: exit code of installation script was non-zero
    """
    install_script = os.path.join(PATH_TO_DIR, (package_name + '.{}'))
    install_path = INSTALL_DIRS[package_name]
    unzip_path = ''
    if os.name == 'nt':
        if package_name == 'mantid':
            # No need to install mantid on windows currently so skip this
            return True
        install_script = install_script.format('bat')
        unzip_path = INSTALL_DIRS['7zip-location']
    else:
        install_script = install_script.format('sh')

    log_handler.logger.info("Installing %s with script %s" %
                            (package_name, install_script))
    if run_process_and_log([install_script, install_path, unzip_path]) is False:
        log_handler.print_and_log("Error encountered when installing %s. "
                                  "Check the build.log for more information." %
                                  package_name, logging.ERROR)
        return False

    log_handler.print_and_log("%s installed successfully" % package_name)
    return True
