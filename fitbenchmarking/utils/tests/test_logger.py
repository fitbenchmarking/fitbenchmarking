"""
Tests for the log file.

Note: As get_logger is effectively an alias, it is not tested here.
"""
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import os
from unittest import TestCase

from fitbenchmarking.utils.log import get_logger, setup_logger
from fitbenchmarking.utils.output_grabber import OutputGrabber


class TestSetupLogger(TestCase):
    """
    Tests for the setup_logger method in log.
    """

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.log_file = os.path.join(self.temp_dir.name, 'some_log.txt')

    def test_file_creation_correct(self):
        """
        Test that the logger creates the correct file.
        """
        self.assertFalse(os.path.exists(self.log_file),
                         'Log file already present?')
        setup_logger(log_file=self.log_file, name='test1')
        logger = get_logger('test1')
        logger.info('Works?')
        self.assertTrue(os.path.exists(self.log_file),
                        'Failed to create log file.')

    def test_append_mode_on(self):
        """
        Test that append mode works when set to true.
        """
        setup_logger(log_file=self.log_file, name='test2')
        logger = get_logger('test2')
        logger.info('Before reset')
        setup_logger(log_file=self.log_file, append=True, name='test2')
        logger.info('After reset')

        with open(self.log_file, 'r') as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 2, 'Wrong number of lines in log file')
        self.assertIn('Before reset', lines[0])
        self.assertIn('After reset', lines[1])

    def test_append_mode_off(self):
        """
        Test that append mode works when set to false.
        """
        setup_logger(log_file=self.log_file, name='test3')

        logger = get_logger('test3')
        logger.info('Before reset')
        setup_logger(log_file=self.log_file, append=False, name='test3')
        logger.info('After reset')

        with open(self.log_file, 'r') as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 1, 'Wrong number of lines in log file')
        self.assertNotIn('Before reset', lines[0])
        self.assertIn('After reset', lines[0])


def test_level(capsys):
    """
    Test that setting the level limits the output from the logger.
    Note: This relies on a pytest fixture (capsys)
    """
    temp_dir = TemporaryDirectory()
    log_file = os.path.join(temp_dir.name, 'some_log.txt')
    setup_logger(log_file=log_file, level='WARNING', append=True, name='test4')
    logger = get_logger('test4')

    logger.error('An error message')
    logger.warning('A warning message')
    logger.info('An info message')

    out, _ = capsys.readouterr()
    output = out.splitlines()

    assert (len(output) == 2), 'Wrong number of lines in log'
    assert ('An error message' in output[0]), 'Error not captured by log'
    assert ('A warning message' in output[1]), 'Warning not captured by log'
