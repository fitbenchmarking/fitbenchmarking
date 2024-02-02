"""
Test that accuracy of FitBenchmarking is consistent with previous versions
"""

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

import os
from sys import platform
from tempfile import NamedTemporaryFile
from unittest import TestCase
from pytest import test_type as TEST_TYPE  # pylint: disable=no-name-in-module
from conftest import run_for_test_types

from fitbenchmarking.cli.main import run
from fitbenchmarking.utils.options import Options


@run_for_test_types(TEST_TYPE, 'all')
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
        cls.results_dir = os.path.join(os.path.dirname(__file__),
                                       "fitbenchmarking_results")

    def test_results_consistent_all(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """
        problem_sub_directory = "all_parsers_set"

        run_benchmark(self.results_dir, problem_sub_directory)

        diff, msg = compare_results(problem_sub_directory, "all_parsers.csv")
        self.assertListEqual([], diff, msg)

    def test_multifit_consistent(self):
        """
        Regression testing that the results of fitting multifit problems
        against a single minimizer from mantid.
        """
        problem_sub_directory = "multifit_set"

        run_benchmark(self.results_dir, problem_sub_directory,
                      override_software=["mantid"],
                      jac_num_method={"scipy": ["2-point", "3-point"]})

        diff, msg = compare_results(problem_sub_directory, "multifit.csv")
        self.assertListEqual([], diff, msg)


@run_for_test_types(TEST_TYPE, 'matlab')
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
        cls.results_dir = os.path.join(os.path.dirname(__file__),
                                       'fitbenchmarking_results')

    def test_results_consistent_all(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """
        problem_sub_directory = "all_parsers_set"

        run_benchmark(self.results_dir, problem_sub_directory)

        diff, msg = compare_results(problem_sub_directory, "matlab.csv")
        self.assertListEqual([], diff, msg)


@run_for_test_types(TEST_TYPE, 'default')
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
        cls.results_dir = os.path.join(os.path.dirname(__file__),
                                       'fitbenchmarking_results')

    def test_results_consistent(self):
        """
        Regression testing that the results of fitting a set of problems
        containing all problem types against a single minimizer from each of
        the supported softwares
        """
        problem_sub_directory = "default_parsers_set"

        run_benchmark(self.results_dir, problem_sub_directory)

        diff, msg = compare_results(problem_sub_directory,
                                    "default_parsers_set.csv")
        self.assertListEqual([], diff, msg)


def diff_result(actual, expected):
    """
    Return the lines which differ between expected and actual along with a
    formatted message.

    :param expected: The expected result
    :type expected: list of strings
    :param actual: The actual result
    :type actual: list of strings
    :return: The lines which differ and a formatted message
    :rtype: list[list[str]], str
    """
    diff = []
    for i, (exp_line, act_line) in enumerate(
            zip_longest(expected, actual)):
        exp_line = '' if exp_line is None else exp_line.strip('\n')
        act_line = '' if act_line is None else act_line.strip('\n')
        if exp_line != act_line:
            diff.append([i, exp_line, act_line])

    msg = f'\n\nOutput has changed in {len(diff)} ' \
          + 'minimizer-problem pairs. \n' \
          + '\n'.join([f'== Line {line_change[0]} ==\n'
                       f'Expected :{line_change[1]}\n'
                       f'Actual   :{line_change[2]}'
                       for line_change in diff])
    if diff != []:
        print("\n==\n")
        print("Output generated (also saved as actual.out):")
        with open("actual.out", "w", encoding='utf-8') as outfile:
            for line in actual:
                print(line)
                outfile.write(line)
    return diff, msg


def compare_results(problem_sub_directory: str, result_filename: str) -> list:
    """
    Compares the expected benchmark results with the actual results,
    and returns the lines which differ between expected and actual
    along with a formatted message.

    :param problem_sub_directory: The directory containing problems.
    :type problem_sub_directory: str
    :param result_filename: The name of the actual result file.
    :type result_filename: str
    :return: The lines which differ and a formatted message
    :rtype: list[list[str]], str
    """
    expected_file = os.path.join(os.path.dirname(__file__),
                                 f'{platform}_expected_results',
                                 result_filename)

    actual_file = os.path.join(os.path.dirname(__file__),
                               'fitbenchmarking_results',
                               problem_sub_directory,
                               'acc_table.csv')

    with open(expected_file, 'r', encoding='utf-8') as f:
        expected = f.readlines()

    with open(actual_file, 'r', encoding='utf-8') as f:
        actual = f.readlines()

    return diff_result(actual, expected)


def setup_options(override_software: list = None,
                  jac_num_method: dict = None) -> Options:
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
    opts.table_type = ['acc', 'runtime', 'compare', 'local_min']

    # The software to test for the different test types.
    # - 'dfo' and 'minuit' are included but are unstable for other datasets.
    # - 'gradient_free' and 'scipy_go' are left out as they require bounds.
    software = {"all": ["bumps", "dfo", "ceres", "gofit", "gsl", "levmar",
                        "lmfit", "mantid", "minuit", "nlopt", "ralfit",
                        "scipy", "scipy_ls", "theseus"],
                "default": ["bumps", "scipy", "scipy_ls"],
                "matlab": ["horace", "matlab", "matlab_curve", "matlab_opt",
                           "matlab_stats"]}

    # The minimizers to test for each software
    minimizers = {"bumps": "lm-bumps",
                  "dfo": "dfols",
                  "ceres": "Levenberg_Marquardt",
                  "gofit": "regularisation",
                  "gsl": "lmsder",
                  "horace": "lm-lsqr",
                  "levmar": "levmar",
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
                  "theseus": "Levenberg_Marquardt"}

    opts.software = software.get(TEST_TYPE) if override_software is None \
        else override_software
    opts.minimizers = {s: [minimizers[s]] for s in opts.software}
    if jac_num_method is not None:
        opts.jac_num_method = jac_num_method
    return opts


def create_options_file(override_software: list = None,
                        jac_num_method: dict = None):
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
    with NamedTemporaryFile(suffix='.ini', mode='w',
                            delete=False) as opt_file:
        opts.write_to_stream(opt_file)
        name = opt_file.name
    return name


def run_benchmark(results_dir: str, problem_sub_directory: str,
                  override_software: list = None,
                  jac_num_method: dict = None) -> None:
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
    problem = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir,
                                           "test_files",
                                           problem_sub_directory))
    run([problem], additional_options={'results_dir': results_dir},
        options_file=opt_file_name,
        debug=True)
    os.remove(opt_file_name)
