"""
Utility decorator function for saving and writing files.
"""
from functools import wraps

from fitbenchmarking.utils.exceptions import FilepathTooLongError

# The character limit for a filepath on Windows is 260
CHARACTER_LIMIT = 260
FILEPATH_MESSAGE = f"\n   Please change the results directory so that it " \
                   f"is well within the {CHARACTER_LIMIT} character limit.\n"


def write_file(function):
    """
    A decorator function used for catching exceptions which can happen
    specifically when writing files. It will log a useful error message
    if the problem is identified.

    :param function: A callable function which writes files.
    :type function: A callable function.

    :return: A callable wrapped function which writes files.
    :rtype: A callable function.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except FileNotFoundError as ex:
            messages = ["The filename or extension is too long",
                        "No such file or directory"]
            if any(message in str(ex) for message in messages):
                raise FilepathTooLongError(FILEPATH_MESSAGE) from ex
            raise

    return wrapper
