"""
This file contains unit tests for the mantid and mantid parser.
"""

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from parameterized import parameterized
from pytest import test_type as TEST_TYPE

from conftest import run_for_test_types
from fitbenchmarking.parsing.parser_factory import ParserFactory


@run_for_test_types(TEST_TYPE, "all")
class TestMantidDevParser(TestCase):
    """
    Unit tests the MantidDevParser class.
    """

    def setUp(self):
        """
        Set up resources before each test case.
        """
        path = Path(__file__).parent / "mantiddev" / "basic.txt"
        mantid_parser_cls = ParserFactory.create_parser(path)
        with patch.object(mantid_parser_cls, "__init__", lambda a, b, c: None):
            self.parser = mantid_parser_cls("test_file.txt", {"parse"})

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

    def test_parse_function(self):
        """
        Verifies the output of _parse_function() method.
        """
        assert self.parser._parse_function() == []
