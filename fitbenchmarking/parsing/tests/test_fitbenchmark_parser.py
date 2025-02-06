"""
This file contains tests for the parsers.
"""

from unittest import TestCase
from unittest.mock import MagicMock, patch

from parameterized import parameterized

from fitbenchmarking.parsing.fitbenchmark_parser import (
    FitbenchmarkParser,
    _parse_range,
)
from fitbenchmarking.utils import exceptions


class TestFitbenchmarkParser(TestCase):
    """
    Tests the FitbenchmarkParser class and related functions.
    """

    @parameterized.expand(
        [
            (["name = '\\sample_problem'"], {"name": "sample_problem"}),
            (["name = 'sample_problem/'"], {"name": "sample_problem"}),
            (['name = "sample_problem"'], {"name": "sample_problem"}),
            (["name = '\\sample_problem/////'"], {"name": "sample_problem"}),
            (["#fitbenchmarking"], {}),
            ([" #fitbenchmarking"], {}),
            (
                ["name = 'sample_problem' # my important comment"],
                {"name": "sample_problem"},
            ),
            (
                ["function = 'Userdefined: a/4 ** 6'"],
                {"function": "Userdefined: a/4 ** 6"},
            ),
            (
                ["function = 'Userdefined = a/4 ** 6'"],
                {"function": "Userdefined = a/4 ** 6"},
            ),
            (
                ["fit_ranges = {'x': [29650.0, 30500.0]}"],
                {"fit_ranges": "{'x': [29650.0, 30500.0]}"},
            ),
            (
                ["parameter_ranges = {'f0.I':(1,2), 'f0.A':(3,4)}"],
                {"parameter_ranges": "{'f0.I':(1,2), 'f0.A':(3,4)}"},
            ),
            (
                ["function = 'name=FlatBackground, A0=30'"],
                {"function": "name=FlatBackground, A0=30"},
            ),
        ]
    )
    @patch.object(FitbenchmarkParser, "__init__", lambda a, b, c: None)
    def test_get_data_problem_entries(self, file_data, expected):
        """
        Verifies the output of _get_data_problem_entries() method.
        """
        parser = FitbenchmarkParser("test_file.txt", {"parse"})
        parser.file = MagicMock()
        parser.file.readlines.return_value = file_data
        assert parser._get_data_problem_entries() == expected

    @parameterized.expand(
        [
            (
                {"function": "name=F1, A=0.04, B=0.03; name=F2, C=30"},
                [
                    {"name": "F1", "A": 0.04, "B": 0.03},
                    {"name": "F2", "C": 30},
                ],
            ),
            (
                {"function": "name=F1, A=0.04, B=0.03"},
                [{"name": "F1", "A": 0.04, "B": 0.03}],
            ),
        ]
    )
    @patch.object(FitbenchmarkParser, "__init__", lambda a, b, c: None)
    def test_parse_function(self, entries, expected):
        """
        Verifies the output of _parse_function() method.
        """
        parser = FitbenchmarkParser("test_file.txt", {"parse"})
        parser._entries = entries
        assert parser._parse_function() == expected

    @parameterized.expand(
        [
            (
                "{'f0.I':(1,2),'f0.A':(3, 4), 'f1.B':(5, 6)}",
                {"f0.i": [1.0, 2.0], "f0.a": [3.0, 4.0], "f1.b": [5.0, 6.0]},
            ),
            (
                "{'f0.I':[1,2],'f0.A':[3, 4], 'f1.B':[5, 6]}",
                {"f0.i": [1.0, 2.0], "f0.a": [3.0, 4.0], "f1.b": [5.0, 6.0]},
            ),
            (
                "{'f0.I':{1,2},'f0.A':{3, 4}, 'f1.B':{5, 6}}",
                {"f0.i": [1.0, 2.0], "f0.a": [3.0, 4.0], "f1.b": [5.0, 6.0]},
            ),
            (
                "{'f0.I':(1,2),'f0.A':[3, 4], 'f1.B':{5, 6}}",
                {"f0.i": [1.0, 2.0], "f0.a": [3.0, 4.0], "f1.b": [5.0, 6.0]},
            ),
            (
                '{"f0.I":(1,2),"f0.A":[3, 4], "f1.B":{5, 6}}',
                {"f0.i": [1.0, 2.0], "f0.a": [3.0, 4.0], "f1.b": [5.0, 6.0]},
            ),
            (
                '{"f0.I  ":(1,2),"f0.A ":[3, 4], " f1.B":{5, 6}}',
                {"f0.i": [1.0, 2.0], "f0.a": [3.0, 4.0], "f1.b": [5.0, 6.0]},
            ),
        ]
    )
    def test_parse_range_with_valid_inputs(self, range_str, expected):
        """
        Verifies the output of _parse_range function.
        """
        assert _parse_range(range_str) == expected

    @parameterized.expand(
        [
            "{'f0.I':(1,2),'f0.A':(3, 4, 'f1.B':(5, 6)}",
            "{'f0.I':1,2],'f0.A':[3, 4], 'f1.B':[5, 6]}",
            "{'f0.I':{1,2},'f0.A':{3, 4}, 'f1.B':{5, 6}",
            "{'f0.I':(1,2,'f0.A':[3, 4, 'f1.B':{5, 6}",
            "{'f0.I':(1,2],'f0.A':[3, 4}, 'f1.B':{5, 6)}",
            "{'f0.I':(2,1),'f0.A':[3, 4], 'f1.B':{5, 6}}",
            "{'f0.I':(1,1A),'f0.A':[55, 4], 'f1.B':{5, 6C}}",
        ]
    )
    def test_parse_range_with_invalid_inputs(self, range_str):
        """
        Verifies the ParsingError is raised.
        """
        with self.assertRaises(exceptions.ParsingError):
            _ = _parse_range(range_str)
