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
    This will strip off any 'debug' inputs.

    :param f: The function to wrap
    :type f: python function
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        debug = kwargs.get('debug', False)
        kwargs.pop('debug')

        try:
            return f(*args, **kwargs)
        except exceptions.FitBenchmarkException as e:
            print('Error while running FitBenchmarking. Exiting. '
                  'See below for more information.')
            if debug:
                raise
            else:
                print(e)
                sys.exit(1)
        except Exception as e:
            print('Unknown exception. Exiting.')
            if debug:
                raise
            else:
                print(e)
                sys.exit(1)

    return wrapped
