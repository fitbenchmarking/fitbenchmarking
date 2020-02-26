"""
A collection of tests to validate external requirements:
mantid
"""
import os
from build.settings import INSTALL_DIRS


def validate_installs(list_of_packages):
    """
    Wrapper function to validate multiple installs
    :param list_of_packages: packages to validate
    :return: Dictionary of {"package_name": install_validity(true/False)
    """
    package_validity = {}
    for package in list_of_packages:
        package = package.lower()
        if package == 'mantid':
            package_validity['mantid'] = _validate_mantid()
        elif package == '7zip':
            package_validity['7zip'] = _validate_7zip()
    return package_validity


def _validate_7zip():
    if os.path.isfile(os.path.join(INSTALL_DIRS['7zip-location'], '7z.exe')):
        return True
    return False


def _validate_mantid():
    if os.name == 'nt':
        # No need to validate mantid on windows as it is not required
        return True
    if os.path.isfile(os.path.join('/opt', 'mantidnightly-python3', 'bin', 'mantidpython')):
        return True
    return False
