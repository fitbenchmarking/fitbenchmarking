"""
This file contains unit tests for the mantid and mantiddev parser.
"""

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from parameterized import parameterized
from pytest import test_type as TEST_TYPE

from conftest import run_for_test_types
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.parsing.parser_factory import ParserFactory
from fitbenchmarking.utils.options import Options


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
        mantiddev_parser_cls = ParserFactory.create_parser(path)
        with patch.object(
            mantiddev_parser_cls, "__init__", lambda a, b, c: None
        ):
            self.parser = mantiddev_parser_cls("test_file.txt", {"parse"})

    @parameterized.expand(
        [
            (
                {"ties": "['A1']"},
                ["A1"],
                True,
            ),
            (
                {"ties": '["A1"]'},
                ["A1"],
                True,
            ),
            (
                {"ties": "['f1.Sigma', 'f1.Frequency']"},
                ["f1.Sigma", "f1.Frequency"],
                True,
            ),
            (
                {"ties": '["f1.Sigma", "f1.Frequency"]'},
                ["f1.Sigma", "f1.Frequency"],
                True,
            ),
            (
                {},
                [],
                True,
            ),
            (
                {},
                {},
                False,
            ),
        ]
    )
    def test_set_additional_info(self, entries, expected, multifit):
        """
        Verifies the output of _set_additional_info() method.
        """
        self.parser._entries = entries
        self.parser.fitting_problem = FittingProblem(Options())
        self.parser.fitting_problem.multifit = multifit
        self.parser._set_additional_info()
        if multifit:
            result = self.parser.fitting_problem.additional_info["mantid_ties"]
            assert result == expected
        else:
            assert self.parser.fitting_problem.additional_info == expected

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

    @parameterized.expand(
        [
            (
                [{"x": [2, 8]}],
                [2],
                [8],
            ),
            (
                [],
                [None, None],
                [None, None],
            ),
        ]
    )
    def test_set_data_points(self, fit_ranges, start_x, end_x):
        """
        Verifies the outputs of _set_data_points() method.
        """
        self.parser._filename = (
            Path("examples")
            / "benchmark_problems"
            / "MultiFit"
            / "basic_multifit.txt"
        )
        self.parser._entries = {
            "input_file": "['basic1.txt','basic2.txt']",
        }
        self.parser.fitting_problem = FittingProblem(Options())
        self.parser.fitting_problem.multifit = True
        data_points = [
            self.parser._get_data_points(p)
            for p in self.parser._get_data_file()
        ]
        self.parser._set_data_points(data_points, fit_ranges)
        assert len(self.parser.fitting_problem.data_x) == 2
        assert len(self.parser.fitting_problem.data_x[0]) == 18
        assert len(self.parser.fitting_problem.data_x[1]) == 18
        assert len(self.parser.fitting_problem.data_y) == 2
        assert len(self.parser.fitting_problem.data_y[0]) == 18
        assert len(self.parser.fitting_problem.data_y[1]) == 18
        assert len(self.parser.fitting_problem.data_e) == 2
        assert self.parser.fitting_problem.data_e == [None, None]
        assert self.parser.fitting_problem.start_x == start_x
        assert self.parser.fitting_problem.end_x == end_x


@run_for_test_types(TEST_TYPE, "all")
class TestMantidParser(TestCase):
    """
    Unit tests the MantidParser class.
    """

    def setUp(self):
        """
        Set up resources before each test case.
        """
        path = (
            Path("examples")
            / "benchmark_problems"
            / "MultiFit"
            / "basic_multifit.txt"
        )
        mantid_parser_cls = ParserFactory.create_parser(path)
        with patch.object(mantid_parser_cls, "__init__", lambda a, b, c: None):
            self.parser = mantid_parser_cls("test_file.txt", {"parse"})

    @parameterized.expand(
        [
            ({"function": "name=LinearBackground,A0=0,A1=0"},),
            ({"function": "name=GausOsc,A=0.2,Sigma=0.2,Frequency=1,Phi=0"},),
        ]
    )
    def test_set_additional_info(self, entries):
        """
        Verifies the output of _set_additional_info() method.
        """
        self.parser._entries = entries
        self.parser.fitting_problem = FittingProblem(Options())
        self.parser._set_additional_info()
        e = self.parser.fitting_problem.additional_info["mantid_equation"]
        assert e == entries["function"]
