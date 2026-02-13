"""
This file contains unit tests for the mantid and mantiddev parser.
"""

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from parameterized import parameterized
from pytest import test_type as TEST_TYPE

from conftest import run_for_test_types
from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.parsing.parser_factory import ParserFactory
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


@run_for_test_types(TEST_TYPE, "mantid")
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
                False,
            ),
            (
                {"function": "name=LinearBackground,A0=0,A1=0"},
                "LinearBackground",
                [{"A0": 0.0, "A1": 0.0}],
                False,
            ),
            (
                {"function": "name=GausOsc,A=0.2,Sigma=0.2,Frequency=1,Phi=0"},
                "GausOsc",
                [{"A": 0.2, "Sigma": 0.2, "Frequency": 1.0, "Phi": 0.0}],
                False,
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
                False,
            ),
            (
                {
                    "function": (
                        "name=BackToBackExponential,I={f0.I},A={f0.A},"
                        "B={f0.B},X0={f0.X0},S={f0.S};"
                        "name=FlatBackground,A0={f1.A0}"
                    ),
                    "parameter_means": (
                        "f0.I=15000, f0.A=0.04, f0.B=0.03,"
                        " f0.X0=29950, f0.S=12, f1.A0=30"
                    ),
                },
                "CompositeFunction",
                [
                    {
                        "f0.I": 15000,
                        "f0.A": 0.04,
                        "f0.B": 0.03,
                        "f0.X0": 29950,
                        "f0.S": 12,
                        "f1.A0": 30,
                    }
                ],
                True,
            ),
        ]
    )
    def test_create_function(self, entries, equation, params, multistart):
        """
        Verifies the output of _create_function() method.
        """
        self.parser._entries = entries
        self.parser.fitting_problem = FittingProblem(Options())
        self.parser.fitting_problem.multistart = multistart
        func = self.parser._create_function()
        assert callable(func)
        assert self.parser._equation == equation
        assert self.parser._mantid_function.name == equation
        function = entries["function"]
        if multistart:
            parameter_means = self.parser._parse_single_function(
                entries["parameter_means"]
            )
            for key, value in parameter_means.items():
                function = function.replace(f"{{{key}}}", str(value))
        assert str(self.parser._mantid_function.fun) == function
        assert str(self.parser._mantid_function.function) == function
        assert self.parser._starting_values == params
        assert self.parser._params_dict == params[0]

    def test_get_starting_values_and_get_equation(self):
        """
        Verifies the outputs of _get_starting_values()
        and _get_equation() methods.
        """
        self.parser._entries = {"function": "name=LinearBackground,A0=0,A1=0"}
        self.parser.fitting_problem = FittingProblem(Options())
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

    @patch.object(
        FitbenchmarkParser, "_dense_jacobian", return_value=lambda x: x
    )
    def test_dense_jacobian(self, mock):
        """
        Verifies _dense_jacobian() returns jac returned by
        super()._dense_jacobian() if it is not None.
        """
        jac = self.parser._dense_jacobian()
        mock.assert_called_once()
        assert jac is not None
        assert callable(jac)

    @patch.object(FitbenchmarkParser, "_dense_jacobian", return_value=None)
    def test_dense_jacobian_exception(self, mock):
        """
        Verifies _dense_jacobian() returns None when exception
        is raised.
        """
        self.parser._entries = {
            "input_file": "basic1.txt",
        }
        self.parser._params_dict = {}
        self.parser.fitting_problem = FittingProblem(Options())
        self.parser.fitting_problem.data_x = [1, 2, 3]
        self.parser.fitting_problem.data_y = [4, 5, 6]
        with patch.object(self.parser, "_jacobian", side_effect=RuntimeError):
            assert self.parser._dense_jacobian() is None


@run_for_test_types(TEST_TYPE, "mantid")
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

    @parameterized.expand(
        [
            (
                {
                    "n_fits": "1",
                    "parameter_means": [1, 2],
                    "parameter_sigmas": [3, 4],
                },
                False,
                True,
            ),
            ({}, False, False),
            ({"n_fits": "1", "parameter_sigmas": [3, 4]}, True, False),
            ({"n_fits": "1", "parameter_means": [1, 2]}, True, False),
        ]
    )
    def test_is_multistart(self, entries, is_error, expected):
        """
        Verifies the _is_multistart() method.
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
                {
                    "n_fits": "5",
                    "parameter_means": "f0.I=15000, f0.A=0.04, "
                    "f0.B=0.03, f0.X0=29950, f0.S=12, f1.A0=30",
                    "parameter_sigmas": "f0.I=1000, f0.A=0.006, "
                    "f0.B=0.005, f0.X0=60, f0.S=2.5, f1.A0=10",
                    "function": "name=BackToBackExponential, I={f0.I}, "
                    "A={f0.A}, B={f0.B}, X0={f0.X0}, S={f0.S} ; "
                    "name=FlatBackground, A0={f1.A0}",
                    "seed": "10",
                },
                True,
                [
                    {
                        "f0.I": 13896.661550934468,
                        "f0.A": 0.0407588983090711,
                        "f0.B": 0.02622533859088124,
                        "f0.X0": 29881.93074802258,
                        "f0.S": 9.53661098399633,
                        "f1.A0": 11.304027671582887,
                    },
                    {
                        "f0.I": 14274.975359755561,
                        "f0.A": 0.04505825542482603,
                        "f0.B": 0.025925929463304544,
                        "f0.X0": 29968.342313164256,
                        "f0.S": 9.217614673409658,
                        "f1.A0": 25.76650890188418,
                    },
                    {
                        "f0.I": 14218.194742681942,
                        "f0.A": 0.04514761929685461,
                        "f0.B": 0.028280725711028694,
                        "f0.X0": 29838.898898196476,
                        "f0.S": 10.098434918907898,
                        "f1.A0": 40.138967997979975,
                    },
                    {
                        "f0.I": 15266.975856394392,
                        "f0.A": 0.04285110185169151,
                        "f0.B": 0.02974309953106533,
                        "f0.X0": 29939.37678950961,
                        "f0.S": 13.620061472091137,
                        "f1.A0": 39.83715344494681,
                    },
                    {
                        "f0.I": 14751.41927056111,
                        "f0.A": 0.0372953884115055,
                        "f0.B": 0.025138631613128213,
                        "f0.X0": 29975.54954003663,
                        "f0.S": 11.675421608971229,
                        "f1.A0": 36.30041950729873,
                    },
                ],
            ),
            (
                {
                    "n_fits": "3",
                    "parameter_means": "f0.I=15000, f0.A=0.04, "
                    "f0.B=0.03, f0.X0=29950, f0.S=12, f1.A0=30",
                    "parameter_sigmas": "f0.I=700, f0.A=0.6, "
                    "f0.B=0.005, f0.X0=600, f0.S=5, f1.A0=20",
                    "function": "name=BackToBackExponential, I={f0.I}, "
                    "A={f0.A}, B={f0.B}, X0={f0.X0}, S={f0.S} ; "
                    "name=FlatBackground, A0={f1.A0}",
                    "seed": "100",
                },
                True,
                [
                    {
                        "f0.I": 14189.715247015918,
                        "f0.A": 0.36638418682514773,
                        "f0.B": 0.03350727830055225,
                        "f0.X0": 30612.60834302339,
                        "f0.S": 12.236055915453703,
                        "f1.A0": 36.511489377743075,
                    },
                    {
                        "f0.I": 15202.829061629425,
                        "f0.A": -0.5368295847472618,
                        "f0.B": 0.03352486727549409,
                        "f0.X0": 31295.78343744081,
                        "f0.S": 20.771173412218765,
                        "f1.A0": 16.21764568024613,
                    },
                    {
                        "f0.I": 15546.597848457568,
                        "f0.A": 0.6826051993609485,
                        "f0.B": 0.033725313013309145,
                        "f0.X0": 29583.104126366154,
                        "f0.S": 5.310100668502489,
                        "f1.A0": 29.60356380016156,
                    },
                ],
            ),
        ]
    )
    @patch(
        "fitbenchmarking.parsing.mantid_parser.MantidParser._update_mantid_equation"
    )
    def test_get_starting_values(
        self,
        entries,
        is_multistart,
        expected,
        mock_update_mantid_equation,
    ):
        """
        Verifies the _get_starting_values() method with valid values.
        """
        self.parser.fitting_problem = MagicMock()
        self.parser.fitting_problem.multistart = is_multistart
        self.parser._entries = entries
        mock_update_mantid_equation.return_value = None
        assert self.parser._get_starting_values() == expected

    @parameterized.expand(
        [
            (
                {
                    "n_fits": "3",
                    "parameter_means": "f0.I=15000, f0.A=0.04, "
                    "f0.B=0.03, f0.X0=29950, f0.S=12, f1.a0=30",
                    "parameter_sigmas": "f0.I=700, f0.A=0.6, "
                    "f0.B=0.005, f0.X0=600, f0.S=5, f1.A0=20",
                    "function": "name=BackToBackExponential, I={f0.I}, "
                    "A={f0.A}, B={f0.B}, X0={f0.X0}, S={f0.S} ; "
                    "name=FlatBackground, A0={f1.A0}",
                },
            ),
            (
                {
                    "n_fits": "3",
                    "parameter_means": "f0.I=15000, f0.A=0.04, "
                    "f0.B=0.03, f0.X0=29950, f0.S=12, f1.A0=30",
                    "parameter_sigmas": "f0.I=700, f0.A=0.6, "
                    "f0.B=0.005, f0.x0=600, f0.S=5, f1.A0=20",
                    "function": "name=BackToBackExponential, I={f0.I}, "
                    "A={f0.A}, B={f0.B}, X0={f0.X0}, S={f0.S} ; "
                    "name=FlatBackground, A0={f1.A0}",
                },
            ),
        ]
    )
    def test_get_starting_values_raises_error(
        self,
        entries,
    ):
        """
        Verifies the _get_starting_values() method raises a ParsingError.
        """
        self.parser.fitting_problem = MagicMock()
        self.parser.fitting_problem.multistart = True
        self.parser._entries = entries
        with self.assertRaises(exceptions.ParsingError):
            _ = self.parser._get_starting_values()

    @parameterized.expand(
        [
            (
                {
                    "function": "name=FlatBackground, A0={f0.A0};",
                },
                [{"f0.A0": 1.0}, {"f0.A0": 2.0}, {"f0.A0": 3.0}],
                [
                    "name=FlatBackground, A0=1.0;",
                    "name=FlatBackground, A0=2.0;",
                    "name=FlatBackground, A0=3.0;",
                ],
            ),
            (
                {
                    "function": "name=BackToBackExponential, I={f0.I}, "
                    "A={f0.A}, B={f0.B}, X0={f0.X0}, S={f0.S} ;",
                },
                [
                    {
                        "f0.I": 1.0,
                        "f0.A": 2.0,
                        "f0.B": 3.0,
                        "f0.X0": 4.0,
                        "f0.S": 5.0,
                    },
                    {
                        "f0.I": 6.0,
                        "f0.A": 7.0,
                        "f0.B": 8.0,
                        "f0.X0": 9.0,
                        "f0.S": 10.0,
                    },
                ],
                [
                    "name=BackToBackExponential, I=1.0, A=2.0, B=3.0, "
                    "X0=4.0, S=5.0 ;",
                    "name=BackToBackExponential, I=6.0, A=7.0, B=8.0, "
                    "X0=9.0, S=10.0 ;",
                ],
            ),
        ]
    )
    def test_update_mantid_equation(self, entries, starting_values, expected):
        """
        Verifies the output of _update_mantid_equation().
        """
        self.parser._entries = entries
        assert self.parser._update_mantid_equation(starting_values) == expected
