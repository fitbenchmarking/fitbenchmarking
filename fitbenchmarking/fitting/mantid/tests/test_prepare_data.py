"""
Mantid data preparation testing
"""
from __future__ import (absolute_import, division, print_function)

import unittest
import numpy as np
import mantid.simpleapi as msapi

from fitbenchmarking.fitting.mantid.prepare_data import wks_cost_function
from fitbenchmarking.fitting.mantid.prepare_data import setup_errors
from fitbenchmarking.fitting.mantid.tests.test_main import nist_problem
from fitbenchmarking.fitting.mantid.tests.test_func_def import (
    create_wks_nist_problem_with_errors,
    create_wks_nist_problem_without_errors)


class MantidTests(unittest.TestCase):
    """
    Implements Mantid data preparation Tests
    """
    def test_wks_cost_function_return_with_errors(self):
        """
        Tests that the workspace cost function returns correctly when errors
        are present
        """
        prob = nist_problem()
        use_errors = True

        wks, cost_function = wks_cost_function(prob, use_errors)
        wks_expected = create_wks_nist_problem_with_errors()
        cost_function_expected = 'Least squares'

        self.assertEqual(cost_function_expected, cost_function)
        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertNotEqual(None, messages)
        self.assertTrue(result)

    def test_wks_cost_function_return_without_errors(self):
        """
        Tests that the workspace cost function returns correctly when errors
        are not present
        """
        prob = nist_problem()
        use_errors = False

        wks, cost_function = wks_cost_function(prob, use_errors)
        wks_expected = create_wks_nist_problem_without_errors()
        cost_function_expected = 'Unweighted least squares'

        self.assertEqual(cost_function_expected, cost_function)
        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertNotEqual(None, messages)
        self.assertTrue(result)

    def test_setup_errors_errors(self):
        """
        Tests the problem setup when errors are present
        """
        prob = nist_problem()
        prob.data_e = [1, 2, 3]

        errors = setup_errors(prob)
        errors_expected = [1, 2, 3]

        self.assertListEqual(errors_expected, errors)


def test_setup_errors_no_errors():
    """
    Tests the problem setup when no errors are present
    """
    prob = nist_problem()

    errors = setup_errors(prob)
    errors_expected = np.sqrt(abs(prob.data_y))

    np.testing.assert_allclose(errors_expected, errors)

if __name__ == "__main__":
    unittest.main()
