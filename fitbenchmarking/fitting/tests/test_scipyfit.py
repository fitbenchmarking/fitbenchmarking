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

from fitting.scipyfit import nist_func_converter
from fitting.scipyfit import neutron_func_converter
class ScipyfitTests(unittest.TestCase):

    def test_nistFuncConverter_return_appropriate_function_object(self):

        function = "b1*(1-exp(-b2*x))"
        startvals = [['b1', [500.0,250.0]],
                     ['b2', [0.0001,0.0005]]]

        f = nist_func_converter(function, startvals)

    def test_nistFuncConverter_return_appropriate_function_object(self):

        function = ("name=LinearBackground;"
                    "name=BackToBackExponential,"
                    "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")

        f = neutron_func_converter(function)


if __name__ == "__main__":
    unittest.main()
