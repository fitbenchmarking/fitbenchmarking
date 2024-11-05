"""
Tests for debug.py
"""

import unittest

from fitbenchmarking.utils.debug import get_printable_table


class GetPrintableTableTests(unittest.TestCase):
    """
    Tests for the get_printable_table utility function.
    """

    def setUp(self):
        """
        Create some class data for testing.
        """
        self.class_name = "FakeClassName"
        self.class_info = {
            "IntAttribute": 1,
            "FloatAttribute": 2.0,
            "StringAttribute": "A string",
            "BoolAttribute": True,
            "TupleAttribute": (3, 4),
        }

    def test_getProblemFiles_get_correct_probs(self):
        """
        Test that the correct files are found
        """
        printable_str = get_printable_table(self.class_name, self.class_info)

        self.assertEqual(
            str(printable_str),
            "+============================+\n"
            "| FakeClassName              |\n"
            "+============================+\n"
            "| IntAttribute    | 1        |\n"
            "+----------------------------+\n"
            "| FloatAttribute  | 2.0      |\n"
            "+----------------------------+\n"
            "| StringAttribute | A string |\n"
            "+----------------------------+\n"
            "| BoolAttribute   | True     |\n"
            "+----------------------------+\n"
            "| TupleAttribute  | (3, 4)   |\n"
            "+----------------------------+",
        )


if __name__ == "__main__":
    unittest.main()
