"""
This file implements a parser for the Fitbenchmark data format.
"""

import importlib
import os
import re
import sys
from contextlib import suppress
from functools import partialmethod
from pathlib import Path
from typing import Callable, Optional, Union

import numpy as np

from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.exceptions import ParsingError
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


class FitbenchmarkParser(Parser):
    """
    Parser for the native FitBenchmarking problem definition (FitBenchmark)
    file.
    """

    def __init__(self, filename, options):
        super().__init__(filename, options)

        self._parsed_func: list = None
        self._entries: dict = None

    def parse(self) -> FittingProblem:
        """
        Parse the Fitbenchmark problem file into a Fitting Problem.

        :return: The fully parsed fitting problem
        :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
        """
        self._entries = self._get_data_problem_entries()

        self.fitting_problem = FittingProblem(self.options)

        self._parsed_func = self._parse_function()

        self.fitting_problem.multifit = self._is_multifit()

        self.fitting_problem.name = self._entries["name"]
        self.fitting_problem.description = self._entries["description"]

        data_points = [self._get_data_points(p) for p in self._get_data_file()]

        self.fitting_problem.function = self._create_function()
        self.fitting_problem.format = self._entries["software"].lower()

        plot_scale_options = ["loglog", "logy", "logx", "linear"]

        if "plot_scale" in self._entries:
            if self._entries["plot_scale"].lower() in plot_scale_options:
                self.fitting_problem.plot_scale = self._entries[
                    "plot_scale"
                ].lower()
            else:
                raise ParsingError(
                    "The plot scale should be one of these "
                    f"options {plot_scale_options}"
                )
        else:
            self.fitting_problem.plot_scale = "linear"

        # If using a multivariate function wrap the call to take a single
        # argument
        if len(data_points[0]["x"].shape) > 1:
            old_function = self.fitting_problem.function
            all_data = []
            count = 0
            for dp in data_points:
                all_data.append(dp["x"])
                dp["x"] = np.arange(count, count + dp["x"].shape[0])
                count = count + dp["x"].shape[0]
            all_data = np.concatenate(all_data)

            def new_function(x, *p):
                inp = all_data[x]
                return old_function(inp, *p)

            self.fitting_problem.function = new_function
            self.fitting_problem.multivariate = True

        # Set this flag if the output is non-scalar either
        if len(data_points[0]["y"].shape) > 2:
            self.fitting_problem.multivariate = True

        # EQUATION
        self.fitting_problem.equation = self._get_equation()

        # STARTING VALUES
        self.fitting_problem.starting_values = self._get_starting_values()

        # PARAMETER RANGES
        # Creates list containing tuples of lower and upper bounds
        # (lb,ub) for each parameter
        vr = _parse_range(self._entries.get("parameter_ranges", ""))
        if vr:
            self.fitting_problem.set_value_ranges(vr)

        # FIT RANGES
        fit_ranges_str = self._entries.get("fit_ranges", "")
        # this creates a list of strs like '{key: val, ...}' and parses each
        fit_ranges = [
            _parse_range("{" + r.split("}")[0] + "}")
            for r in fit_ranges_str.split("{")[1:]
        ]

        self._set_data_points(data_points, fit_ranges)

        # SPARSE JAC FUNCTION
        self.fitting_problem.jacobian = self._dense_jacobian()
        self.fitting_problem.sparse_jacobian = self._sparse_jacobian()

        self._set_additional_info()

        return self.fitting_problem

    def _is_multifit(self) -> bool:
        """
        Returns true if the problem is a multi fit problem.

        :return: True if the problem is a multi fit problem.
        :rtype: bool
        """
        return self._entries["input_file"].startswith("[")

    def _create_function(self) -> Callable:
        """
        Creates a python callable which is a wrapper around the fit function.
        """
        raise NotImplementedError

    def _get_equation(self) -> str:
        """
        Returns the equation in the problem definition file.

        :return: The equation in the problem definition file.
        :rtype: str
        """
        equation_count = len(self._parsed_func)
        if equation_count == 1:
            return self._parsed_func[0]["name"]
        return f"{equation_count} Functions"

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        # SasView functions can have reserved keywords so ignore these
        ignore = ["name"]

        starting_values = [
            {
                name: val
                for name, val in self._parsed_func[0].items()
                if name not in ignore
            }
        ]

        return starting_values

    def _set_data_points(self, data_points: list, fit_ranges: list) -> None:
        """
        Sets the data points and fit range data in the fitting problem.

        :param data_points: A list of data points.
        :type data_points: list
        :param fit_ranges: A list of fit ranges.
        :type fit_ranges: list
        """
        self.fitting_problem.data_x = data_points[0]["x"]
        self.fitting_problem.data_y = data_points[0]["y"]
        if "e" in data_points[0]:
            self.fitting_problem.data_e = data_points[0]["e"]

        if fit_ranges and "x" in fit_ranges[0]:
            self.fitting_problem.start_x = fit_ranges[0]["x"][0]
            self.fitting_problem.end_x = fit_ranges[0]["x"][1]

    def _set_additional_info(self) -> None:
        """
        Sets any additional info for a fitting problem.
        """
        return

    def _get_data_file(self):
        """
        Find/create the (full) path to a data_file(s) specified in a
        FitBenchmark definition file, where the data_file is searched for in
        the directory of the definition file and subfolders of this file.

        :return: (full) path to a data file.
        :rtype: list<str>
        """
        if self._is_multifit():
            pattern = r"['\"]\s*([^'\"]+)\s*['\"]"
            files = re.findall(pattern, self._entries["input_file"])
        else:
            files = [self._entries["input_file"]]

        search_path = Path(self._filename).parent

        paths = [
            path
            for file in files
            for path in search_path.rglob(file)
            if "data_files" in path.parts
        ]

        missing_files = [
            file for file in files if not any(search_path.rglob(file))
        ]
        for file in missing_files:
            LOGGER.error("Data file %s not found", file)

        return paths

    def _get_data_problem_entries(self):
        """
        Get the problem entries from a problem definition file.

        :return: The entries from the file with string values
        :rtype: dict
        """
        entries = {}
        for line in self.file.readlines():
            # Discard comment after #
            text = re.search(r"^(.*?)\s*#", line)
            line = text[1] if text else line
            if line and (match := re.search(r"(\w+)\s*=\s*(.+)", line)):
                key, value = match.groups()
                if key == "name":
                    value = re.sub(r"[\\/]", "", value)
                entries[key] = re.sub(r"^\s*['\"]?|['\"]?\s*$", "", value)

        return entries

    def _parse_string(self, key: str, func: Optional[str] = None):
        """
        if key == "function"
            Get the params from the function as a list of dicts
            from the data file.
        if key == "jac"
            Get the (relative) path and the name of the jacobian
            function from the data file. Returns a list of dicts
            if these have been defined.

        :param func: The function to parse. Optional, defaults to
                     self._entries[key]
        :type func: str
        :return: Function definition in format:
                 [{name1: value1, name2: value2, ...}, ...]
        :rtype: list of dict
        """
        func = func if func else self._entries[key]
        function_def = [
            self._parse_single_function(f) for f in func.split(";")
        ]
        return function_def

    _parse_function = partialmethod(_parse_string, "function")
    _parse_jac_function = partialmethod(_parse_string, "jac")

    def _get_jacobian(self, jac_type) -> Optional[Callable]:
        """
        Process the dense/sparse jac function into a callable.
        Returns None if this is not possible.

        :param jac_type: either 'dense_func' or 'sparse_func'
        :type jac_type: str
        :return: A callable function or None
        :rtype: callable or None
        """
        if "jac" in self._entries:
            parsed_jac_func = self._parse_jac_function()
            if jac_type not in parsed_jac_func[0]:
                return None
            pf = parsed_jac_func[0]
            path = os.path.join(os.path.dirname(self._filename), pf["module"])
            sys.path.append(os.path.dirname(path))
            module = importlib.import_module(os.path.basename(path))
            func = getattr(module, pf[jac_type])
            return func
        else:
            return None

    _dense_jacobian = partialmethod(_get_jacobian, "dense_func")
    _sparse_jacobian = partialmethod(_get_jacobian, "sparse_func")

    @classmethod
    def _parse_single_function(cls, func: str) -> dict:
        """
        Convert a string defining a single list of parameters into a
        dictionary with parsed values.

        Parameter values may be:
          - nested parameter dictionary
          - vectors of float
          - int
          - float
          - bool ('true', 'false')
          - strings (not containing '[](),=' )

        Example:
          a=1,b=3.2,c='foo',d=(e=true,f='bar'),g=[1.0,1.0,1.0]

        :param func: The definition to parse
        :type func: str
        :raises ParsingError: If unexpected characters are encoutered or
                              parentheses do not match
        :return: The function as a dict of name, value pairs.
        :rtype: dict
        """
        func_dict = {}
        pattern = (
            r"\s*([^=\s]+)\s*=\s*(\([^)]*\)|\[[^\]]*\]|'"
            r"[^']*'|\"[^\"]*\"|[-\w\.\+e/]+)\s*(?:,|$)"
        )
        matches = re.findall(pattern, func)

        for key, value in matches:
            if not re.match(r"^\w+$", key):
                raise ParsingError(
                    f"Unexpected character in parameter name: {key}"
                )

            if value.startswith(("(", "[")):
                value = cls._parse_parens(value)
            else:
                value = value.strip("'\"")
                value = cls._parse_function_value(value)

            func_dict[key] = value

        return func_dict

    @classmethod
    def _parse_parens(cls, string: str):
        """
        Parse a string starting with an opening bracket into the parsed
        contents of the brackets.

        If the string starts with '(' a dictionary is returned.
        If the string starts with '[' a list is returned.

        :param string: The string to parse
        :type string: str
        :raises ParsingError: If brackets remain unclosed

        :return: The parsed value
        :rtype: Union[dict, list]
        """
        if any(
            string.count(open_bracket) != string.count(close_bracket)
            for open_bracket, close_bracket in {"(": ")", "[": "]"}.items()
        ):
            raise ParsingError("Not all brackets are closed in function.")

        if string.startswith("("):
            string = string.removeprefix("(").removesuffix(")")
            value = cls._parse_single_function(string)
        else:  # string.startswith("[")
            string = string.removeprefix("[").removesuffix("]")
            value = [cls._parse_function_value(s) for s in string.split(",")]

        return value

    @staticmethod
    def _parse_function_value(value: str) -> Union[int, float, bool, str]:
        """
        Parse a value from a string into a numerical type if possible.

        :param value: The value to parse
        :type value: str
        :raises ParsingError: If the value has any unexpected characters
        :return: The parsed value
        :rtype: bool, int, float, or str
        """
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        for convert in [int, float]:
            with suppress(ValueError, TypeError):
                return convert(value)
        return value

    def _get_data_points(self, data_file_path: str):
        """
        Get the data points of the problem from the data file.

        :param data_file_path: The path to the file to load the points from
        :type data_file_path: str

        :return: data
        :rtype: dict[str, np.ndarray]
        """

        with open(data_file_path, encoding="utf-8") as f:
            data_text = f.readlines()

        first_row = _find_first_line(data_text)
        dim = len(data_text[first_row].split())
        cols = _get_column_data(data_text, first_row, dim)

        if not cols["x"] or not cols["y"]:
            raise ParsingError("Input files need both X and Y values.")
        if cols["e"] and len(cols["y"]) != len(cols["e"]):
            raise ParsingError("Error must be of the same dimension as Y.")

        data_points = np.zeros((len(data_text) - first_row, dim))

        for idx, line in enumerate(data_text[first_row:]):
            point_text = line.split()
            # Skip any values that can't be represented
            try:
                point = [float(val) for val in point_text]
            except ValueError:
                point = [np.nan for _ in point_text]
            data_points[idx, :] = point

        # Strip all np.nan entries
        data_points = data_points[~np.isnan(data_points[:, 0]), :]

        # Split into x, y, and e
        data = {key: data_points[:, cols[key]] for key in ["x", "y"]}
        if cols["e"]:
            data["e"] = data_points[:, cols["e"]]

        # Flatten if the columns are 1D
        for key, col in cols.items():
            if len(col) == 1:
                data[key] = data[key].flatten()

        return data


def _parse_range(range_str):
    """
    Parse a range string for the problem into a dict or list of dict if
    multi-fit.

    :param range_str: The a string to parse
    :type range_str: string

    :return: The ranges in a dictionary with key as the var and value as a
             list with min and max
             e.g. {'x': [0, 10]}
    :rtype: dict
    """
    output_ranges = {}

    if range_str:
        range_str = range_str.removeprefix("{").removesuffix("}")
        bracket_pairs = {"(": ")", "[": "]", "{": "}"}

        if any(
            range_str.count(open_bracket) != range_str.count(close_bracket)
            for open_bracket, close_bracket in bracket_pairs.items()
        ):
            raise ParsingError(f"Unbalanced parentheses in {range_str}")

        pattern = (
            r'\'?"?([\w\.\s]+)"?\'?\s*:\s*'
            r"([\(\[\{])([\d\.]+),\s*([\d\.]+)([\)\]\}])"
        )
        matches = re.findall(pattern, range_str)

        for var, open_bracket, low, high, close_bracket in matches:
            expected_closing = bracket_pairs.get(open_bracket, "")
            if close_bracket != expected_closing:
                raise ParsingError(f"Mismatched parentheses for '{var}'")

            try:
                low, high = float(low), float(high)
            except ValueError:
                raise ParsingError(f"Expected floats for '{var}'")

            if low >= high:
                raise ParsingError(
                    f"MIN value must be smaller than MAX value for '{var}'"
                )

            output_ranges[var.lower().strip()] = [low, high]

    return output_ranges


def _find_first_line(file_lines: list[str]) -> int:
    """
    Finds the first line where the data starts i.e. the
    first line with a float on it.

    :param file_lines: A list of lines from a file.
    :type file_lines: A list of strings.

    :return: index of the first file line with data.
    :rtype: int
    """
    for i, line in enumerate(file_lines):
        line = line.strip()
        if not line:
            continue
        try:
            float(line.split()[0])
        except ValueError:
            continue
        return i

    raise ParsingError("Could not find data points")


def _get_column_data(file_lines: list[str], first_row: int, dim: int) -> list:
    """
    Gets the data in the file as a dictionary of x, y and e data.

    :param file_lines: A list of lines from a file.
    :type file_lines: A list of strings.
    :param first_row: Index of the first line in the file containing data.
    :type first_row: int
    :param dim: The number of columns in the file.
    :type dim: int

    :return: index of the first file line with data.
    :rtype: int
    """
    cols = {"x": [], "y": [], "e": []}
    num_cols = 0
    if first_row != 0:
        header = file_lines[0].split()
        for heading in header:
            if heading == "#":
                continue
            if heading[0] == "<" and heading[-1] == ">":
                heading = heading[1:-1]
            col_type = heading[0].lower()
            if col_type in ["x", "y", "e"]:
                cols[col_type].append(num_cols)
                num_cols += 1
            else:
                raise ParsingError(
                    "Unrecognised header line, header names must start with "
                    '"x", "y", or "e".'
                    "Examples are: "
                    '"# X Y E", "#   x0 x1 y e", "# X0 X1 Y0 Y1 E0 E1", '
                    '"<X> <Y> <E>", "<X0> <X1> <Y> <E>"...'
                )
        if dim != num_cols:
            raise ParsingError("Could not match header to columns.")
    else:
        cols["x"], cols["y"] = [0], [1]
        if dim == 3:
            cols["e"] = [2]
        elif dim != 2:
            raise ParsingError(
                "Cannot infer size of inputs and outputs in datafile. "
                "Headers are required when not using 1D inputs and outputs."
            )
    return cols
