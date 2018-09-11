from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from fitting.misc import compute_chisq


class FitMiscTests(unittest.TestCase):

    def test_compute_chisq(self):

        differences = np.array([1,2,3])

        chi_sq = compute_chisq(differences)
        chi_sq_expected = 14

        self.assertEqual(chi_sq_expected, chi_sq)


if __name__ == "__main__":
    unittest.main()
