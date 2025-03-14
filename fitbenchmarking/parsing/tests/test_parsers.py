"""
This file contains tests for the parsers.
"""

import os
from importlib import import_module
from inspect import getmembers, isabstract, isclass
from json import load
from pathlib import Path
from unittest import TestCase

import numpy as np
from parameterized import parameterized
from pytest import test_type as TEST_TYPE
from scipy.sparse import issparse

from conftest import run_for_test_types
from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.parsing.parser_factory import (
    ParserFactory,
    parse_problem_file,
)
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options

OPTIONS = Options()
JACOBIAN_ENABLED_PARSERS = ["cutest", "nist", "hogben"]
SPARSE_JACOBIAN_ENABLED_PARSERS = ["cutest", "hogben", "mantiddev"]
HESSIAN_ENABLED_PARSERS = ["nist"]
BOUNDS_ENABLED_PARSERS = ["cutest", "fitbenchmark"]


def pytest_generate_tests(metafunc):
    """
    Function used by pytest to parametrize tests.
    This will create a set of tests for each function in the class where
    the parameters are given in a 'params' dict in the class.
    """
    # called once per each test function
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    argvals = [
        [funcargs[name] for name in argnames] for funcargs in funcarglist
    ]
    metafunc.parametrize(argnames, argvals)


def form_dict(file_format, evaluations):
    """
    Helper function to form a dict with provided elements.

    :param file_format: The name of the file format
    :type file_format: str
    :param evaluations: Path to the file containing the func/jac evaluations
    :type evaluations: str

    :return: Dictionary with provided elements
    :rtype: dict
    """
    test_dict = {"file_format": file_format, "evaluations_file": evaluations}
    return test_dict


def generate_test_cases():
    """
    Utility function to create the params dict for parametrising the tests.

    :return: params dictionary with a function name as a key, and a list of
             parameter dictionaries for the value
    :rtype: dict
    """
    params = {
        "test_parsers": [],
        "test_factory": [],
        "test_function_evaluation": [],
        "test_jacobian_evaluation": [],
        "test_sparsej_evaluation": [],
        "test_hessian_evaluation": [],
    }

    # get all parsers
    test_dir = os.path.dirname(__file__)
    if TEST_TYPE == "all":
        formats = [
            "cutest",
            "nist",
            "ivp",
            "sasview",
            "hogben",
            "mantiddev",
            "bal",
        ]
    elif TEST_TYPE == "default":
        formats = ["nist"]
    else:
        formats = ["nist", "horace"]

    # create list of test_cases
    expected_dir = os.listdir(os.path.join(test_dir, "expected"))
    for file_format in formats:
        format_dir = os.listdir(os.path.join(test_dir, file_format))
        for expected_file in expected_dir:
            expected_path = os.path.join(test_dir, "expected", expected_file)
            test_name = os.path.splitext(expected_file)[0]
            test_name_with_ext = [
                f for f in format_dir if f.startswith(test_name)
            ]
            if not test_name_with_ext:
                test_file = None
            elif len(test_name_with_ext) == 1:
                test_file = os.path.join(
                    test_dir, file_format, test_name_with_ext[0]
                )
            else:
                raise RuntimeError(
                    f"Too many '{file_format}' files "
                    f"found for '{test_name}' test"
                )

            test_parsers = {}
            test_parsers["file_format"] = file_format
            test_parsers["test_file"] = test_file
            test_parsers["expected"] = load_expectation(expected_path)
            params["test_parsers"].append(test_parsers)

            test_factory = {}
            test_factory["file_format"] = file_format
            test_factory["test_file"] = test_file
            params["test_factory"].append(test_factory)

        func_eval = os.path.join(
            test_dir, file_format, "function_evaluations.json"
        )

        test_func_eval = form_dict(file_format, func_eval)
        params["test_function_evaluation"].append(test_func_eval)

        jac_eval = os.path.join(
            test_dir, file_format, "jacobian_evaluations.json"
        )

        test_jac_eval = form_dict(file_format, jac_eval)
        params["test_jacobian_evaluation"].append(test_jac_eval)

        sparsej_eval = os.path.join(
            test_dir, file_format, "sparse_jacobian_evaluations.json"
        )

        test_sparsej_eval = form_dict(file_format, sparsej_eval)
        params["test_sparsej_evaluation"].append(test_sparsej_eval)

        hes_eval = os.path.join(
            test_dir, file_format, "hessian_evaluations.json"
        )

        test_hes_eval = form_dict(file_format, hes_eval)
        params["test_hessian_evaluation"].append(test_hes_eval)

    return params


def load_expectation(filename):
    """
    Load an expected fitting problem from a json file.

    :param filename: The path to the expectation file
    :type filename: string
    :return: A fitting problem to test against
    :rtype: fitbenchmarking.parsing.FittingProblem
    """
    with open(filename, encoding="utf-8") as f:
        expectation_dict = load(f)

    expectation = FittingProblem(OPTIONS)
    expectation.name = expectation_dict["name"]
    expectation.start_x = expectation_dict["start_x"]
    expectation.end_x = expectation_dict["end_x"]
    expectation.data_x = np.array(expectation_dict["data_x"])
    expectation.data_y = np.array(expectation_dict["data_y"])
    expectation.data_e = expectation_dict["data_e"]
    if expectation.data_e is not None:
        expectation.data_e = np.array(expectation.data_e)
    expectation.starting_values = expectation_dict["starting_values"]
    expectation.value_ranges = expectation_dict["value_ranges"]

    return expectation


class TestParsers:
    """
    A class to hold the tests for parametrized testing of parsers.
    """

    params = generate_test_cases()

    def test_parsers(self, file_format, test_file, expected):
        """
        Test that the parser correctly parses the specified input file.

        :param file_format: The name of the file format
        :type file_format: string
        :param test_file: The path to the test file
        :type test_file: string
        """
        assert test_file is not None, f"No test file for {file_format}"

        with open(test_file, encoding="utf-8") as f:
            if f.readline() == "NA":
                # Test File cannot be written
                return

        # Test import
        module = import_module(
            name=f".{file_format}_parser", package="fitbenchmarking.parsing"
        )

        parser = getmembers(
            module,
            lambda m: (
                isclass(m)
                and not isabstract(m)
                and issubclass(m, Parser)
                and m is not Parser
                and file_format.lower() in str(m.__name__.lower())
            ),
        )[0][1]

        # Test parse
        with parser(test_file, OPTIONS) as p:
            fitting_problem = p.parse()

        # Allow for problems not supporting certain test cases
        # (e.g. value_ranges)
        if fitting_problem.name == "NA":
            return

        # Check against expected
        fitting_problem.verify()

        # functions and equation need to be done seperately as they can't be
        # generic across problem types.
        # similarly starting_values uses the param name so must be checked
        # separately
        for attr in ["name", "data_x", "data_y", "data_e", "start_x", "end_x"]:
            parsed_attr = getattr(fitting_problem, attr)
            expected_attr = getattr(expected, attr)
            equal = parsed_attr == expected_attr
            if isinstance(equal, np.ndarray):
                equal = equal.all()
            assert equal, (
                f"{attr} was parsed incorrectly. "
                f"{parsed_attr} != {expected_attr}"
            )

        # Check starting_values
        for a, e in zip(
            fitting_problem.starting_values, expected.starting_values
        ):
            loaded_as_set = set(a.values())
            expected_as_set = set(e.values())
            assert loaded_as_set == expected_as_set, (
                "starting_values were parsed incorrectly."
            )

        # check value ranges
        if file_format in BOUNDS_ENABLED_PARSERS:
            if fitting_problem.value_ranges is not None:
                act_val = str(fitting_problem.value_ranges)
            else:
                act_val = fitting_problem.value_ranges
            assert act_val == expected.value_ranges, (
                "value_ranges were parsed incorrectly."
            )

        # Check that the function is callable
        assert callable(fitting_problem.function)

        if file_format in JACOBIAN_ENABLED_PARSERS:
            # Check that the Jacobian is callable
            assert callable(fitting_problem.jacobian)

        if file_format in SPARSE_JACOBIAN_ENABLED_PARSERS:
            # Check that the Jacobian is callable
            assert callable(fitting_problem.sparse_jacobian)

        if file_format in HESSIAN_ENABLED_PARSERS:
            # Check that the Jacobian is callable
            assert callable(fitting_problem.hessian)

    def test_function_evaluation(self, file_format, evaluations_file):
        """
        Tests that the function evaluation is consistent with what would be
        expected by comparing to some precomputed values with fixed params and
        x values.

        :param file_format: The name of the file format
        :type file_format: string
        :param evaluations_file: Path to a json file containing tests and
                                 results
                                 in the following format:
                                 {"test_file1": [[x1, params1, results1],
                                                 [x2, params2, results2],
                                                  ...],
                                  "test_file2": ...}
        :type evaluations_file: string
        """

        assert evaluations_file is not None, (
            "No function evaluations provided "
            f"to test against for {file_format}"
        )

        with open(evaluations_file, encoding="utf-8") as ef:
            results = load(ef)

        format_dir = os.path.dirname(evaluations_file)

        for f, tests in results.items():
            f = os.path.join(format_dir, f)

            parser = ParserFactory.create_parser(f)
            with parser(f, OPTIONS) as p:
                fitting_problem = p.parse()

            for r in tests:
                # for problems with too many params to type out individually
                if isinstance(r[1], dict):
                    r[1] = np.ones(r[1]["n_params"]) * r[1]["param_value"]
                    r[2] = np.ones(r[2]["n_data_points"]) * r[2]["func_val"]

                if r[0] == "NA":
                    actual = fitting_problem.eval_model(params=r[1])
                else:
                    x = np.array(r[0])
                    actual = fitting_problem.eval_model(x=x, params=r[1])

                assert np.isclose(actual, r[2]).all(), (
                    f"Expected: {r[2]}\nReceived: {actual}"
                )

    def test_jacobian_evaluation(self, file_format, evaluations_file):
        """
        Tests that the Jacobian evaluation is consistent with what would be
        expected by comparing to some precomputed values with fixed params and
        x values.

        :param file_format: The name of the file format
        :type file_format: string
        :param evaluations_file: Path to a json file containing tests and
                                 results
                                 in the following format:
                                 {"test_file1": [[x1, params1, results1],
                                                 [x2, params2, results2],
                                                  ...],
                                  "test_file2": ...}
        :type evaluations_file: string
        """
        # Note that this test is optional so will only run if the file_format
        # is added to the JACOBIAN_ENABLED_PARSERS list.
        if file_format in JACOBIAN_ENABLED_PARSERS:
            message = (
                "No function evaluations provided "
                f"to test against for {file_format}"
            )
            assert evaluations_file is not None, message

            with open(evaluations_file, encoding="utf-8") as ef:
                results = load(ef)

            format_dir = os.path.dirname(evaluations_file)

            for f, tests in results.items():
                f = os.path.join(format_dir, f)

                parser = ParserFactory.create_parser(f)
                with parser(f, OPTIONS) as p:
                    fitting_problem = p.parse()

                for r in tests:
                    x = np.array(r[0])
                    actual = fitting_problem.jacobian(x, r[1])
                    assert np.isclose(actual, r[2]).all()

    def test_sparsej_evaluation(self, file_format, evaluations_file):
        """
        Test that the sparse Jacobian evaluation is consistent with what
        would be expected by comparing to some precomputed values with
        fixed params and x values.

        :param file_format: The name of the file format
        :type file_format: string
        :param evaluations_file: Path to a json file containing tests and
                                 results
                                 in the following format:
                                 {"test_file1": [[x1, params1, results1],
                                                 [x2, params2, results2],
                                                  ...],
                                  "test_file2": ...}
        :type evaluations_file: string
        """
        # Note that this test is optional so will only run if the file_format
        # is added to the SPARSE_JACOBIAN_ENABLED_PARSERS list.
        if file_format in SPARSE_JACOBIAN_ENABLED_PARSERS:
            message = (
                "No function evaluations provided "
                f"to test against for {file_format}"
            )
            assert evaluations_file is not None, message

            with open(evaluations_file, encoding="utf-8") as ef:
                results = load(ef)

            format_dir = os.path.dirname(evaluations_file)

            for f, tests in results.items():
                f = os.path.join(format_dir, f)

                parser = ParserFactory.create_parser(f)
                with parser(f, OPTIONS) as p:
                    fitting_problem = p.parse()

                for r in tests:
                    x = np.array(r[0])
                    actual = fitting_problem.sparse_jacobian(x, r[1])
                    assert issparse(actual)
                    assert np.isclose(actual.todense(), r[2]).all()

    def test_hessian_evaluation(self, file_format, evaluations_file):
        """
        Tests that the Hessian evaluation is consistent with what would be
        expected by comparing to some precomputed values with fixed params and
        x values.

        :param file_format: The name of the file format
        :type file_format: string
        :param evaluations_file: Path to a json file containing tests and
                                 results
                                 in the following format:
                                 {"test_file1": [[x1, params1, results1],
                                                 [x2, params2, results2],
                                                  ...],
                                  "test_file2": ...}
        :type evaluations_file: string
        """
        # Note that this test is optional so will only run if the file_format
        # is added to the HESSIAN_ENABLED_PARSERS list.
        if file_format in HESSIAN_ENABLED_PARSERS:
            message = (
                "No function evaluations provided "
                f"to test against for {file_format}"
            )
            assert evaluations_file is not None, message

            with open(evaluations_file, encoding="utf-8") as ef:
                results = load(ef)

            format_dir = os.path.dirname(evaluations_file)

            for f, tests in results.items():
                f = os.path.join(format_dir, f)

                parser = ParserFactory.create_parser(f)
                with parser(f, OPTIONS) as p:
                    fitting_problem = p.parse()

                for r in tests:
                    x = np.array(r[0])
                    actual = fitting_problem.hessian(x, r[1])
                    assert np.isclose(actual, r[2]).all()

    def test_factory(self, file_format, test_file):
        """
        Tests that the factory selects the correct parser

        :param file_format: The name of the file format
        :type file_format: string
        :param test_file: The path to the test file
        :type test_file: string
        """
        with open(test_file, encoding="utf-8") as f:
            if f.readline() == "NA":
                # Skip the test files with no data
                return

        parser = ParserFactory.create_parser(test_file)
        assert parser.__name__.lower().startswith(file_format.lower()), (
            f"Factory failed to get associated parser for {test_file}: got "
            f"{parser.__name__.lower()}, required starting with"
            f" {parser.__name__.lower()}"
        )


class TestParserFactory(TestCase):
    """
    A class to hold the tests for the parser factory.
    Note: testing that the parser factory works for all new parsers is left to
          the factory tests in TestParsers
    """

    def test_unknown_parser(self):
        """
        Tests that the parser factory raises a NoParserError when an erroneous
        parser is requested.
        """
        filename = Path.cwd() / "this_is_a_fake_parser.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("this_is_a_fake_parser")

        factory = ParserFactory()
        with self.assertRaises(exceptions.NoParserError):
            _ = factory.create_parser(filename)

        os.remove(filename)

    def test_parse_problem_file(self):
        """
        Tests the parse_problem_file method
        """
        filename = Path(__file__).parent / "nist" / "basic.dat"
        fitting_problem = parse_problem_file(filename, OPTIONS)
        self.assertEqual(fitting_problem.name, "basic")


class TestParserNoJac(TestCase):
    """
    A class to hold the tests for cases where the user does not provide
    a jacobian function
    """

    def setUp(self):
        """
        Set up the tests.
        """
        self.test_dir = Path(__file__).parent

    @parameterized.expand(["simplified_anac.txt", "simplified_anac2.txt"])
    def test_sparsej_returns_none(self, filename):
        """
        Test sparse_jacobian is None in two cases:
         - when no 'jac' line in prob def file
         - when there is a 'jac' line but no 'sparse_func' in it.
        """
        prob_def_file_path = self.test_dir / "ivp" / filename

        parser = ParserFactory.create_parser(prob_def_file_path)
        with parser(prob_def_file_path, OPTIONS) as p:
            fitting_problem = p.parse()

        assert fitting_problem.sparse_jacobian is None

    @run_for_test_types(TEST_TYPE, "all")
    def test_mantid_jac_when_no_func_by_user(self):
        """
        Tests that, for mantid problems, when no jacobian is provided
        by the user, the jacobian function from mantid is used.
        """
        format_dir = "mantiddev"
        file_path = self.test_dir / format_dir / "jacobian_evaluations.json"

        with open(file_path, encoding="utf-8") as ef:
            results = load(ef)

            for f, tests in results.items():
                f = os.path.join(self.test_dir, format_dir, f)

                parser = ParserFactory.create_parser(f)
                with parser(f, OPTIONS) as p:
                    fitting_problem = p.parse()

                for r in tests:
                    x = np.array(r[0])

                    actual = fitting_problem.jacobian(x, r[1])
                    assert np.isclose(actual, r[2]).all()
