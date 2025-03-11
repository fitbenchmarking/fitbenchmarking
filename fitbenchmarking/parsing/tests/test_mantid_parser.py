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

    @parameterized.expand(
        [
            (
                {
                    "function": (
                        "name=LinearBackground,A0=0,A1=0;name=GausOsc"
                        ",A=0.2,Sigma=0.2,Frequency=1,Phi=0"
                    )
                },
                "CompositeFunction",
                [
                    {
                        "f0.A0": 0.0,
                        "f0.A1": 0.0,
                        "f1.A": 0.2,
                        "f1.Sigma": 0.2,
                        "f1.Frequency": 1.0,
                        "f1.Phi": 0.0,
                    }
                ],
            ),
            (
                {"function": "name=LinearBackground,A0=0,A1=0"},
                "LinearBackground",
                [{"A0": 0.0, "A1": 0.0}],
            ),
            (
                {"function": "name=GausOsc,A=0.2,Sigma=0.2,Frequency=1,Phi=0"},
                "GausOsc",
                [{"A": 0.2, "Sigma": 0.2, "Frequency": 1.0, "Phi": 0.0}],
            ),
            (
                {
                    "function": (
                        "name=GausOsc,A=0.2,Sigma=0.2,"
                        "Frequency=1,Phi=0,ties=(Sigma=0.2,Phi=0)"
                    )
                },
                "GausOsc",
                [{"A": 0.2, "Frequency": 1.0}],
            ),
        ]
    )
    def test_create_function(self, entries, equation, params):
        """
        Verifies the output of _create_function() method.
        """
        self.parser._entries = entries
        func = self.parser._create_function()
        assert callable(func)
        assert self.parser._equation == equation
        assert self.parser._mantid_function.name == equation
        assert str(self.parser._mantid_function.fun) == entries["function"]
        assert (
            str(self.parser._mantid_function.function) == entries["function"]
        )
        assert self.parser._starting_values == params
        assert self.parser._params_dict == params[0]

    def test_get_starting_values_and_get_equation(self):
        """
        Verifies the outputs of _get_starting_values()
        and _get_equation() methods.
        """
        self.parser._entries = {"function": "name=LinearBackground,A0=0,A1=0"}
        _ = self.parser._create_function()
        assert (
            self.parser._starting_values == self.parser._get_starting_values()
        )
        assert self.parser._equation == self.parser._get_equation()
