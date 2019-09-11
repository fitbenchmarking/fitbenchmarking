"""
Utility functions to support logging for the fitbenchmarking
project.
"""

from __future__ import (absolute_import, division, print_function)

import os
import logging
from utils import create_dirs

current_path = os.path.dirname(os.path.realpath(__file__))
fitbm_main_dir = os.path.abspath(os.path.join(current_path, os.pardir))
logs_path = os.path.join(fitbm_main_dir, 'logs')

# Create or clear directory before logging run.
if not os.path.exists(logs_path):
    os.makedirs(logs_path)
else:
    create_dirs.del_contents_of_dir(logs_path)

# Create logger with name fitbenchmarking (this is the name of the file)
FORMATTER = '[%(asctime)s]  %(levelname)s %(filename)s: %(message)s'

formatter = logging.Formatter(FORMATTER, "%H:%M:%S")
handler = logging.FileHandler(logs_path + os.sep + 'fitbenchmarking.log',
                              mode='a')
handler.setFormatter(formatter)
logger = logging.getLogger('fitbenchmarking')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Define a Handler which writes WARNING messages or higher to the console
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

