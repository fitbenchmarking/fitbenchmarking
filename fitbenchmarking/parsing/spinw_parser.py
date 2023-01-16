"""
This file implements a parser for SpinW data.
"""
import os
import typing
import sys

import matlab
import numpy as np

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser
from fitbenchmarking.utils.exceptions import ParsingError
from fitbenchmarking.utils.matlab_engine import ENG as eng
from fitbenchmarking.utils.matlab_engine import add_persistent_matlab_var

# horace_location = os.environ["HORACE_LOCATION"]
# sys.path.insert(0, horace_location)

# eng.evalc(f"addpath('{horace_location}')")

# Keep horace active - even after cleanup of horace controller..
eng.evalc('horace = 1;')
add_persistent_matlab_var('horace')
eng.evalc('horace_on')


class SpinWParser(FitbenchmarkParser):
    """
    Parser for a SpinW problem definition file.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A container for improving efficiency in function call if calling
        # with full input data
        self._spinw_x: typing.Optional[np.ndarray] = None

    def _get_data_points(self, data_file_path):
        """
        Get the data points of the problem from the data file.

        :param data_file_path: The path to the file to load the points from
        :type data_file_path: str

        :return: data
        :rtype: dict<str, np.ndarray>
        """
        wxye_data_f = self._parse_function(self._entries['wxye_function'])
        #print(wxye_data_f[0]['matlab_script'])
        path = os.path.join(os.path.dirname(self._filename),
                        wxye_data_f[0]['matlab_script'])
        eng.addpath(os.path.dirname(path))
        func_name = os.path.basename(path).split('.', 1)[0]
        
        eng.evalc(f'[w, x ,y ,e] = {func_name}("{data_file_path}")')
        x = np.array(eng.workspace['x'])
        signal = np.array(eng.workspace['y'])
        error = np.array(eng.workspace['e'])

        #print(f'{x=}')

        add_persistent_matlab_var('w')

        y = signal.flatten()
        e = error.flatten()

        self._spinw_x = x

        return {'x': x, 'y': y, 'e': e}

    

    def _create_function(self) -> typing.Callable:
        """
        Process the SpinW formatted function into a callable.

        Expected function format:
        function='matlab_script=filename,p0=...'

        :return: A callable function
        :rtype: callable
        """
        
        if len(self._parsed_func) > 1:
            raise ParsingError('Could not parse SpinW problem. Please ensure '
                               'only 1 function definition is present')

        pf = self._parsed_func[0]
        path = os.path.join(os.path.dirname(self._filename),
                            pf['matlab_script'])
        eng.addpath(os.path.dirname(path))
        func_name = os.path.basename(path).split('.', 1)[0]

        # pylint: disable=attribute-defined-outside-init
        self._equation = os.path.splitext(
            os.path.basename(pf['matlab_script']))[0]

        p_names = [k for k in pf if k != 'matlab_script']

        self._starting_values = [{n: pf[n] for n in p_names}]
        
        simulate_f = self._parse_function(self._entries['simulate_function'])
        print(simulate_f[0]['matlab_script'])
        path = os.path.join(os.path.dirname(self._filename),
                        simulate_f[0]['matlab_script'])
        eng.addpath(os.path.dirname(path))
        simulate_func_name = os.path.basename(path).split('.', 1)[0]

        def fit_function(x, *p):
            # Assume, for efficiency, matching shape => matching values
            # print(*p)
            if x.shape != self._spinw_x.shape:
                return np.ones(x.shape)
            eng.workspace['fitpars'] = matlab.double(p)
            eng.evalc(f'[spinw_y, e, msk] = {simulate_func_name}(w,fitpars)')
            return np.array(eng.workspace['spinw_y']).flatten()

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
            eng.evalc('horace_on;')
            print(eng.evalc(f"load('{path}')"))
        self.fitting_problem.set_persistent_vars = set_persistent_vars
        return super()._set_additional_info()