"""
This file contains tests for the parsers.
"""

from pathlib import Path, PosixPath
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

import numpy as np
from parameterized import parameterized

from fitbenchmarking.parsing.fitbenchmark_parser import (
    FitbenchmarkParser,
    _find_first_line,
    _get_column_data,
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

    @parameterized.expand(['d=(e=true ,f = "bar"', "g=1.0,1.0,1.0]"])
    def test_parse_parens_with_invalid_inputs(self, input):
        """
        Verifies the ParsingError is raised by _parse_parens.
        """
        with self.assertRaises(exceptions.ParsingError):
            _ = self.parser._parse_parens(input)

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
            "{'f0.I':(1,A),'f0.A':[55, B], 'f1.B':{5, C}}",
        ]
    )
    def test_parse_range_with_invalid_inputs(self, range_str):
        """
        Verifies the ParsingError is raised by _parse_range.
        """
        with self.assertRaises(exceptions.ParsingError):
            _ = _parse_range(range_str)

    @parameterized.expand(
        [
            ("['multifit1.txt','multifit2.txt']", True),
            ('["multifit1.txt", "multifit2.txt"]', True),
            ("fit1.txt", False),
        ]
    )
    def test_is_multifit(self, input_file, expected):
        """
        Verifies the output of _is_multifit() method.
        """
        self.parser._entries = {"input_file": input_file}
        assert self.parser._is_multifit() == expected

    @parameterized.expand(
        [
            (
                "mantid",
                "multifit.txt",
                "['multifit1.txt','multifit2.txt']",
                [
                    PosixPath("mantid/data_files/multifit1.txt"),
                    PosixPath("mantid/data_files/multifit2.txt"),
                ],
                0,
            ),
            (
                "mantid",
                "start_end_x.txt",
                "mantid_start_end_x.dat",
                [
                    PosixPath("mantid/data_files/mantid_start_end_x.dat"),
                ],
                0,
            ),
            (
                "mantid",
                "multifit.txt",
                "['multit.txt','multift2.txt']",
                [None, None],
                2,
            ),
            (
                "mantid",
                "multifit.txt",
                "['multifit1.txt','multift2.txt']",
                [
                    PosixPath("mantid/data_files/multifit1.txt"),
                    None,
                ],
                1,
            ),
            (
                "mantid",
                "start_end_x.txt",
                "mant_start_end_x.dat",
                [None],
                1,
            ),
            (
                "ivp",
                "simplified_anac.txt",
                "simplified_anac.txt",
                [PosixPath("ivp/data_files/simplified_anac.txt")],
                0,
            ),
            (
                "hogben",
                "simple_sample.txt",
                "simple_sample.txt",
                [PosixPath("hogben/data/simple_sample.txt")],
                0,
            ),
            (
                "hogben",
                "simple_sample.txt",
                "simple_sale.txt",
                [None],
                1,
            ),
        ]
    )
    @patch("fitbenchmarking.parsing.fitbenchmark_parser.LOGGER")
    def test_get_data_file(
        self, folder, file, input_file, expected, count, mock_logger
    ):
        """
        Verifies the output of _get_data_file method.
        """
        self.parser._filename = Path(__file__).parent / folder / file
        self.parser._entries = {"input_file": input_file}
        paths = [
            path.relative_to(Path(__file__).parent) if path else None
            for path in self.parser._get_data_file()
        ]
        assert paths == expected
        assert len(mock_logger.method_calls) == count

    @parameterized.expand(
        [
            ({"plot_scale": "loglog"}, "loglog"),
            ({"plot_scale": "LOGLOG"}, "loglog"),
            ({"plot_scale": "logLOG"}, "loglog"),
            ({"plot_scale": "logy"}, "logy"),
            ({"plot_scale": "logY"}, "logy"),
            ({"plot_scale": "LOGY"}, "logy"),
            ({"plot_scale": "logx"}, "logx"),
            ({"plot_scale": "logX"}, "logx"),
            ({"plot_scale": "LOGX"}, "logx"),
            ({"plot_scale": "linear"}, "linear"),
            ({"plot_scale": "LINEAR"}, "linear"),
            ({}, "linear"),
        ]
    )
    def test_get_plot_scale_with_valid_inputs(self, entries, expected):
        """
        Verifies the output of _get_plot_scale() method.
        """
        self.parser._entries = entries
        assert self.parser._get_plot_scale() == expected

    @parameterized.expand(
        [
            ({"plot_scale": "logs"},),
            ({"plot_scale": "ylog"},),
            ({"plot_scale": "xlog"},),
            ({"plot_scale": "linaer"},),
        ]
    )
    def test_get_plot_scale_with_invalid_inputs(self, entries):
        """
        Verifies the ParsingError is raised by _get_plot_scale().
        """
        self.parser._entries = entries
        with self.assertRaises(exceptions.ParsingError):
            _ = self.parser._get_plot_scale()

    @parameterized.expand(
        [
            (["# X Y Z\n", "", "1 2 3\n"], 2),
            (["#   x0 x1 y e\n", "", "", "1 2 3 4\n"], 3),
            (["# X0 X1 Y0 Y1 E0 E1\n", "", " 1 2 3 4 5"], 2),
            (["<X> <Y> <E>", " 1  2  3 "], 1),
            (["<X0> <X1> <Y> <E>", "", "1 2  3 4 "], 2),
            (["# X Y Z\n", "", "-1 -2 -3\n"], 2),
            (["# X Y Z\n", "1 2 -3\n"], 1),
            (["# X Y\n", "1 2\n"], 1),
        ]
    )
    def test_find_first_line_with_valid_inputs(self, file_lines, expected):
        """
        Verifies the output of _find_first_line().
        """
        assert _find_first_line(file_lines) == expected

    @parameterized.expand(
        [
            (["# X Y Z\n", "", "\n"],),
            (["#   x0 x1 y e\n"],),
            (["<X> <Y> <E>"],),
            ([],),
            (["# X Y\n", "# comment", ""],),
            (["# X Y\n", "# X Y\n"],),
        ]
    )
    def test_find_first_line_with_invalid_inputs(self, file_lines):
        """
        Verifies the ParsingError is raised by _find_first_line().
        """
        with self.assertRaises(exceptions.ParsingError):
            _ = _find_first_line(file_lines)

    @parameterized.expand(
        [
            (["# X Y E\n"], 2, 3, {"x": [0], "y": [1], "e": [2]}),
            (["# Y X E\n"], 2, 3, {"x": [1], "y": [0], "e": [2]}),
            (["# E Y X\n"], 2, 3, {"x": [2], "y": [1], "e": [0]}),
            (["# X   Y   E\n"], 2, 3, {"x": [0], "y": [1], "e": [2]}),
            (["# X Y   E\n"], 2, 3, {"x": [0], "y": [1], "e": [2]}),
            (["# x y e\n"], 2, 3, {"x": [0], "y": [1], "e": [2]}),
            (
                ["# X0 X1  Y0 Y1  E1 E2\n"],
                2,
                6,
                {"x": [0, 1], "y": [2, 3], "e": [4, 5]},
            ),
            (["<x> <y> <e>\n"], 2, 3, {"x": [0], "y": [1], "e": [2]}),
            (["<x> <y> <e>\n"], 2, 3, {"x": [0], "y": [1], "e": [2]}),
            (["<X1> <Y1>\n"], 2, 2, {"x": [0], "y": [1], "e": []}),
            (
                ["<X0> <X1> <Y0> <Y1> <E1> <E2>\n"],
                2,
                6,
                {"x": [0, 1], "y": [2, 3], "e": [4, 5]},
            ),
            (
                ["<X0>    <X1>  <Y0>   <Y1>  <E1>  <E2>\n"],
                2,
                6,
                {"x": [0, 1], "y": [2, 3], "e": [4, 5]},
            ),
            (["<Y> <X>\n"], 2, 2, {"x": [1], "y": [0], "e": []}),
            ([""], 0, 2, {"x": [0], "y": [1], "e": []}),
            ([""], 0, 3, {"x": [0], "y": [1], "e": [2]}),
        ]
    )
    def test_get_column_data_valid_inputs(
        self, file_lines, first_line, dim, expected
    ):
        """
        Verifies the output of _get_column_data() function with valid inputs.
        """
        assert _get_column_data(file_lines, first_line, dim) == expected

    @parameterized.expand(
        [
            (["# X Y E\n"], 2, 2),
            (["# A B C\n"], 2, 3),
            ([""], 0, 1),
            ([""], 0, 4),
            (["# X0 X1  Y0 Y1  E1\n"], 2, 5),
            (["# X0 X1 E1\n"], 2, 3),
        ]
    )
    def test_get_column_data_invalid_inputs(self, file_lines, first_line, dim):
        """
        Verifies the ParsingError is raised by _get_column_data().
        """
        with self.assertRaises(exceptions.ParsingError):
            _ = _get_column_data(file_lines, first_line, dim)

    @parameterized.expand(
        [
            (
                ["# X Y E\n", "", "1 2 3\n"],
                2,
                {"x": [0], "y": [1], "e": [2]},
                {"x": np.array([1]), "y": np.array([2]), "e": np.array([3])},
            ),
            (
                ["# X Y E\n", "1 2 3\n", "4 B C\n"],
                1,
                {"x": [0], "y": [1], "e": [2]},
                {"x": np.array([1]), "y": np.array([2]), "e": np.array([3])},
            ),
            (
                ["# X Y E\n", "", "", "1 2 3\n", "4 5  6\n", "7  8 9\n"],
                3,
                {"x": [0], "y": [1], "e": [2]},
                {
                    "x": np.array([1, 4, 7]),
                    "y": np.array([2, 5, 8]),
                    "e": np.array([3, 6, 9]),
                },
            ),
            (
                ["1 2\n", "4 5\n", "7  8\n"],
                0,
                {"x": [0], "y": [1], "e": []},
                {"x": np.array([1, 4, 7]), "y": np.array([2, 5, 8])},
            ),
            (
                ["# X0 X1 Y0 Y1\n", "1 2 3 4\n", "5 6 7 8\n"],
                1,
                {"x": [0, 1], "y": [2, 3], "e": []},
                {
                    "x": np.array([[1, 2], [5, 6]]),
                    "y": np.array([[3, 4], [7, 8]]),
                },
            ),
        ]
    )
    @patch("fitbenchmarking.parsing.fitbenchmark_parser._find_first_line")
    @patch("fitbenchmarking.parsing.fitbenchmark_parser._get_column_data")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_data_points(
        self,
        file_lines,
        first_line,
        cols,
        expected,
        mock_open_file,
        mock_get_column_data,
        mock_find_first_line,
    ):
        """
        Verifies the output of _get_data_points() method.
        """
        mock_find_first_line.return_value = first_line
        mock_get_column_data.return_value = cols
        mock_open_file.return_value.readlines.return_value = file_lines
        result = self.parser._get_data_points("test")
        for key in expected:
            np.testing.assert_array_equal(result[key], expected[key])

    @parameterized.expand(
        [
            (
                [
                    {"name": "BackToBackExponential"},
                    {"name": "FlatBackground"},
                ],
                "2 Functions",
            ),
            (
                [
                    {"name": "BackToBackExponential"},
                    {"name": "FlatBackground"},
                    {"name": "GausOsc"},
                ],
                "3 Functions",
            ),
            ([{"name": "BackToBackExponential"}], "BackToBackExponential"),
            ([{"name": "FlatBackground"}], "FlatBackground"),
        ]
    )
    def test_get_equation(self, parsed_func, expected):
        """
        Verifies the output of _get_equation() method.
        """
        self.parser._parsed_func = parsed_func
        assert self.parser._get_equation() == expected

    @parameterized.expand(
        [
            (
                [
                    {
                        "name": "BackToBackExponential",
                        "I": 15000.0,
                        "A": 0.04,
                        "B": 0.03,
                        "X0": 29950,
                        "S": 12,
                    },
                ],
                [{"I": 15000.0, "A": 0.04, "B": 0.03, "X0": 29950, "S": 12}],
            ),
            (
                [
                    {"name": "FlatBackground", "A0": 30},
                ],
                [{"A0": 30}],
            ),
        ]
    )
    def test_get_starting_values(self, parsed_func, expected):
        """
        Verifies the output of _get_starting_values() method.
        """
        self.parser._parsed_func = parsed_func
        assert self.parser._get_starting_values() == expected
