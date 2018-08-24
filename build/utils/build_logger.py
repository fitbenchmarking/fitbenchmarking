"""
Handle the logging of build information
This is fundamentally an extra layer of functionality added to logging
"""
from __future__ import print_function

import os
import logging


class BuildLogger(object):
    """
    Class to handle logging for build script.
    """

    logger = None

    def __init__(self, root_directory):
        # Clear log file
        with open(os.path.join(root_directory, 'build.log'), 'w'):
            pass
        self._initialise_logger(root_directory)

    def _initialise_logger(self, root_directory):
        """
        Set up logger in given root directory and add handler
        @param root_directory :: base directory of the project
        """

        self.logger = logging.getLogger("build")
        handler = logging.FileHandler(os.path.join(root_directory, 'build.log'))
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s : '
                                               '%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def print_and_log(self, message, log_level=logging.INFO):
        """
        Print a message to the console and to the log file
        @param message :: message to display
        @param log_level :: level to log at (logging.LEVEL)
        """

        self.logger.log(level=log_level, msg=message)
        print(message)
