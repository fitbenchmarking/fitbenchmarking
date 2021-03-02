from __future__ import absolute_import, division, print_function

import platform
import sys
import unittest

from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.output_grabber import OutputGrabber


class OutputGrabberTests(unittest.TestCase):

    def setUp(self):
        self.options = Options()
        self.plt = platform.system()

    def test_correct_stdout(self):
        """
        Test that the OutputGrabber grabs the stdout stream.
        """
        output_string = 'This is the correct output string\nSecond line'
        error_string = 'An error has occurred:\nSome details'

        output = OutputGrabber(self.options)
        with output:
            print(output_string, end='')
            print(error_string, end='', file=sys.stderr)

        # The output grabber is not enabled for windows
        if self.plt != "Windows":
            assert output.stdout_grabber.capturedtext == output_string

    def test_correct_stderr(self):
        """
        Test that the OutputGrabber grabs the stderr stream.
        """
        output_string = 'This is the correct output string\nSecond line'
        error_string = 'An error has occurred:\nSome details'

        output = OutputGrabber(self.options)
        with output:
            print(output_string, end='')
            print(error_string, end='', file=sys.stderr)

        # The output grabber is not enabled for windows
        if self.plt != "Windows":
            assert output.stderr_grabber.capturedtext == error_string


if __name__ == "__main__":
    unittest.main()
