"""
Script to hold common varibales used in building the project
"""
import os

from build.utils.build_logger import BuildLogger

build_dir = os.path.dirname(os.path.realpath(__file__))
BUILD_LOGGER = BuildLogger(build_dir)
