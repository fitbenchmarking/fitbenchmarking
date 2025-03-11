"""
This file contains tests for the mantid and mantid parser.
"""

from unittest import TestCase
from unittest.mock import patch

from parameterized import parameterized
from pytest import test_type as TEST_TYPE

from conftest import run_for_test_types
from fitbenchmarking.parsing.mantiddev_parser import MantidDevParser


@run_for_test_types(TEST_TYPE, "all")
class TestMantidDevParser(TestCase):
    """
    Unit tests the MantidDevParser class.
    """

    @patch.object(MantidDevParser, "__init__", lambda a, b, c: None)
    def setUp(self):
        """
        Set up resources before each test case.
        """
        self.parser = MantidDevParser("test_file.txt", {"parse"})

    @parameterized.expand(
        [
            (
                {"ties": "['A1']"},
                ["A1"],
            ),
            (
                {"ties": '["A1"]'},
                ["A1"],
            ),
            (
                {"ties": "['f1.Sigma', 'f1.Frequency']"},
                ["f1.Sigma", "f1.Frequency"],
            ),
            (
                {"ties": '["f1.Sigma", "f1.Frequency"]'},
                ["f1.Sigma", "f1.Frequency"],
            ),
            (
                {},
                [],
            ),
        ]
    )
    def test_parse_ties(self, entries, expected):
        """
        Verifies the output of _parse_ties() method.
        """
        self.parser._entries = entries
        assert self.parser._parse_ties() == expected
