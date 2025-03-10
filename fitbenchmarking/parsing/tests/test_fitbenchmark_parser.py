"""
This file contains tests for the fitbenchmark parser.
"""

import sys
from pathlib import Path
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
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


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
            "na.m.e= BackToBackExponential",
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
                [{"x": np.array([[1], [2]]), "y": np.array([3])}],
                True,
            ),
            (
                [{"x": np.array([[1], [2]]), "y": np.array([[3], [4]])}],
                True,
            ),
            (
                [{"x": np.array([1]), "y": np.array([[3], [4]])}],
                True,
            ),
        ]
    )
    def test_is_multivariate(self, data_points, expected):
        """
        Verifies the output of _is_multivariate method.
        """
        assert self.parser._is_multivariate(data_points) == expected

    @parameterized.expand(
        [
            (
                {},
                False,
                False,
            ),
            (
                {"n_fits": 1},
                True,
                True,
            ),
        ]
    )
    def test_is_multistart(self, entries, is_error, expected):
        """
        Verifies the _is_multistart method.
        """
        self.parser._entries = entries
        if is_error:
            with self.assertRaises(exceptions.ParsingError):
                _ = self.parser._is_multistart()
        else:
            assert self.parser._is_multistart() == expected

    @parameterized.expand(
        [
            (
                "mantiddev",
                "multifit.txt",
                "['multifit1.txt','multifit2.txt']",
                [
                    Path("mantiddev") / "data_files" / "multifit1.txt",
                    Path("mantiddev") / "data_files" / "multifit2.txt",
                ],
                0,
            ),
            (
                "mantiddev",
                "start_end_x.txt",
                "mantid_start_end_x.dat",
                [
                    Path("mantiddev")
                    / "data_files"
                    / "mantid_start_end_x.dat",
                ],
                0,
            ),
            (
                "mantiddev",
                "multifit.txt",
                "['multit.txt','multift2.txt']",
                [None, None],
                2,
            ),
            (
                "mantiddev",
                "multifit.txt",
                "['multifit1.txt','multift2.txt']",
                [
                    Path("mantiddev") / "data_files" / "multifit1.txt",
                    None,
                ],
                1,
            ),
            (
                "mantiddev",
                "start_end_x.txt",
                "mant_start_end_x.dat",
                [None],
                1,
            ),
            (
                "ivp",
                "simplified_anac.txt",
                "simplified_anac.txt",
                [Path("ivp") / "data_files" / "simplified_anac.txt"],
                0,
            ),
            (
                "hogben",
                "simple_sample.txt",
                "simple_sample.txt",
                [Path("hogben") / "data" / "simple_sample.txt"],
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
        self.parser._PARAM_IGNORE_LIST = ["name"]
        assert self.parser._get_starting_values() == expected

    @parameterized.expand(
        [
            (
                [
                    {
                        "x": np.array([0]),
                        "y": np.array([1]),
                        "e": np.array([2]),
                    },
                ],
                [],
            ),
            (
                [
                    {
                        "x": np.array([3]),
                        "y": np.array([4]),
                        "e": np.array([5]),
                    },
                ],
                [{"x": [1, 4]}],
            ),
            (
                [
                    {
                        "x": np.array([3]),
                        "y": np.array([4]),
                    },
                ],
                [],
            ),
        ]
    )
    def test_set_data_points(self, data_points, fit_ranges):
        """
        Verifies the output of _set_data_points() method.
        """
        self.parser.fitting_problem = FittingProblem(Options())
        self.parser._set_data_points(data_points, fit_ranges)
        assert self.parser.fitting_problem.data_x == data_points[0]["x"]
        assert self.parser.fitting_problem.data_y == data_points[0]["y"]
        assert self.parser.fitting_problem.data_e == data_points[0].get(
            "e", None
        )
        if fit_ranges:
            assert self.parser.fitting_problem.start_x == fit_ranges[0]["x"][0]
            assert self.parser.fitting_problem.end_x == fit_ranges[0]["x"][1]

    @patch.object(sys, "path", new_callable=list)
    @patch("importlib.import_module")
    def test_get_jacobian(
        self,
        mock_import_module,
        mock_sys_path,
    ):
        """
        Verifies the output of _get_jacobian().
        """
        self.parser._entries = {
            "jac": "module=jac/sample, dense_func=d, sparse_func=s"
        }
        self.parser._filename = Path("test") / "problem.txt"

        for jac in ["dense_func", "sparse_func"]:
            mock_function, mock_module = MagicMock(), MagicMock()
            setattr(mock_module, jac[0], mock_function)
            mock_import_module.return_value = mock_module
            result = self.parser._get_jacobian(jac)

            self.assertTrue(
                any("test" in path and "jac" in path for path in mock_sys_path)
            )
            self.assertIn(
                ("sample",),
                [call.args for call in mock_import_module.mock_calls],
            )
            self.assertEqual(result, mock_function)

    @parameterized.expand(
        [
            ({"jac": "module=j/p/sample"},),
            ({},),
        ]
    )
    def test_get_jacobian_returns_none(self, entries):
        """
        Verifies the output of _get_jacobian() returns None.
        """
        self.parser._entries = entries
        for jac in ["dense_func", "sparse_func"]:
            result = self.parser._get_jacobian(jac)
            assert result is None

    def test_create_function(self):
        """
        Verifies the NotImplementedError is raised by _create_function().
        """
        with self.assertRaises(NotImplementedError):
            _ = self.parser._create_function()

    @patch(
        "fitbenchmarking.parsing.fitbenchmark_parser.FitbenchmarkParser._get_data_points"
    )
    @patch(
        "fitbenchmarking.parsing.fitbenchmark_parser.FitbenchmarkParser._get_data_file"
    )
    @patch(
        "fitbenchmarking.parsing.fitbenchmark_parser.FitbenchmarkParser._parse_function"
    )
    @patch(
        "fitbenchmarking.parsing.fitbenchmark_parser.FitbenchmarkParser._create_function"
    )
    @patch(
        "fitbenchmarking.parsing.fitbenchmark_parser.FitbenchmarkParser._get_data_problem_entries"
    )
    def test_parse(
        self,
        mock_get_data_problem_entries,
        mock_create_function,
        mock_parse_function,
        mock_get_data_file,
        mock_get_data_points,
    ):
        """
        Verifies the output of the parse() method.
        """
        mock_get_data_problem_entries.return_value = {
            "software": "Mantid",
            "name": "Basic MultiFit",
            "description": "Test Parse",
            "input_file": "['basic1.txt','basic2.txt']",
            "function": "name=LinearBackground,A0=0,A1=0",
            "parameter_ranges": "{'A0': (1,10), 'A1': (1,5)}",
        }

        mock_parse_function.return_value = [
            {"name": "LinearBackground", "A0": "0", "A1": "0"}
        ]

        mock_get_data_file.return_value = ["basic1.txt", "basic2.txt"]
        mock_x = np.array([1.0, 2.0, 3.0])
        mock_y = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        mock_get_data_points.return_value = {"x": mock_x, "y": mock_y}
        mock_create_function.return_value = ["mock_function"]

        self.parser.options = Options()
        self.parser._PARAM_IGNORE_LIST = ["name"]
        result = self.parser.parse()

        # Verify all the parameters are set correctly
        assert not result.additional_info
        assert not result.data_e
        assert result.data_x.shape == (3,)
        assert result.data_y.shape == (3, 2)
        assert result.description == "Test Parse"
        assert not result.end_x
        assert result.equation == "LinearBackground"
        assert result.format == "mantid"
        assert result.function == ["mock_function"]
        assert not result.hessian
        assert not result.jacobian
        assert result.multifit
        assert result.multivariate
        assert not result.multistart
        assert result.name == "Basic MultiFit"
        assert result.param_names == ["A0", "A1"]
        assert result.plot_scale == "linear"
        assert not result.sorted_index
        assert not result.sparse_jacobian
        assert not result.start_x
        assert result.value_ranges == [(1.0, 10.0), (1.0, 5.0)]
