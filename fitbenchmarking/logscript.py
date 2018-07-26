"""
Utility functions to support logging for the fitbenchmarking
algorithm.
"""
# Copyright &copy; 2016 ISIS Rutherford Appleton Laboratory, NScD
# Oak Ridge National Laboratory & European Spallation Source
#
# This file is part of Mantid.
# Mantid is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Mantid is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# File change history is stored at: <https://github.com/mantidproject/mantid>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>

from __future__ import (absolute_import, division, print_function)

import os
import logging

class loggingFunctions():

    def logging_directory(self):

        current_dir = os.path.dirname(os.path.realpath(__file__))
        logs_dir = os.path.join(current_dir, "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        return logs_dir


    def  setup_logger(self, name, file, level=logging.DEBUG,
                      formatter='%(asctime)s %(name)s %(levelname)s: %(message)s'):
        '''
            Sets up a logger to a certain file.

            @param name :: name of the logger
            @param file :: name of file where the logs will be written
            @param level :: level of the logger, can be either DEBUG, ERROR, INFO etc.
            @param formatter :: format of what is displayed in the logger
        '''

        formatter = logging.Formatter(formatter, "%H:%M:%S")
        logs_dir = self.logging_directory()

        log_file = os.path.join(logs_dir, file)

        handler = logging.FileHandler(log_file, mode='a')
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)

        logger.setLevel(level)
        logger.addHandler(handler)

        return logger


    def clear_logs_folder(self):
        '''
            Function that clear all logs from previous runs.

            @param directory: Directory in which the logs are located
        '''
        directory = self.logging_directory()

        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)


    def close_logger(self, logger):

        handlers = logger.handlers[:]
        for handler in handlers:

            logger.removeHandler(handler)
            handler.close()
            handler.flush()

    def shutdown_logging(self):

        logging.shutdown()
