"""
This file implements a parser for Horace problem sets.
"""

import os
import pathlib
import typing

import matlab
import numpy as np

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser
from fitbenchmarking.utils.exceptions import ParsingError
from fitbenchmarking.utils.matlab_engine import ENG as eng
from fitbenchmarking.utils.matlab_engine import add_persistent_matlab_var


def horace_on():
    """
    Turning Horace and SpinW on in matlab
    """
    if "HORACE_LOCATION" in os.environ and "SPINW_LOCATION" in os.environ:
        horace_location = os.environ["HORACE_LOCATION"]
        spinw_location = os.environ["SPINW_LOCATION"]
        eng.evalc("restoredefaultpath")
        eng.evalc(f"addpath('{horace_location}')")
        eng.evalc("horace_on")
        eng.evalc(f"addpath('{spinw_location}')")
    elif (
        "HORACE_LOCATION" not in os.environ and "SPINW_LOCATION" in os.environ
    ):
        raise ParsingError(
            "Could not parse SpinW problem. Please ensure "
            "that HORACE_LOCATION is specfied as a environment "
            "variable"
        )
    elif (
        "HORACE_LOCATION" in os.environ and "SPINW_LOCATION" not in os.environ
    ):
        raise ParsingError(
            "Could not parse SpinW problem. Please ensure "
            "that SPINW_LOCATION is specfied as a environment "
            "variable"
        )
    else:
        eng.evalc("horace_on")


horace_on()


class HoraceParser(FitbenchmarkParser):
    """
    Parser for a Horace problem definition file.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._equation = None
        self._starting_values = None

        # A container for improving efficiency in function call if calling
        # with full input data
        self._horace_x: typing.Optional[np.ndarray] = None
        self._horace_w: typing.Optional[str] = None
        self._horace_msk: typing.Optional[str] = None
        self._horace_path: typing.Optional[str] = None

    def _get_data_points(self, data_file_path):
        """
        Get the data points of the problem from the data file.

        :param data_file_path: The path to the file to load the points from
        :type data_file_path: str

        :return: data
        :rtype: dict<str, np.ndarray>
        """
        wye_data_f = self._parse_function(self._entries["wye_function"])
        script = pathlib.Path(wye_data_f[0]["matlab_script"])
        func_name = script.stem

        path = pathlib.Path(self._filename).parent
        eng.addpath(str(path / script.parent))

        self._horace_path = str(path.resolve())

        name = self._entries["name"].replace(" ", "_")
        self._horace_w = f"w_{name}"
        self._horace_msk = f"msk_{name}"

        try:
            eng.evalc(
                f"[{self._horace_w}, y, e, {self._horace_msk}] ="
                f"{func_name}('{data_file_path}','{self._horace_path}')"
            )
        except Exception as e:
            raise ParsingError(
                f"Failed to evaluate wye_function: {script}"
            ) from e

        signal = np.array(eng.workspace["y"], dtype=np.float64)
        error = np.array(eng.workspace["e"], dtype=np.float64)

        add_persistent_matlab_var(self._horace_msk)
        add_persistent_matlab_var(self._horace_w)
        eng.evalc(f"global {self._horace_msk}")
        eng.evalc(f"global {self._horace_w}")

        y = signal.flatten()
        e = error.flatten()
        x = np.ones(len(y))

        self._horace_x = x
        return {"x": x, "y": y, "e": e}

    def _create_function(self) -> typing.Callable:
        """
        Process the Horace formatted function into a callable.

        Expected function format:
        function='foreground=filename,p0=...'
        or
        function='foreground=filename,p0=... ; background=filename,q0=...'

        :return: A callable function
        :rtype: callable
        """
        path = pathlib.Path(self._filename).parent

        function_string = "{loc}: {f_name}<br>parameters: {p_names}"
        foreground_func = self._parsed_func[0]
        foreground_params = [k for k in foreground_func if k != "foreground"]
        foreground_params_string = ", ".join(foreground_params)
        script = pathlib.Path(foreground_func["foreground"])
        eng.addpath(str(path / script.parent))
        foreground_func_name = script.stem
        frgd_eq = function_string.format(
            loc="foreground",
            f_name=foreground_func_name,
            p_names=foreground_params_string,
        )
        foreground_starting_vals = {
            n: foreground_func[n] for n in foreground_params
        }

        if len(self._parsed_func) == 1:
            equations = frgd_eq
            start_values = [foreground_starting_vals]
        else:
            background_func = self._parsed_func[1]
            background_params = [
                k for k in background_func if k != "background"
            ]
            background_params_string = ", ".join(background_params)
            script = pathlib.Path(background_func["background"])
            eng.addpath(str(path / script.parent))
            background_func_name = script.stem
            bkgd_eq = function_string.format(
                loc="background",
                f_name=background_func_name,
                p_names=background_params_string,
            )
            equations = frgd_eq + "<br>" + bkgd_eq

            background_starting_vals = {
                n: background_func[n] for n in background_params
            }
            start_values = [
                {**foreground_starting_vals, **background_starting_vals}
            ]

        self._equation = equations
        self._starting_values = start_values

        simulate_f = self._parse_function(self._entries["simulate_function"])
        script = pathlib.Path(simulate_f[0]["matlab_script"])
        eng.addpath(str(path / script.parent))
        simulate_func_name = script.stem

        def fit_function(x, *p):
            # Assume, for efficiency, matching shape => matching values
            # print(*p)
            if x.shape != self._horace_x.shape:
                return np.ones(x.shape)
            eng.evalc(f"global {self._horace_msk}")
            eng.evalc(f"global {self._horace_w}")
            eng.workspace["fitpars"] = matlab.double(p)
            eng.evalc(
                f"horace_y = {simulate_func_name}"
                f"({self._horace_w},fitpars,{self._horace_msk})"
            )
            return np.array(
                eng.workspace["horace_y"], dtype=np.float64
            ).flatten()

        return fit_function

    def _get_equation(self) -> str:
        """
        Returns the equation in the problem definition file.

        :return: The equation in the problem definition file.
        :rtype: str
        """
        return self._equation

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        return self._starting_values

    def _set_additional_info(self) -> None:
        """
        Add set_tbf to the fitting problem.
        """

        def set_persistent_vars(path):
            """
            Update the persistent_vars from a matlab dump.

            :param path: The file to update from
            :type path: str
            """
            horace_on()
            eng.evalc(f"addpath(genpath('{self._horace_path}'))")
            print(eng.evalc(f"load('{path}')"))

        self.fitting_problem.set_persistent_vars = set_persistent_vars
        return super()._set_additional_info()
