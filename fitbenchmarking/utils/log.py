"""
Utility functions to support logging for the fitbenchmarking
project.
"""
import logging
import sys


def setup_logger(log_file='./fitbenchmarking.log', name='fitbenchmarking',
                 append=False, level='INFO'):
    """
    Define the location and style of the log file.

    :param log_file: path to the log file, defaults to './fitbenchmarking.log'
    :type log_file: str, optional
    :param name: The name of the logger to run the setup for,
                 defaults to fitbenchmarking
    :type name: str, optional
    :param append: Whether to append to the log or create a new one,
                   defaults to False
    :type append: bool, optional
    :param level: The level of error to print, defaults to 'INFO'
    :type level: str, optional
    """
    FORMAT = '[%(asctime)s]  %(levelname)s %(filename)s: %(message)s'
    formatter = logging.Formatter(FORMAT, "%H:%M:%S")

    handler = logging.FileHandler(log_file, mode='a' if append else 'w')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    for h in logger.handlers:
        logger.removeHandler(h)

    logger.addHandler(handler)

    # Define a Handler which writes <level> or higher messages to console
    levels = {'CRITICAL': logging.CRITICAL,
              'ERROR': logging.ERROR,
              'WARNING': logging.WARNING,
              'INFO': logging.INFO,
              'DEBUG': logging.DEBUG,
              'NOTSET': logging.NOTSET}
    log_level = levels.get(level.upper(), logging.INFO)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    logger.addHandler(console)
    logger.propagate = False


def get_logger(name='fitbenchmarking'):
    """
    Get the unique logger for the given name.
    This is a straight pass through but will be more intutive for people who
    have not used python logging.

    :param name: Name of the logger to use, defaults to 'fitbenchmarking'
    :type name: str, optional

    :return: The named logger
    :rtype: logging.Logger
    """
    return logging.getLogger(name)
