"""
Test the DASH section for the options file
"""

import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from fitbenchmarking.core.results_output import prepare_dash_app_and_run
from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.tests.test_options_fitting import (
    BaseFittingOptionTests,
)


class DashOptionsTests(unittest.TestCase):
    """
    Checks Dash options in the options file are set correctly
    """

    def setUp(self):
        """
        Create an options file and store input
        """
        config_str = """
            [DASH]
            port: 3000
            ip_address: 127.0.0.3
        """

        self.options_file = Path("test_options_tests.ini")
        with open(self.options_file, "w", encoding="utf-8") as f:
            f.write(config_str)

        self.options = Options(self.options_file)

        example_data = {"minim1": [0, 1, 2, 3], "minim2": [0, 1, 2, 3]}
        example_df = pd.DataFrame(data=example_data, index=[0, 1, 2, 3])

        self.pp_df = {
            "example_prob": {
                "acc": example_df,
                "runtime": example_df,
                "energy_usage": example_df,
            }
        }

    @patch(
        "fitbenchmarking.core.results_output.run_dash_app",
    )
    def test_run_dash_called_with_correct_port_and_ip(self, mock_run_dash):
        """ """

        expected_port = self.options.port
        expected_address = self.options.ip_address
        prepare_dash_app_and_run(self.options, self.pp_df)

        args = mock_run_dash.call_args[1]
        self.assertEqual(args["host"], expected_address)
        self.assertEqual(args["port"], expected_port)

    def test_dash_default(self):
        """
        Checks dash default options
        """
        default_options = Options()
        expected_port = 4000
        expected_ip = "127.0.0.1"

        actual_port = default_options.port
        actual_ip = default_options.ip_address

        self.assertEqual(expected_port, actual_port)
        self.assertEqual(expected_ip, actual_ip)


class UserDashOptionTests(BaseFittingOptionTests):
    """
    Checks the Dash in the options file are set correctly or raise errors
    """

    def test_dash_port_option_valid(self):
        """
        Checks user set dash port is valid
        """
        set_option = 3000
        config_str = """
        [DASH]
        port: 3000
        """
        self.shared_valid("port", set_option, config_str)

    def test_dash_port_option_invalid(self):
        """
        Checks user set dash port is invalid
        """
        config_str = """
        [DASH]
        port: 127.0.0.1
        """
        self.shared_invalid("port", config_str)

    def test_dash_ip_option_valid(self):
        """
        Checks user set dash ip_address is valid
        """
        set_option = "127.0.0.3"
        config_str = """
        [DASH]
        ip_address: 127.0.0.3
        """
        self.shared_valid("ip_address", set_option, config_str)
