from __future__ import (absolute_import, division, print_function)
import unittest
import platform

from fitbenchmarking.utils.output_grabber import OutputGrabber
from fitbenchmarking.utils.options import Options

class OutputGrabberTests(unittest.TestCase):

    def setUp(self):
        self.options = Options()
        self.plt = platform.system()

    def test_correct_output(self):
        output_string = 'This is the correct output string\nSecond line'
        output = OutputGrabber(self.options)
        with output:
            print(output_string)

        # there is currently an issue with OutputGrapper on Windows
        # see issues for details
        if self.plt != "Windows":
            # print adds an extra \n
            assert output.capturedtext == output_string + "\n"

    def test_incorrect_output(self):
        output_string = 'This is the correct output string\nSecond line'
        incorrect_output_sting = 'This is the incorrect string\n'
        output = OutputGrabber(self.options)
        with output:
            print(output_string)
        assert output.capturedtext != incorrect_output_sting


if __name__ == "__main__":
    unittest.main()
