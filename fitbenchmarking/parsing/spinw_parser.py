"""
This file implements a parser for SpinW data.
"""
import os
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
        eng.evalc("spinw_on")
    elif "HORACE_LOCATION" not in os.environ and \
         "SPINW_LOCATION" in os.environ:
        raise ParsingError('Could not parse SpinW problem. Please ensure '
                           'that HORACE_LOCATION is specfied as a environment '
                           'variable')
    elif "HORACE_LOCATION" in os.environ and \
         "SPINW_LOCATION" not in os.environ:

        raise ParsingError('Could not parse SpinW problem. Please ensure '
                           'that SPINW_LOCATION is specfied as a environment '
                           'variable')
    else:
        eng.evalc("horace_on")


eng.evalc('horace = 1;')
add_persistent_matlab_var('horace')
horace_on()


class SpinWParser(FitbenchmarkParser):
    """
    Parser for a SpinW problem definition file.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A container for improving efficiency in function call if calling
        # with full input data
        self._spinw_x: typing.Optional[np.ndarray] = None
        self._spinw_w: typing.Optional[str] = None
        self._spinw_msk: typing.Optional[str] = None
        self._spinw_path: typing.Optional[str] = None

    def _get_data_points(self, data_file_path):
        """
        Get the data points of the problem from the data file.

        :param data_file_path: The path to the file to load the points from
        :type data_file_path: str

        :return: data
        :rtype: dict<str, np.ndarray>
        """
        wye_data_f = self._parse_function(self._entries['wye_function'])
        path = os.path.join(os.path.dirname(self._filename),
                            wye_data_f[0]['matlab_script'])
        eng.addpath(os.path.dirname(path))
        func_name = os.path.basename(path).split('.', 1)[0]

        self._spinw_path = os.path.abspath(os.path.dirname(self._filename))

        name = self._entries["name"].replace(' ', '_')

        self._spinw_w = f'w_{name}'
        self._spinw_msk = f'msk_{name}'

        eng.evalc(f"[{self._spinw_w}, y, e, {self._spinw_msk}] ="
                  f"{func_name}('{data_file_path}','{self._spinw_path}')")

        signal = np.array(eng.workspace['y'], dtype=np.float64)
        error = np.array(eng.workspace['e'], dtype=np.float64)

        add_persistent_matlab_var(self._spinw_msk)
        add_persistent_matlab_var(self._spinw_w)
        eng.evalc(f'global {self._spinw_msk}')
        eng.evalc(f'global {self._spinw_w}')

        y = signal.flatten()
        e = error.flatten()
        x = np.ones(len(y))

        self._spinw_x = x
        return {'x': x, 'y': y, 'e': e}

    def _create_function(self) -> typing.Callable:
        """
        Process the SpinW formatted function into a callable.

        Expected function format:
        function='foreground=filename,p0=...'
        or
        function='foreground=filename,p0=... ; background=filename,q0=...'

        :return: A callable function
        :rtype: callable
        """
        # pylint: disable=attribute-defined-outside-init
        if len(self._parsed_func) == 1:
            pfg = self._parsed_func[0]
            p_names = [k for k in pfg if k != 'foreground']
            equations = "foreground: " + \
                os.path.splitext(os.path.basename(pfg['foreground']))[0] +\
                "<br>" + 'parameters: ' + ', '.join(p_names)
            start_values = [{n: pfg[n] for n in p_names}]
        else:
            pfg = self._parsed_func[0]
            pbg = self._parsed_func[1]
            p_names = [k for k in pfg if k != 'foreground']
            bp_names = [k for k in pbg if k != 'background']
            equations = "foreground: " + \
                os.path.splitext(os.path.basename(pfg['foreground']))[0] +\
                "<br>" + 'parameters: ' + ', '.join(p_names) +\
                "<br>" + "background: " +\
                os.path.splitext(os.path.basename(pbg['background']))[0] \
                + '<br>' + 'parameters: ' + ', '.join(bp_names)
            fg_starting_vals = {n: pfg[n] for n in p_names}
            bg_starting_vals = {n: pbg[n] for n in bp_names}
            start_values = [{**fg_starting_vals, **bg_starting_vals}]

        self._equation = equations
        self._starting_values = start_values

        simulate_f = self._parse_function(self._entries['simulate_function'])
        path = os.path.join(os.path.dirname(self._filename),
                            simulate_f[0]['matlab_script'])
        eng.addpath(os.path.dirname(path))
        simulate_func_name = os.path.basename(path).split('.', 1)[0]

        def fit_function(x, *p):
            # Assume, for efficiency, matching shape => matching values
            # print(*p)
            if x.shape != self._spinw_x.shape:
                return np.ones(x.shape)
            eng.evalc(f'global {self._spinw_msk}')
            eng.evalc(f'global {self._spinw_w}')
            eng.workspace['fitpars'] = matlab.double(p)
            eng.evalc(f'spinw_y = {simulate_func_name}'
                      f'({self._spinw_w},fitpars,{self._spinw_msk})')
            return np.array(eng.workspace['spinw_y'],
                            dtype=np.float64).flatten()

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
            eng.evalc(f"addpath(genpath('{self._spinw_path}'))")
            print(eng.evalc(f"load('{path}')"))
        self.fitting_problem.set_persistent_vars = set_persistent_vars
        return super()._set_additional_info()
