"""
Utility decorator function for saving and writing files.
"""
from functools import wraps

from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()

FILEPATH_MESSAGE = "\nERROR: \n   The file path to the results directory " \
                   "is too long. Please change the results directory\n   " \
                   "so that it is well within the 260 character limit.\n"

UNKNOWN_MESSAGE = "\nERROR: \n   An unexpected error occurred while " \
                  "writing the output files. Please report this message " \
                  "to the FitBenchmarking team."


def write_file(function):
    """
    A decorator function used for catching exceptions which can happen
    specifically when writing files. It will log a useful error message
    if the problem is identified.

    :param function: A callable function which writes files.
    :type function: A callable function.

    :return: It depends on the function being wrapped.
    :rtype: It depends on the function being wrapped.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except FileNotFoundError as ex:
            filepath_err = "The filename or extension is too long" in \
                           str(ex) or "No such file or directory" in str(ex)

        LOGGER.error(FILEPATH_MESSAGE if filepath_err else UNKNOWN_MESSAGE)

    return wrapper
