"""
This file calls the pycutest interface for SIF data
"""

from __future__ import print_function

import numpy as np
import os
import pycutest
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

from collections import OrderedDict
from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.create_dirs import del_contents_of_dir
from fitbenchmarking.utils.logging_setup import logger


# Empty the cache
del_contents_of_dir(os.environ["PYCUTEST_CACHE"])


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
        self.mastsif_dir = TemporaryDirectory()

        # set the MASTSIF environment variable so that pycutest
        # can find the sif files
        os.environ["MASTSIF"] = self.mastsif_dir.name

        self._n = None
        self._m = None

        # get just the short filename (minus the .SIF)
        fp = FittingProblem()

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

        # Use the object id as a hash to the function.
        # In order to prevent the id being reused also store the x_data
        self._cache = {id(fp.data_x): {'f': self._p.objcons, 'x': fp.data_x}}

        return fp

    def __del__(self):
        self.mastsif_dir.cleanup()

    def _import_problem(self, file_name):
        """
        Import the problem using cutest

        :param file_name: The path to the file
        :type file_name: str
        :return: The parsed problem
        :rtype: pycutest.CUTEstProblem
        """

        problem_ext = os.path.basename(file_name)
        problem, _ = os.path.splitext(problem_ext)

        return pycutest.import_problem(problem)

    def _function(self, x, *params):
        """
        If these x values have been passed in before, then run the function
        Otherwise, create a new problem file, parse and cache the function

        :param x: The data to evaluate at
        :type x: np.array
        :return: The result of evaluating at the given x
        :rtype: np.array
        """
        os.environ["MASTSIF"] = self.mastsif_dir.name

        try:
            f = self._cache[id(x)]['f']
        except KeyError:
            fname, _, _ = self._setup_data(x)
            try:
                p = self._import_problem(fname)
            except:
                print('Failed for: {}'.format(self._p.name))
                raise
            f = p.objcons
            self._cache[id(x)] = {'f': f, 'x': x}
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

        :param x: X values to save (used for evaluating at new points)
        :type x: np.array
        :returns: data_x, data_y
        :rtype: lists of floats
        """

        if self.file.closed:
            with open(self._filename, 'r') as f:
                lines = f.readlines()
        else:
            lines = self.file.readlines()

        if x is not None and len(x.shape) == 0:
            x = np.array([x])

        x_idx, y_idx = 0, 0
        data_x, data_y = None, None

        # SIF requires columns of 25 chars
        col_width = 25

        written_x = False

        to_write = []

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
                    line = line[:col_width-1] + str(len(x))
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
                            idx = i+1
                            tmp_line_x = ' RE X{}'.format(idx)
                            spacing = ' '*(col_width - (5 + len(str(idx))))
                            tmp_line_x += spacing + str(val)
                            tmp_line_y = ' RE Y{}{}0.0'.format(idx,
                                                                spacing)
                            new_lines.extend([tmp_line_x, tmp_line_y])
                        x_idx = y_idx = len(new_lines) / 2
                        line = '\n'.join(new_lines)
                        written_x = True

            elif "RE Y" in line:
                if x is None:
                    data_y[y_idx] = float(line.split()[2])
                    y_idx += 1
                    line = line[:col_width-1] + '0.0\n'
                else:
                    continue

            to_write.append(line)

        if x is None:
            x = data_x

        file_path = os.path.join(self.mastsif_dir.name,
                                 '{}.SIF'.format(str(id(x))[-10:]))

        with open(file_path, 'w') as f:
            f.writelines(to_write)

        # check the data is right
        # TODO: turn into an exception
        if x_idx != self._m:
            print("wrong number of x data points")
            print(" got {}, expected {}".format(x_idx, self._m))
        if y_idx != self._m:
            print("wrong number of y data points")
            print(" got {}, expected {}".format(y_idx, self._m))

        return file_path, data_x, data_y
