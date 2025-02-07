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

    @patch.object(FitbenchmarkParser, "__init__", lambda a, b, c: None)
    def setUp(self):
        """
        Set up resources before each test case.
        """
        self.parser = FitbenchmarkParser("test_file.txt", {"parse"})

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
    def test_get_data_problem_entries(self, file_data, expected):
        """
        Verifies the output of _get_data_problem_entries() method.
        """
        self.parser.file = MagicMock()
        self.parser.file.readlines.return_value = file_data
        assert self.parser._get_data_problem_entries() == expected

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
    def test_parse_function(self, entries, expected):
        """
        Verifies the output of _parse_function() method.
        """
        self.parser._entries = entries
        assert self.parser._parse_function() == expected

    @parameterized.expand(
        [
            ("True", True, bool),
            ("TRUE", True, bool),
            ("true", True, bool),
            ("False", False, bool),
            ("FALSE", False, bool),
            ("false", False, bool),
            ("BackToBackExponential", "BackToBackExponential", str),
            ("1", 1, int),
            ("100", 100, int),
            ("2.0", 2.0, float),
            ("200.0", 200.0, float),
        ]
    )
    def test_parse_function_value(self, input, expected, expected_type):
        """
        Verifies the output of _parse_function_value() method.
        """
        result = self.parser._parse_function_value(input)
        assert result == expected
        assert isinstance(result, expected_type)

    @parameterized.expand(
        [
            (
                "name=BackToBackExponential, I=1.5e4, A=0.04, B=3",
                {
                    "name": "BackToBackExponential",
                    "I": 15000.0,
                    "A": 0.04,
                    "B": 3,
                },
            ),
            (
                "name = BackToBackExponential, I = 1.5e4, A = 0.04, B = 3",
                {
                    "name": "BackToBackExponential",
                    "I": 15000.0,
                    "A": 0.04,
                    "B": 3,
                },
            ),
            (
                "name= BackToBackExponential, I= 1.5e4, A= 0.04, B= 3",
                {
                    "name": "BackToBackExponential",
                    "I": 15000.0,
                    "A": 0.04,
                    "B": 3,
                },
            ),
            (
                "name =BackToBackExponential, I =1.5e4, A =0.04, B =3",
                {
                    "name": "BackToBackExponential",
                    "I": 15000.0,
                    "A": 0.04,
                    "B": 3,
                },
            ),
            (
                " name=FlatBackground, A0=30",
                {"name": "FlatBackground", "A0": 30},
            ),
            (
                "a=1,b=3.2,c='foo',d=(e=true,f='bar'),g=[1.0,1.0,1.0]",
                {
                    "a": 1,
                    "b": 3.2,
                    "c": "foo",
                    "d": {"e": True, "f": "bar"},
                    "g": [1.0, 1.0, 1.0],
                },
            ),
            (
                "d=(e=true,f='bar'),  g=[1.0,1.0,1.0]",
                {"d": {"e": True, "f": "bar"}, "g": [1.0, 1.0, 1.0]},
            ),
            (
                'd=(e=true ,f = "bar"),  g=[ 1.0, 1.0, 1.0]',
                {"d": {"e": True, "f": "bar"}, "g": [1.0, 1.0, 1.0]},
            ),
            (
                "module=func/anac,func=anac,step=0.1,gamma=15,mu=-0.5",
                {
                    "module": "func/anac",
                    "func": "anac",
                    "step": 0.1,
                    "gamma": 15,
                    "mu": -0.5,
                },
            ),
        ]
    )
    def test_parse_single_function_with_valid_inputs(self, input, expected):
        """
        Verifies the output of _parse_single_function() method with valid
        inputs.
        """
        assert self.parser._parse_single_function(input) == expected

    @parameterized.expand(
        [
            "na+me= BackToBackExponential",
            "na.me= BackToBackExponential",
            "na$me = BackToBackExponential",
            "na%me = BackToBackExponential",
        ]
    )
    def test_parse_single_function_with_invalid_inputs(self, input):
        """
        Verifies the ParsingError is raised by _parse_single_function.
        """
        with self.assertRaises(exceptions.ParsingError):
            _ = self.parser._parse_single_function(input)

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
        Verifies the output of _parse_range function with valid inputs.
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
        Verifies the ParsingError is raised by _parse_range.
        """
        with self.assertRaises(exceptions.ParsingError):
            _ = _parse_range(range_str)

    def test_is_multifit(self):
        """
        Verifies the output of _is_multifit() method is always False.
        """
        assert not self.parser._is_multifit()
