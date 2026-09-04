"""
Test that accuracy of FitBenchmarking is consistent with previous versions
"""

import csv
import os
import re
from sys import platform
from tempfile import NamedTemporaryFile
from unittest import TestCase

import numpy as np
from pytest import test_type as TEST_TYPE

from conftest import run_for_test_types
from fitbenchmarking.cli.main import run
from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.test_utils import compare_files

# Relative tolerance used when comparing expected and actual results.
# Minimizers are not reproducible to the last digit across platforms,
# library versions and CPUs, and the normalised value in brackets
# amplifies this because a tiny change in which minimizer was the
# best for a problem rescales the whole row. Only differences larger
# than RELATIVE_TOLERANCE are treated as a regression.
RELATIVE_TOLERANCE = 1e-3

# Matches a value in a results table, e.g. '11.97 (1.001)[2]', capturing
# the absolute value, the normalised value and the error flag.
TABLE_VALUE_RE = re.compile(
    r"^\s*(?P<abs>[^\s(]+)\s*\((?P<rel>[^)]+)\)\s*(?P<flag>\[\d+\])?\s*$"
)


@run_for_test_types(TEST_TYPE, "all")
class TestRegressionAll(TestCase):
    """
    Regression tests for the Fitbenchmarking software with all fitting software
    packages
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """
        cls.results_dir = os.path.join(
            os.path.dirname(__file__), "fitbenchmarking_results"
        )

    def test_results_consistent_all(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """
        problem_sub_directory = "all_parsers_set"

        run_benchmark(self.results_dir, problem_sub_directory)
        compare_results(self, problem_sub_directory, "all_parsers.csv")


@run_for_test_types(TEST_TYPE, "mantid")
class TestRegressionMantid(TestCase):
    """
    Regression tests for the Fitbenchmarking software with
    mantid fitting software
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """
        cls.results_dir = os.path.join(
            os.path.dirname(__file__), "fitbenchmarking_results"
        )

    def test_results_consistent_mantid(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """
        problem_sub_directory = "mantid_set"

        run_benchmark(self.results_dir, problem_sub_directory)
        compare_results(self, problem_sub_directory, "mantid.csv")

    def test_multifit_consistent(self):
        """
        Regression testing that the results of fitting multifit problems
        against a single minimizer from mantid.
        """
        problem_sub_directory = "multifit_set"

        run_benchmark(
            self.results_dir,
            problem_sub_directory,
        )
        compare_results(self, problem_sub_directory, "multifit.csv")


@run_for_test_types(TEST_TYPE, "local_only")
class TestRegressionLocal(TestCase):
    """
    Regression tests for the Fitbenchmarking software with
    matlab fitting software
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """
        cls.results_dir = os.path.join(
            os.path.dirname(__file__), "fitbenchmarking_results"
        )

    def test_results_consistent_all(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """
        problem_sub_directory = "local_only_set"

        run_benchmark(self.results_dir, problem_sub_directory)
        compare_results(self, problem_sub_directory, "local_only_set.csv")


@run_for_test_types(TEST_TYPE, "matlab")
class TestRegressionMatlab(TestCase):
    """
    Regression tests for the Fitbenchmarking software with
    matlab fitting software
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """
        cls.results_dir = os.path.join(
            os.path.dirname(__file__), "fitbenchmarking_results"
        )

    def test_results_consistent_all(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """
        problem_sub_directory = "all_parsers_set"

        run_benchmark(self.results_dir, problem_sub_directory)
        compare_results(self, problem_sub_directory, "matlab.csv")


@run_for_test_types(TEST_TYPE, "default")
class TestRegressionDefault(TestCase):
    """
    Regression tests for the Fitbenchmarking software with all default fitting
    software packages
    """

    @classmethod
    def setUpClass(cls):
        """
        Create an options file, run it, and get the results.
        """
        cls.results_dir = os.path.join(
            os.path.dirname(__file__), "fitbenchmarking_results"
        )

    def test_results_consistent(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """
        problem_sub_directory = "default_parsers_set"

        run_benchmark(self.results_dir, problem_sub_directory)
        compare_results(self, problem_sub_directory, "default_parsers_set.csv")


def values_match(expected: str, actual: str) -> bool:
    """
    Compare a single cell of the results table. Cells which hold a number,
    such as '11.97 (1.001)[2]', match when both the absolute and the
    normalised value are within RELATIVE_TOLERANCE of the expected ones and
    the error flag is identical. Anything else, e.g. a problem name or
    'N/A', must match exactly.

    :param expected: The expected cell
    :type expected: str
    :param actual: The actual cell
    :type actual: str
    :return: True if the cells match
    :rtype: bool
    """
    if expected == actual:
        return True

    exp_value = TABLE_VALUE_RE.match(expected)
    act_value = TABLE_VALUE_RE.match(actual)
    if exp_value is None or act_value is None:
        return False

    # The error flag records how the fit ended, so it must not change.
    if exp_value["flag"] != act_value["flag"]:
        return False

    for group in ("abs", "rel"):
        try:
            exp_num = float(exp_value[group])
            act_num = float(act_value[group])
        except ValueError:
            return False
        if not np.isclose(
            act_num, exp_num, rtol=RELATIVE_TOLERANCE, equal_nan=True
        ):
            return False

    return True


def lines_match(expected: str, actual: str) -> bool:
    """
    Compare a row of the results table cell by cell, allowing the numbers
    to differ by up to RELATIVE_TOLERANCE.

    :param expected: The expected row
    :type expected: str
    :param actual: The actual row
    :type actual: str
    :return: True if the rows match
    :rtype: bool
    """
    expected = expected.rstrip("\r\n")
    actual = actual.rstrip("\r\n")
    if expected == actual:
        return True

    exp_cells = next(csv.reader([expected]), [])
    act_cells = next(csv.reader([actual]), [])
    if len(exp_cells) != len(act_cells):
        return False

    return all(
        values_match(exp, act) for exp, act in zip(exp_cells, act_cells)
    )


def compare_results(
    test_case: TestCase, problem_sub_directory: str, result_filename: str
) -> None:
    """
    Compares the expected benchmark results with the actual results
    using compare_files from test_utils.

    :param problem_sub_directory: The directory containing problems.
    :type problem_sub_directory: str
    :param result_filename: The name of the actual result file.
    :type result_filename: str
    :return: The lines which differ and a formatted message
    :rtype: list[list[str]], str
    """
    expected_file = os.path.join(
        os.path.dirname(__file__),
        f"{platform}_expected_results",
        result_filename,
    )

    actual_file = os.path.join(
        os.path.dirname(__file__),
        "fitbenchmarking_results",
        problem_sub_directory,
        "acc_table.csv",
    )

    with open(actual_file, encoding="utf-8") as f:
        actual_output = f.read()

    compare_files(test_case, expected_file, actual_output, eq=lines_match)


def setup_options(
    override_software: list | None = None,
    jac_num_method: dict | None = None,
) -> Options:
    """
    Setups up options class for system tests

    :param override_software: The software to use instead of the
    software determined by the test type.
    :type override_software: list of strings
    :param jac_num_method: The jacobian methods to use when fitting.
    :type jac_num_method: dict{str: list[str]}

    :return: Fitbenchmarking options file for tests
    :rtype: fitbenchmarking.utils.options.Options
    """
    opts = Options()
    opts.num_runs = 1
    opts.make_plots = False
    opts.run_dash = False
    opts.table_type = ["acc", "runtime", "compare", "local_min"]

    # The software to test for the different test types.
    # - 'dfo' and 'minuit' are included but are unstable for other datasets.
    # - 'gradient_free' and 'scipy_go' are left out as they require bounds.
    software = {
        "all": [
            "bumps",
            "dfo",
            "ceres",
            "galahad",
            "gofit",
            "gsl",
            "lmfit",
            "minuit",
            "nlopt",
            "ralfit",
            "scipy",
            "scipy_ls",
            "scipy_leastsq",
            "theseus",
        ],
        "default": ["bumps", "scipy", "scipy_ls"],
        "matlab": [
            "horace",
            "matlab",
            "matlab_curve",
            "matlab_opt",
            "matlab_stats",
        ],
        "mantid": [
            "mantid",
            "bumps",
            "dfo",
            "lmfit",
            "minuit",
            "nlopt",
            "scipy",
            "scipy_ls",
            "scipy_leastsq",
        ],
        "local_only": [
            "bumps",
            "dfo",
            "ceres",
            "gofit",
            "gsl",
            "lmfit",
            "minuit",
            "nlopt",
            "scipy",
            "scipy_ls",
            "scipy_leastsq",
        ],
    }

    # The minimizers to test for each software
    minimizers = {
        "bumps": "lm-bumps",
        "dfo": "dfols",
        "ceres": "Levenberg_Marquardt",
        "galahad": "arc",
        "gofit": "regularisation",
        "gsl": "lmsder",
        "horace": "lm-lsqr",
        "lmfit": "least_squares",
        "mantid": "Levenberg-Marquardt",
        "matlab": "Nelder-Mead Simplex",
        "matlab_curve": "Levenberg-Marquardt",
        "matlab_opt": "levenberg-marquardt",
        "matlab_stats": "Levenberg-Marquardt",
        "minuit": "migrad",
        "nlopt": "LD_VAR1",
        "ralfit": "gn",
        "scipy": "Nelder-Mead",
        "scipy_ls": "lm-scipy",
        "scipy_leastsq": "lm-leastsq",
        "theseus": "Levenberg_Marquardt",
    }

    opts.software = (
        software.get(TEST_TYPE)
        if override_software is None
        else override_software
    )
    opts.minimizers = {s: [minimizers[s]] for s in opts.software}
    if jac_num_method is not None:
        opts.jac_num_method = jac_num_method
    return opts


def create_options_file(
    override_software: list | None = None,
    jac_num_method: dict | None = None,
):
    """
    Creates a temporary options file and returns its name.

    :param override_software: The software to use instead of the
    software determined by the test type.
    :type override_software: list of strings
    :param jac_num_method: The jacobian methods to use when fitting.
    :type jac_num_method: dict{str: list[str]}
    :return: Name of the temporary options file.
    :rtype: str
    """
    opts = setup_options(override_software, jac_num_method)
    with NamedTemporaryFile(suffix=".ini", mode="w", delete=False) as opt_file:
        opts.write_to_stream(opt_file)
        name = opt_file.name
    return name


def run_benchmark(
    results_dir: str,
    problem_sub_directory: str,
    override_software: list | None = None,
    jac_num_method: dict | None = None,
    additional_options: dict | None = None,
) -> None:
    """
    Runs a benchmark of the problems in a specific directory
    and places them in the results directory.

    :param results_dir: The directory to place the results in.
    :type results_dir: str
    :param problem_sub_directory: The directory containing problems.
    :type problem_sub_directory: str
    :param override_software: The software to use instead of the
    software determined by the test type.
    :type override_software: list[str]
    :param jac_num_method: The jacobian methods to use when fitting.
    :type jac_num_method: dict{str: list[str]}
    """
    opt_file_name = create_options_file(override_software, jac_num_method)
    problem = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "test_files",
            problem_sub_directory,
        )
    )

    add_opts = {"results_dir": results_dir}
    if additional_options is not None:
        add_opts.update(additional_options)

    run(
        [problem],
        additional_options=add_opts,
        options_file=opt_file_name,
        debug=True,
    )
    os.remove(opt_file_name)
