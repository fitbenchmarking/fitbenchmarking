"""
Tests for the exception handler file.
"""
from unittest import TestCase

from fitbenchmarking.cli.exception_handler import exception_handler
from fitbenchmarking.utils.exceptions import FittingProblemError


class TestExceptionHandler(TestCase):
    """
    Tests for the exception handler function in exception handler.
    """
    def test_return_unchanged(self):
        """
        Test that the return value is correct when wrapping a function.
        """
        @exception_handler
        def get_val():
            """
            Do something...
            """
            return "The correct string!"

        result = get_val()
        self.assertEqual(result, "The correct string!")

    def test_non_fb_exception(self):
        """
        Test behaviour on a non fitbenchmarking exception.
        """
        @exception_handler
        def get_val():
            """
            Do something...
            """
            raise RuntimeError

        self.assertRaises(SystemExit, get_val)

    def test_fb_exception(self):
        """
        Test behaviour on a fitbenchmarking exception.
        """
        @exception_handler
        def get_val():
            """
            Do something...
            """
            raise FittingProblemError

        self.assertRaises(SystemExit, get_val)
