"""
This file holds an exception handler decorator that should wrap all cli
functions to provide cleaner output.
"""

from functools import wraps
import sys

from fitbenchmarking.utils import exceptions


def exception_handler(f):
    """
    Decorator to simplify handling exceptions within FitBenchmarking

    :param f: The function to wrap
    :type f: python function
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except exceptions.FitBenchmarkException as e:
            print('Error while running FitBenchmarking. Exiting. '
                  'See below for more information.')
            print(e)
            sys.exit(1)
        except Exception as e:
            print('Unknown exception. Exiting.')
            print(e)
            sys.exit(1)

    return wrapped
