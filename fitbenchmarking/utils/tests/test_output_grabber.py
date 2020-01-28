from __future__ import (absolute_import, division, print_function)
import unittest

from fitbenchmarking.utils.output_grabber import OutputGrabber


class OutputGrabberTests(unittest.TestCase):

    def test_correct_output(self):
        output_string = 'This is the correct output string\nSecond line'
        output = OutputGrabber()
        with output:
            print(output_string)


if __name__ == "__main__":
    unittest.main()
