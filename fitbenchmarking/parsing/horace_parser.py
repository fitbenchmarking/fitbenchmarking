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
        eng.evalc(f"addpath(genpath('{horace_location}'))")
        eng.evalc("horace_on")
        eng.evalc(f"addpath(genpath('{spinw_location}'))")
    elif (
        "HORACE_LOCATION" not in os.environ and "SPINW_LOCATION" in os.environ
    ):
        raise ParsingError(
            "Could not parse SpinW problem. Please ensure "
            "that HORACE_LOCATION is specfied as an environment "
            "variable"
        )
    elif (
        "HORACE_LOCATION" in os.environ and "SPINW_LOCATION" not in os.environ
    ):
        raise ParsingError(
            "Could not parse SpinW problem. Please ensure "
            "that SPINW_LOCATION is specfied as an environment "
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

    def _process_spinw_data(self, data_file_path):
        """
        Cut SpinW data based on q_cens.

        :param data_file_path: The path to the file to load the points from
        :type data_file_path: str

        :return: The path to the new file with 1d cuts
        :rtype: str
        """
        q_cens = [float(i) for i in self._entries["q_cens"].split(",")]
        foreground_dict = self._parsed_func[0]
        params_dict = {
            k: v for k, v in foreground_dict.items() if k != "foreground"
        }

        process_f = self._parse_function(self._entries["process_function"])
        script = pathlib.Path(process_f[0]["matlab_script"])
        path = pathlib.Path(self._filename).parent
        eng.addpath(str(path / script.parent))
        process_f_name = script.stem

        eng.workspace["params_dict"] = params_dict
        eng.evalc(
            f"[fitpow, qmax_final, qmin_final] = {process_f_name}"
            f"('{data_file_path}', params_dict, {q_cens})"
        )

        for var in ["y", "e"]:
            eng.evalc(f"{var}_final = fitpow.{var}")
        eng.evalc("x = fitpow.ebin_cens")

        eng.evalc("x_size = size(x)")
        x_size = [int(x) for x in list(eng.workspace["x_size"][0])]
        rows, cols = x_size
        if rows > 1 and cols == 1:
            eng.evalc("x=x'")  # need x to be a row vector
        eng.evalc(f"x_final = repelem(x,{len(q_cens)},1)'")

        # Create and fill struct
        eng.evalc(
            "data = struct('x', {}, 'y', {}, 'e', {}, 'qmax', {}, 'qmin', {})"
        )
        for i in np.arange(1, len(q_cens) + 1):
            for var in ["x", "y", "e", "qmax", "qmin"]:
                eng.evalc(f"data({i}).{var}={var}_final(:, {i})'")

        # Save cuts
        new_path = str(data_file_path).split(".mat")[0] + "_cuts.mat"
        eng.evalc(f"save('{new_path}', 'data')")
        return new_path

    def _get_data_points(self, data_file_path):
        """
        Get the data points of the problem from the data file.

        :param data_file_path: The path to the file to load the points from
        :type data_file_path: str

        :return: data
        :rtype: dict<str, np.ndarray>
        """
        # This if condition avoids error when "plot_type" not provided
        if (
            "plot_type" in self._entries
            and self._entries["plot_type"].lower() == "1d_cuts"
        ):
            new_data_path = self._process_spinw_data(data_file_path)
        else:
            new_data_path = data_file_path

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
                f"{func_name}('{new_data_path}','{self._horace_path}')"
            )
        except Exception as e:
            raise ParsingError(
                f"Failed to evaluate wye_function: {script}: {e}"
            ) from e
        mask = np.array(eng.workspace[f"{self._horace_msk}"])
        signal = np.array(eng.workspace["y"], dtype=np.float64)
        error = np.array(eng.workspace["e"], dtype=np.float64)

        # check for NaNs in 2D SpinW problems

        add_persistent_matlab_var(self._horace_msk)
        add_persistent_matlab_var(self._horace_w)
        eng.evalc(f"global {self._horace_msk}")
        eng.evalc(f"global {self._horace_w}")

        y = signal.flatten()
        e = error.flatten()
        x = np.ones(len(y))

        self._horace_x = x
        return {"x": x, "y": y, "e": e, "mask": mask}

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

        # This if condition avoids error when "plot_type" not provided
        if "plot_type" in self._entries:
            self._set_plot_type()
            self._add_plot_info_as_additional_info()

    def _set_plot_type(self) -> None:
        """
        Add plot_type to fitting_problem.additional_info.
        """
        plot_type_options = ["1d_cuts", "2d"]

        if self._entries["plot_type"].lower() in plot_type_options:
            self.fitting_problem.additional_info["plot_type"] = self._entries[
                "plot_type"
            ].lower()
        else:
            raise ParsingError(
                "The plot type should be one of these "
                f"options {plot_type_options}"
            )

    def _get_subplot_titles_SpinW(self, q_cens) -> list[str]:
        """Gets subplot titles for SpinW."""
        subplot_titles = [f"{i} Å<sup>-1</sup>" for i in q_cens]
        return subplot_titles

    def _add_plot_info_as_additional_info(self) -> None:
        """
        Add plot info needed for 1d cuts (e.g. n_plots and subplot_titles)
        to fitting_problem.additional_info.
        """

        if self.fitting_problem.additional_info["plot_type"] in [
            "1d_cuts",
            "2d",
        ]:
            eng.evalc(f"ebin_cens = {self._horace_w}(1).x")

            if self.fitting_problem.additional_info["plot_type"] == "2d":
                # Calculate ebin_cens
                ebin_cens = np.array(
                    eng.workspace["ebin_cens"][0], dtype=np.float64
                )
                if len(ebin_cens) == 1:
                    self.fitting_problem.additional_info["ebin_cens"] = (
                        ebin_cens[0]
                    )
                else:
                    self.fitting_problem.additional_info["ebin_cens"] = (
                        np.array([i[0] for i in ebin_cens], dtype=np.float64)
                    )

                # Calculate modQ_cens
                modQ_cens = np.array(
                    eng.workspace["ebin_cens"][1], dtype=np.float64
                )
                if len(modQ_cens) == 1:
                    self.fitting_problem.additional_info["modQ_cens"] = (
                        modQ_cens[0]
                    )
                else:
                    self.fitting_problem.additional_info["modQ_cens"] = (
                        np.array([i[0] for i in modQ_cens], dtype=np.float64)
                    )

                if "dq" in self._entries:
                    dq = float(self._entries["dq"])
                    self.fitting_problem.additional_info["dq"] = dq
                else:
                    raise ParsingError(
                        "dq is required for plotting 1D cuts of"
                        " (2D fitted) SpinW data"
                    )
            else:
                self.fitting_problem.additional_info["ebin_cens"] = np.array(
                    eng.workspace["ebin_cens"], dtype=np.float64
                )[0]

            self.fitting_problem.additional_info["ax_titles"] = {
                "x": "Energy (meV)",
                "y": "Intensity",
            }

            if "q_cens" in self._entries:
                q_cens = self._entries["q_cens"].split(",")
                self.fitting_problem.additional_info["q_cens"] = q_cens
                self.fitting_problem.additional_info["n_plots"] = len(q_cens)
                self.fitting_problem.additional_info["subplot_titles"] = (
                    self._get_subplot_titles_SpinW(q_cens)
                )
            else:
                raise ParsingError(
                    "q_cens are required for plotting 1D cuts of SpinW data"
                )
