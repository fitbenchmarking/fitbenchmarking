"""
This file contains tests for the LSQfitParser class.

It covers the lsqfit-specific behaviour not exercised by the shared
test_parsers framework:
  - _parse_covariance: deriving the covariance file path from the data file
    path and loading it, or returning None when no file is found.
  - _set_additional_info: storing the covariance matrix in
    fitting_problem.additional_info['covariance'].

Integration tests for parsing, function evaluation, and factory routing
are in test_parsers.py (fixtures in parsing/tests/lsqfit/).
"""

from unittest import TestCase
from unittest.mock import MagicMock, patch

import numpy as np
from parameterized import parameterized

from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.parsing.lsqfit_parser import LSQfitParser
from fitbenchmarking.utils.options import Options


class TestLSQfitParser(TestCase):
    """
    Tests the LSQfitParser class.
    """

    @patch.object(LSQfitParser, "__init__", lambda a, b, c: None)
    def setUp(self):
        """
        Set up resources before each test case.
        """
        self.parser = LSQfitParser("test_file.txt", Options())
        self.parser._filename = "test_file.txt"
        self.parser.fitting_problem = FittingProblem(Options())

    @parameterized.expand(
        [
            ("problem.dat", "problem_cov.txt"),
            ("data_files/ASB1M4_av.dat", "data_files/ASB1M4_av_cov.txt"),
        ]
    )
    @patch("fitbenchmarking.parsing.lsqfit_parser.np.loadtxt")
    @patch("fitbenchmarking.parsing.lsqfit_parser.os.path.exists")
    def test_parse_covariance_returns_array_when_file_exists(
        self, data_file, expected_cov_file, mock_exists, mock_loadtxt
    ):
        """
        Verifies the output of _parse_covariance() when the cov file exists.
        """
        mock_exists.return_value = True
        mock_loadtxt.return_value = np.eye(3)

        result = self.parser._parse_covariance(data_file)

        mock_exists.assert_called_once_with(expected_cov_file)
        mock_loadtxt.assert_called_once_with(expected_cov_file)
        np.testing.assert_array_equal(result, np.eye(3))

    @patch("fitbenchmarking.parsing.lsqfit_parser.os.path.exists")
    def test_parse_covariance_returns_none_when_file_missing(
        self, mock_exists
    ):
        """
        Verifies _parse_covariance() returns None when no cov file is found.
        """
        mock_exists.return_value = False
        result = self.parser._parse_covariance("data_files/test.dat")
        self.assertIsNone(result)

    @patch(
        "fitbenchmarking.parsing.lsqfit_parser.LSQfitParser._parse_covariance"
    )
    @patch(
        "fitbenchmarking.parsing.fitbenchmark_parser.FitbenchmarkParser"
        "._set_additional_info"
    )
    def test_set_additional_info_stores_covariance(
        self, mock_parent_set_additional_info, mock_parse_cov
    ):
        """
        Verifies _set_additional_info() stores the covariance matrix in
        additional_info when a cov file is found.
        """
        expected_cov = np.eye(3)
        mock_parse_cov.return_value = expected_cov
        self.parser._get_data_file = MagicMock(
            return_value=["data_files/test.dat"]
        )

        self.parser._set_additional_info()

        mock_parent_set_additional_info.assert_called_once()
        np.testing.assert_array_equal(
            self.parser.fitting_problem.additional_info["covariance"],
            expected_cov,
        )

    @patch(
        "fitbenchmarking.parsing.lsqfit_parser.LSQfitParser._parse_covariance"
    )
    @patch(
        "fitbenchmarking.parsing.fitbenchmark_parser.FitbenchmarkParser"
        "._set_additional_info"
    )
    def test_set_additional_info_no_covariance_when_none_returned(
        self, mock_parent_set_additional_info, mock_parse_cov
    ):
        """
        Verifies _set_additional_info() does not set 'covariance' in
        additional_info when no cov file is found.
        """
        mock_parse_cov.return_value = None
        self.parser._get_data_file = MagicMock(
            return_value=["data_files/test.dat"]
        )

        self.parser._set_additional_info()

        self.assertNotIn(
            "covariance", self.parser.fitting_problem.additional_info
        )
