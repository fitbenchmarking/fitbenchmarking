"""
This file calls the pycutest interface for SIF data
"""

from __future__ import print_function

import numpy as np
import os
import pycutest

from collections import OrderedDict
from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.logging_setup import logger

class FitbenchmarkParser(Parser):
    """
    Use the pycutest interface to parse SIF files
    """
    
    def parse(self):
        """ 
        Get data into a Fitting Problem via cutest.
        
        :return: The fully parsed fitting problem
        :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
        
        """
        self._n = None
        self._m = None
        
        problem_ext = os.path.basename(self._filename)
        problem_directory = os.path.dirname(self._filename)
        problem, _ = os.path.splitext(problem_ext)
        
        # get just the short filename (minus the .SIF)
        fp = FittingProblem()

        # load the problem from the sif file
        # set the MASTSIF environment variable so that pycutest
        # can find the sif files
        os.environ["MASTSIF"] = problem_directory
        self._p = pycutest.import_problem(problem)

        fp.name = problem
        fp.data_x, fp.data_y = self._get_data()
        self._y = fp.data_y
        fp.function = self._function # self._p.obj
        fp.equation = None
        fp.starting_values = self._get_starting_values()
        fp.start_x = None
        fp.end_x = None

        return fp

    def _function(self, x, *params):

        _, fx = self._p.objcons(np.asarray(params))
        fx = fx + self._y

        return fx

    def _get_starting_values(self):

        starting_values = [
            OrderedDict([
                ('f{}'.format(i), self._p.x0[i])
                for i in range(self._n)
            ])
        ]

        return starting_values
        
    
    def _get_data(self):
        """
        Parses CUTEst SIF files to extract data points
        
        :returns: data_x, data_y
        :rtype: lists of floats
        """

        lines = self.file.readlines()
        idx, ignored_lines, x_idx, y_idx = 0, 0, 0, 0

        while idx < len(lines):
            line = lines[idx].strip()
            idx += 1

            if not line:
                continue

            if "IE M" in line:
                self._m = int(line.split()[2])
                # this will always come before x/y data
                # so allocate space for these now
                data_x = np.zeros(self._m)
                data_y = np.zeros(self._m)
                # initialize index parameters for x and y
            
            if "IE N" in line:
                self._n = int(line.split()[2])

            if "RE X" in line:
                data_x[x_idx] = float(line.split()[2])
                x_idx += 1

            if "RE Y" in line:
                data_y[y_idx] = float(line.split()[2])
                y_idx += 1

        # check the data is right
        # TODO: turn into an exception
        if x_idx != self._m:
            print("wrong number of x data points")
            print(" got {}, expected {}".format(x_idx,self._m))
        if y_idx != self._m:
            print("wrong number of y data points")
            print(" got {}, expected {}".format(y_idx,self._m))

        return data_x, data_y
            
    
