"""Tests for user-facing exception messages."""

from unittest import TestCase

from fitbenchmarking.utils.exceptions import (
    CostFuncError,
    NoResultsError,
    UnsupportedMinimizerError,
)


class TestExceptionMessages(TestCase):
    """Exceptions should identify the failure without losing its details."""

    cases = (
        (
            UnsupportedMinimizerError,
            "FitBenchmarking encountered an unsupported or unconfigured "
            "minimizer",
            15,
        ),
        (
            CostFuncError,
            "FitBenchmarking encountered an error with the cost function",
            16,
        ),
        (NoResultsError, "FitBenchmarking ran with no results", 14),
    )

    def test_default_messages(self):
        """Report the specific error when no extra details are supplied."""
        for error_type, message, code in self.cases:
            with self.subTest(error_type=error_type):
                error = error_type()
                self.assertEqual(str(error), message)
                self.assertEqual(error.error_code, code)

    def test_messages_include_details(self):
        """Keep caller-supplied details after the specific error message."""
        for error_type, message, _ in self.cases:
            with self.subTest(error_type=error_type):
                error = error_type("example failure")
                self.assertEqual(
                    str(error), f"{message}\nDetails: example failure"
                )
