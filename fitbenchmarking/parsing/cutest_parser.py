"""
This file calls the pycutest interface for SIF data
"""

from __future__ import print_function

import numpy as np
import os
import pycutest
import shutil
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

from collections import OrderedDict
from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.logging_setup import logger


class CutestParser(Parser):
    """
    Use the pycutest interface to parse SIF files
    """

    def parse(self):
        """
        Get data into a Fitting Problem via cutest.

        :return: The fully parsed fitting problem
        :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
        """
        self.cache_dir = TemporaryDirectory()

        # set the MASTSIF environment variable so that pycutest
        # can find the sif files
        os.environ["MASTSIF"] = self.cache_dir.name

        self._n = None
        self._m = None

        # get just the short filename (minus the .SIF)
        fp = FittingProblem()

        # Clear the pycutest cache
        shutil.rmtree(os.environ['PYCUTEST_CACHE'])
        os.makedirs(os.environ['PYCUTEST_CACHE'])

        # Collect x and create new file with blank y
        fname, fp.data_x, fp.data_y = self._setup_data()

        self._p = self._import_problem(fname)

        fp.name = self._p.name
        self._y = fp.data_y

        fp.function = self._function  # self._p.obj
        fp.equation = None
        fp.starting_values = self._get_starting_values()
        fp.start_x = None
        fp.end_x = None

        self._cache = {id(fp.data_x): self._p.objcons}

        return fp

    def _import_problem(self, file_name):

        problem_ext = os.path.basename(file_name)
        problem, _ = os.path.splitext(problem_ext)

        return pycutest.import_problem(problem)

    def _function(self, x, *params):
        try:
            f = self._cache[id(x)]
        except KeyError:
            fname, _, _ = self._setup_data(x)
            p = self._import_problem(fname)
            f = p.objcons
            self._cache[id(x)] = f
        _, fx = f(np.asarray(params))

        return fx

    def _get_starting_values(self):

        starting_values = [
            OrderedDict([
                ('f{}'.format(i), self._p.x0[i])
                for i in range(self._n)
            ])
        ]

        return starting_values

    def _setup_data(self, x=None):
        """
        Parses CUTEst SIF files to extract data points

        :returns: data_x, data_y
        :rtype: lists of floats
        """
        if self.file.closed:
            with open(self._filename, 'r') as f:
                lines = f.readlines()
        else:
            lines = self.file.readlines()

        x_idx, y_idx = 0, 0

        # SIF requires columns of 25 chars
        col_width = 25

        written_x = False
        file_path = os.path.join(self.cache_dir.name, '{}.SIF'.format(id(x)))

        with open(file_path, 'w') as tmp_file:
            for line in lines:

                if "IE M " in line:
                    if x is None:
                        self._m = int(line.split()[2])
                        # this will always come before x/y data
                        # so allocate space for these now
                        data_x = np.zeros(self._m)
                        data_y = np.zeros(self._m)
                        # initialize index parameters for x and y
                    else:
                        line = line[:col_width] + str(len(x))
                        self._m = len(x)

                elif "IE N " in line:
                    self._n = int(line.split()[2])

                elif "RE X" in line:
                    if x is None:
                        data_x[x_idx] = float(line.split()[2])
                        x_idx += 1
                    else:
                        if written_x:
                            continue
                        else:
                            line = ''
                            new_lines = []
                            for i, val in enumerate(x):
                                tmp_line_x = ' RE X{}'.format(i)
                                spacing = ' '*(col_width - (5 + len(str(i))))
                                tmp_line_x += spacing + str(val)
                                tmp_line_y = ' RE Y{}{}0.0'.format(i, spacing)
                                new_lines.extend([tmp_line_x, tmp_line_y])
                            x_idx = y_idx = len(new_lines) / 2
                            line = '\n'.join(new_lines)
                            written_x = True

                elif "RE Y" in line:
                    if x is None:
                        data_y[y_idx] = float(line.split()[2])
                        y_idx += 1
                        line = line[:col_width] + '0.0'
                    else:
                        continue

                #print(line)
                tmp_file.write(line + '\n')

        # check the data is right
        # TODO: turn into an exception
        if x_idx != self._m:
            print("wrong number of x data points")
            print(" got {}, expected {}".format(x_idx, self._m))
        if y_idx != self._m:
            print("wrong number of y data points")
            print(" got {}, expected {}".format(y_idx, self._m))

        return file_path, data_x, data_y
