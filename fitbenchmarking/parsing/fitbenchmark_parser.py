"""
This file implements a parser for the Fitbenchmark data format.
"""

import importlib
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
    PARAM_IGNORE_LIST = []

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
        self.fitting_problem.multistart = self._is_multistart()

        self.fitting_problem.name = self._entries["name"]
        self.fitting_problem.description = self._entries["description"]

        data_points = [self._get_data_points(p) for p in self._get_data_file()]

        self.fitting_problem.function = self._create_function()
        self.fitting_problem.format = self._entries["software"].lower()

        self.fitting_problem.plot_scale = self._get_plot_scale()

        self.fitting_problem.multivariate = self._is_multivariate(data_points)
        if data_points[0]["x"].ndim > 1:
            # If using a multivariate function wrap the call to take a single
            # argument
            old_function = self.fitting_problem.function
            all_data = np.concatenate([dp["x"] for dp in data_points])
            self.fitting_problem.function = lambda x, *p: old_function(
                all_data[x], *p
            )

        # EQUATION
        self.fitting_problem.equation = self._get_equation()

        # STARTING VALUES
        self.fitting_problem.starting_values = self._get_starting_values()

        # PARAMETER RANGES
        # Creates list containing tuples of lower and upper bounds
        # (lb,ub) for each parameter
        if vr := _parse_range(self._entries.get("parameter_ranges", "")):
            self.fitting_problem.set_value_ranges(vr)

        # FIT RANGES
        fit_ranges_str = self._entries.get("fit_ranges", "")
        # this creates a list of strs like '{key: val, ...}' and parses each
        fit_ranges = [
            _parse_range(match)
            for match in re.findall(r"\{[^}]*\}", fit_ranges_str)
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

    def _is_multistart(self) -> bool:
        """
        Returns false for all parsers. multistart analysis
        is only enabled for the mantid parser.

        :return: False because multi start analysis is disabled.
        :rtype: bool
        """
        if "n_fits" in self._entries:
            raise ParsingError(
                "Multi start analysis is only supported "
                "for mantid problems. Either remove 'n_fits' "
                "entry from the problem definition file. "
                "Or update the 'software' in the problem "
                "definition file to 'Mantid'."
            )
        return False

    def _is_multivariate(self, data_points) -> bool:
        """
        Returns true if the problem is multivariate.

        :param data_points: A list of data points.
        :type data_points: list
        :return: True if problem is multivariate.
        :rtype: bool
        """
        return data_points[0]["x"].ndim > 1 or data_points[0]["y"].ndim > 1

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
        return (
            self._parsed_func[0]["name"]
            if len(self._parsed_func) == 1
            else f"{len(self._parsed_func)} Functions"
        )

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        return [
            {
                name: val
                for name, val in self._parsed_func[0].items()
                if name not in self.PARAM_IGNORE_LIST
            }
        ]

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
        self.fitting_problem.data_e = data_points[0].get("e", None)

        if fit_ranges and "x" in fit_ranges[0]:
            self.fitting_problem.start_x = fit_ranges[0]["x"][0]
            self.fitting_problem.end_x = fit_ranges[0]["x"][1]

    def _get_plot_scale(self) -> str:
        """
        Gets the plot scale of the fitting problem.

        :return: The plot scale. "linear" if not specified.
        :rtype: str
        """
        valid_options = ["loglog", "logy", "logx", "linear"]
        plot_scale = self._entries.get("plot_scale", "linear").lower()
        if plot_scale not in valid_options:
            raise ParsingError(
                "The plot scale should be one of these "
                f"options {valid_options}"
            )
        return plot_scale

    def _set_additional_info(self) -> None:
        """
        Sets any additional info for a fitting problem.
        """
        return

    def _get_data_file(self) -> list:
        """
        Find/create the (full) path to a data_file(s) specified in a
        FitBenchmark definition file, where the data_file is searched for in
        the directory of the definition file and subfolders of this file.

        :return: (full) path to a data file. Return None if not found
        :rtype: list<str>
        """
        if self._is_multifit():
            pattern = r"['\"]\s*([^'\"]+)\s*['\"]"
            files = re.findall(pattern, self._entries["input_file"])
        else:
            files = [self._entries["input_file"]]

        search_path = Path(self._filename).parent
        subdirs = [d for d in search_path.iterdir() if d.is_dir()]

        paths = []
        for file in files:
            # Tries to find the first file in the sub folders
            # with the same name. The data file is usually
            # stored in a sub folder called data_files or data.
            # The logic will also be able to handle cases
            # where the sub folder has a different name.
            found_path = next(
                (
                    subdir_match
                    for subdir in subdirs
                    for subdir_match in subdir.rglob(file)
                ),
                None,
            )
            if found_path is None:
                # Then look for it in parent directory of self._filename
                found_path = next(search_path.rglob(file), None)
                if found_path is None:
                    LOGGER.error("Data file %s not found", file)
            paths.append(found_path)

        return paths

    def _get_data_problem_entries(self) -> dict:
        """
        Get the problem entries from a problem definition file.

        :return: The entries from the file with string values
        :rtype: dict
        """
        entries = {}
        for line in self.file.readlines():
            # Discard comment after #
            line = (
                text[1] if (text := re.search(r"^(.*?)\s*#", line)) else line
            )
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
        func = func or self._entries[key]
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
        if "jac" not in self._entries:
            return None

        parsed_jac_func = self._parse_jac_function()
        if jac_type not in parsed_jac_func[0]:
            return None

        pf = parsed_jac_func[0]
        module_path = Path(self._filename).parent / pf["module"]
        sys.path.append(str(module_path.parent))
        module = importlib.import_module(module_path.stem)
        return getattr(module, pf[jac_type])

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
            if not re.match(r"^\w+$", key) and not (
                "." in key and key.count(".") == 1
            ):
                raise ParsingError(
                    f"Unexpected character in parameter name: {key}"
                )

            if value.startswith(("(", "[")):
                value = cls._parse_parens(value)
            else:
                value = cls._parse_function_value(value.strip("'\""))

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
            value = cls._parse_single_function(
                string.removeprefix("(").removesuffix(")")
            )
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

    def _get_data_points(self, data_file_path: str) -> dict:
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
        data_lines = data_text[first_row:]
        dim = len(data_lines[0].split())
        cols = _get_column_data(data_text, first_row, dim)

        data_points = np.full((len(data_lines), dim), np.nan)

        for idx, line in enumerate(data_lines):
            # Skip any values that can't be represented
            with suppress(ValueError):
                data_points[idx] = [float(val) for val in line.split()]

        # Strip all np.nan entries
        data_points = data_points[~np.isnan(data_points).any(axis=1)]

        # Split into x, y, and e
        data = {
            key: data_points[:, indices]
            for key, indices in cols.items()
            if indices
        }

        # Flatten if the columns are 1D
        for key in data:
            if data[key].shape[1] == 1:
                data[key] = data[key].ravel()

        return data


def _parse_range(range_str: str) -> dict:
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

        if not (matches := re.findall(pattern, range_str)):
            raise ParsingError(
                f"Could not parse string '{range_str}'. "
                "The range of variables should be defined as "
                "'var': (min, max) where var should be the "
                "variable name and min and max values of the "
                "range should be defined as floats."
            )

        for var, open_bracket, low, high, close_bracket in matches:
            expected_closing = bracket_pairs.get(open_bracket, "")
            if close_bracket != expected_closing:
                raise ParsingError(f"Mismatched parentheses for '{var}'")

            low, high = float(low), float(high)
            if low >= high:
                raise ParsingError(
                    f"MIN must be smaller than MAX value for '{var}'"
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
    index = (
        i
        for i, line in enumerate(file_lines)
        if re.match(r"^\s*-?\d+(\.\d+)?", line)
    )
    if (data_start_index := next(index, None)) is None:
        raise ParsingError("Could not find data points")
    return data_start_index


def _get_column_data(file_lines: list[str], first_row: int, dim: int) -> dict:
    """
    Gets the data columns in the file as a dictionary of x, y and e.

    :param file_lines: A list of lines from a file.
    :type file_lines: A list of strings.
    :param first_row: Index of the first line in the file containing data.
    :type first_row: int
    :param dim: The number of columns in the file.
    :type dim: int

    :return: A dictionary mapping "x", "y", and "e" to their
             respective column indices.
    :rtype: dict
    """
    cols = {"x": [], "y": [], "e": []}

    if first_row == 0:
        # No header in data file
        cols["x"], cols["y"] = [0], [1]
        if dim == 3:
            cols["e"] = [2]
        elif dim != 2:
            raise ParsingError(
                "Cannot infer size of inputs and outputs in datafile. "
                "Headers are required when not using 1D inputs and outputs."
            )
    else:
        pattern = r"\bX\d*\b|\bY\d*\b|\bE\d*\b"
        matches = [
            m.lower()
            for m in re.findall(pattern, file_lines[0], re.IGNORECASE)
        ]
        if matches:
            if dim != len(matches):
                raise ParsingError("Could not match header to columns.")
            for ix, col_name in enumerate(matches):
                if (col_type := col_name[0]) in cols:
                    cols[col_type].append(ix)
        else:
            raise ParsingError(
                "Unrecognised header line, header names must start with "
                '"x", "y", or "e".'
                "Examples are: "
                '"# X Y E", "#   x0 x1 y e", "# X0 X1 Y0 Y1 E0 E1", '
                '"<X> <Y> <E>", "<X0> <X1> <Y> <E>"...'
            )

    if not (cols["x"] and cols["y"]):
        raise ParsingError("Input files need both X and Y values.")
    if cols["e"] and len(cols["y"]) != len(cols["e"]):
        raise ParsingError("Error must be of the same dimension as Y.")

    return cols
