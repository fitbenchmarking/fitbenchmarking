"""
Script to hold common varibales used in building the project
"""
import os

from build.utils.build_logger import BuildLogger

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BUILD_LOGGER = BuildLogger(ROOT_DIR)
