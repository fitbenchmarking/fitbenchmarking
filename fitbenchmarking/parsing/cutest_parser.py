"""
This file calls the pycutest interface for SIF data
"""

import os
import time
from tempfile import TemporaryDirectory

import numpy as np
import pycutest

from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.exceptions import ParsingError

if os.path.isdir(os.environ["PYCUTEST_CACHE"] + "/pycutest_cache_holder"):
    # clear problems from cache that are older than 1 hour, do not clear
    # all problems as when running with matlab the cache is cleared again
    # when dill.load is called in controller
    for cached_problem in pycutest.all_cached_problems():
        file_age = time.time() - os.path.getmtime(
            os.environ["PYCUTEST_CACHE"]
            + "/pycutest_cache_holder/"
            + cached_problem[0]
        )
        if file_age > 7200:
            pycutest.clear_cache(cached_problem[0], cached_problem[1])


class CutestParser(Parser):
    """
    Use the pycutest interface to parse SIF files

    This parser has some quirks.
    Due to the complex nature of SIF files, we utilise pycutest to generate the
    function. This function returns the residual `r(f,x,y,e) := (f(x) - y)/e`
    for some parameters x.
    For consistency we require the value to be `f(x, p)`.

    To avoid having to convert back from the residual in the evaluation, we
    store the data separately and set y to 0.0, and e to 1.0 for all
    datapoints.

    We then accomodate for the missing x argument by caching x against an
    associated function `f_x(p)`.

    As such the function is defined by: `f(x, p) := r(f_x,p,0,1)`

    If a new x is passed, we write a new file and parse it to generate a
    function. We define x to be new if ``not np.isclose(x, cached_x)`` for each
    ``cached_x`` that has already been stored.
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

        self._num_params = None

        # get just the short filename (minus the .SIF)
        fp = FittingProblem(self.options)

        # Collect x and create new file with blank y
        fname, fp.data_x, fp.data_y, fp.data_e = self._setup_data()

        self._p = _import_problem(fname)

        fp.name = self._p.name

        fp.function = self._function  # self._p.objcons
        fp.jacobian = self._dense_jacobian  # self._p.lagjac
        fp.sparse_jacobian = self._sparse_jacobian  # self._p.slagjac

        fp.equation = None
        fp.starting_values = self._get_starting_values()
        fp.start_x = None
        fp.end_x = None
        fp.format = "cutest"

        # read in parameter ranges if bounds are
        # specified
        vr = self._get_parameter_ranges()
        if vr:
            fp.set_value_ranges(vr)

        # Create a list of x and f (function evaluation) and x and g (Jacobian
        # evaluation).
        # If a new x is given we will create and parse a new file
        self._cache_f = [(fp.data_x, self._p.objcons)]
        self._cache_g = [(fp.data_x, self._p.lagjac, self._p.slagjac)]

        return fp

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

        for cx, cf in self._cache_f:
            if x.size == cx.size and np.isclose(cx, x).all():
                f = cf
                break
        else:
            fname, _, _, _ = self._setup_data(x)
            p = _import_problem(fname)
            f = p.objcons
            self._cache_f.append((x, f))
        _, fx = f(np.asarray(params))

        return fx

    def _dense_jacobian(self, x, *params):
        """
        If these x values have been passed in before, then run the function to
        calculate the Jacobian. Otherwise, create a new problem file, parse and
        cache the Jacobian

        :param x: The data to evaluate at
        :type x: np.array
        :return: The result of evaluating at the given x
        :rtype: np.array
        """
        os.environ["MASTSIF"] = self.mastsif_dir.name

        for cx, cg, _ in self._cache_g:
            if np.isclose(cx, x).all():
                g = cg
                break
        else:
            fname, _, _, _ = self._setup_data(x)
            p = _import_problem(fname)
            g = p.lagjac
            sg = p.slagjac
            self._cache_g.append((x, g, sg))
        _, gx = g(np.asarray(params)[0])

        return gx

    def _sparse_jacobian(self, x, *params):
        """
        Computes sparse jac and returns it in coo format.

        :param x: The data to evaluate at
        :type x: np.array
        :return: The result of evaluating at the given x
        :rtype: scipy.sparse.coo_matrix
        """

        os.environ["MASTSIF"] = self.mastsif_dir.name

        for cx, _, csg in self._cache_g:
            if np.isclose(cx, x).all():
                sg = csg
                break
        else:
            fname, _, _, _ = self._setup_data(x)
            p = _import_problem(fname)
            g = p.lagjac
            sg = p.slagjac
            self._cache_g.append((x, g, sg))
        _, gx = sg(np.asarray(params)[0])

        return gx

    def _get_starting_values(self):
        starting_values = [
            {f"f{i}": self._p.x0[i] for i in range(self._num_params)}
        ]

        return starting_values

    def _get_parameter_ranges(self):
        if all(x == -1.0e20 for x in self._p.bl) and all(
            x == 1.0e20 for x in self._p.bu
        ):
            parameter_values = False
        else:
            parameter_values = [
                {
                    f"f{i}": (self._p.bl[i], self._p.bu[i])
                    for i in range(self._num_params)
                }
            ][0]

        return parameter_values

    def _setup_data(self, x=None):
        """
        Reads datapoints from CUTEst SIF files and rewrites values where
        needed.

        With x=None, read all data from file into x_data, y_data, and e_data,
        then create a new file with y values of 0.0, and e values of 1.0.

        If x is given, create a file with the given x data, 0.0 y values, and
        1.0 e values, and return the path to the file.

        y and e are set here to avoid the function returning residuals that we
        then have to convert every time the function is evaluated.

        :param x: X values to save (used for evaluating at new points)
        :type x: np.array
        :returns: path to new sif file, data_x, data_y, data_e
        :rtype: str, numpy.ndarray, numpy.ndarray, numpy.ndarray
        """

        if self.file.closed:
            with open(self._filename, encoding="utf-8") as f:
                lines = f.readlines()
        else:
            lines = self.file.readlines()

        if x is None:
            x, y, e, to_write, n = _read_x(lines)
            self._num_params = n
        else:
            if not x.shape:
                x = np.array([x])
            x, y, e, to_write = _write_x(lines, x)

        file_path = os.path.join(
            self.mastsif_dir.name, f"{str(id(x))[-10:]}.SIF"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(to_write)

        return file_path, x, y, e


def _read_x(lines):
    """
    Read data from the list of lines from the file.
    Overwrite the Y and E values with 0.0 and 1.0 respectively, and return a
    new list of lines of text.

    :param lines: The text to parse data from.
    :type lines: list of str
    :return: x, y, and error data, list of text to write, and number of
             parameters from the file.
    :rtype: numpy array, numpy array, numpy array, list of str, int
    """
    to_write, num_params = [], 0
    # SIF requires columns of 25 chars, so line[:col_width-1] will be 1 column
    col_width = 25

    x_idx, y_idx, e_idx = 0, 0, 0

    for line in lines:
        if "IE M " in line:
            data_count = int(line.split()[2])
            # this will always come before x/y data so allocate space now
            data_x = np.zeros(data_count)
            data_y = np.zeros(data_count)
            data_e = np.zeros(data_count)
        elif "IE N " in line:
            num_params = int(line.split()[2])
        elif "RE X" in line:
            data_x[x_idx] = float(line.split()[2])
            x_idx += 1
        elif "RE Y" in line:
            data_y[y_idx] = float(line.split()[2])
            y_idx += 1
            line = line[: col_width - 1] + "0.0"
        elif "RE E" in line:
            data_e[e_idx] = float(line.split()[2])
            e_idx += 1
            line = line[: col_width - 1] + "1.0"
        to_write.append(line + "\n")

    _check_data(data_count, x_idx, y_idx, e_idx)
    if not e_idx:
        data_e = None
    return data_x, data_y, data_e, to_write, num_params


def _write_x(lines, x):
    """
    Overwrite x values in the list of lines from the file with values from a
    numpy array.
    Use Y=0.0 and E=1.0, and return the new list of lines of text.

    :param lines: The text to parse data from.
    :type lines: list of str
    :param x: The data to write in place of the data in file
    :type x: numpy array
    :return: x, y, and error data, list of text to write.
    :rtype: numpy array, numpy array, numpy array, list of str
    """
    to_write = []
    x_idx, y_idx, e_idx = 0, 0, 0
    # SIF requires columns of 25 chars, so line[:col_width-1] will be 1 column
    col_width = 25

    written = False

    for line in lines:
        if "IE M " in line:
            line = line[: col_width - 1] + str(len(x))
        elif "IE MLOWER" in line:
            line = line[: col_width - 1] + "1\n"
        elif "IE MUPPER" in line:
            line = line[: col_width - 1] + str(len(x))
        elif "RE X" in line:
            # Only write data once.
            # Once written can skip all x entries
            if written:
                continue
            line = ""
            new_lines = []
            for i, val in enumerate(x):
                idx = i + 1
                spacing = " " * (col_width - (5 + len(str(idx))))
                new_lines.extend(
                    [
                        f" RE X{idx}{spacing}{val}",
                        f" RE Y{idx}{spacing}0.0",
                        f" RE E{idx}{spacing}1.0",
                    ]
                )
            x_idx = y_idx = e_idx = len(new_lines) / 3
            line = "\n".join(new_lines)
            written = True
        elif "RE Y" in line or "RE E" in line:
            # These should be ignored as they are written when X is found.
            continue
        to_write.append(line + "\n")

    _check_data(len(x), x_idx, y_idx, e_idx)
    return x, np.zeros_like(x), np.ones_like(x), to_write


def _check_data(count, x, y, e):
    """
    Check that then number of data points for x, y, and errors are consistent.

    :param count: Expected number of datapoints
    :type count: int
    :param x: Number of x data points
    :type x: int
    :param y: Number of y data points
    :type y: int
    :param e: Number of error data points
    :type e: int
    :raises ParsingError: If x, y, or e does not match count. (e can also be 0)
    """

    if x != count:
        raise ParsingError(
            f"Wrong number of x data points. Got {x}, expected {count}"
        )
    if y != count:
        raise ParsingError(
            f"Wrong number of y data points. Got {y}, expected {count}"
        )
    if e not in (0, count):
        raise ParsingError(
            f"Wrong number of e data points. Got {e}, expected {count}"
        )


def _import_problem(file_name):
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
