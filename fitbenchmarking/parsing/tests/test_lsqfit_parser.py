"""
This file contains tests for the LsqfitParser class.

It covers the lsqfit-specific behaviour not exercised by the shared
test_parsers framework:
  - _parse_covariance: loading the covariance file whose path is given by
    the ``covariance_file`` entry in the problem definition file, or returning
    None when the entry is absent.
  - _set_additional_info: storing the covariance matrix in
    fitting_problem.additional_info['covariance'].

Integration tests for parsing, function evaluation, and factory routing
are in test_parsers.py (fixtures in parsing/tests/lsqfit/).
"""

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

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
            ("data_files/cov.txt",),
            ("../shared/ASB1M4_av_cov.txt",),
        ]
    )
    @patch("fitbenchmarking.parsing.lsqfit_parser.np.loadtxt")
    def test_parse_covariance_returns_array_when_entry_present(
        self, cov_entry, mock_loadtxt
    ):
        """
        Test that _parse_covariance loads and returns the array from the path
        given by the covariance_file entry, resolved relative to the problem
        definition file's directory.
        """
        mock_loadtxt.return_value = np.eye(3)
        self.parser._entries = {"covariance_file": cov_entry}

        result = self.parser._parse_covariance()

        expected_path = Path("test_file.txt").parent / cov_entry
        mock_loadtxt.assert_called_once_with(expected_path)
        np.testing.assert_array_equal(result, np.eye(3))

    def test_parse_covariance_returns_none_when_entry_absent(self):
        """
        Test that _parse_covariance returns None when covariance_file is not
        in the problem definition.
        """
        self.parser._entries = {}
        result = self.parser._parse_covariance()
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
        Test that _set_additional_info stores the covariance matrix when
        _parse_covariance returns an array.
        """
        expected_cov = np.eye(3)
        mock_parse_cov.return_value = expected_cov

        self.parser._set_additional_info()

        mock_parent_set_additional_info.assert_called_once()
        mock_parse_cov.assert_called_once_with()
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
        Test that _set_additional_info does not set 'covariance' when
        _parse_covariance returns None.
        """
        mock_parse_cov.return_value = None

        self.parser._set_additional_info()

        self.assertNotIn(
            "covariance", self.parser.fitting_problem.additional_info
        )
