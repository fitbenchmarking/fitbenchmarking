"""
This file implements a parser for lsqfit-specific problem definitions.
"""

import importlib
import os
import sys
import typing
from pathlib import Path

import numpy as np

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser


class LSQfitParser(FitbenchmarkParser):
    """
    Parser for FitBenchmark problems with lsqfit-specific metadata.

    Extends FitbenchmarkParser to read covariance matrices from *_cov.txt
    files, storing them in problem.additional_info.
    """

    def _create_function(self) -> typing.Callable:
        """
        Create a callable function from the lsqfit model specification.

        Expected function format:
        function='module=functions/functions,func=periodic_cosh,a=0.1,E=0.7,Nt=48'
        or
        function='module=functions,func=periodic_cosh,a=0.1,E=0.7,Nt=48'

        :return: A callable function
        :rtype: callable
        """
        pf = self._parsed_func[0]
        module_path_str = pf["module"]
        func_name = pf["func"]

        base_path = Path(self._filename).parent
        module_file_path = base_path / f"{module_path_str}.py"
        module_dir = module_file_path.parent
        module_name = module_file_path.stem

        sys.path.insert(0, str(module_dir))
        module = importlib.import_module(module_name)
        model_func = getattr(module, func_name)

        # Extract parameter names (all keys except module and func)
        param_names = [k for k in pf if k not in ("module", "func")]

        self._equation = func_name
        self._starting_values = [{n: pf[n] for n in param_names}]

        def fit_function(x, *params):
            param_dict = dict(zip(param_names, params))
            return model_func(x, **param_dict)

        return fit_function

    def _get_equation(self) -> str:
        """
        Returns the function name as the equation.

        :return: The function name
        :rtype: str
        """
        return self._equation

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values from the function definition
        :rtype: list
        """
        return self._starting_values

    def _set_additional_info(self):
        """
        Parse lsqfit priors and covariance.

        Stores in problem.additional_info:
            - 'priors': dict of {param_name: gvar} (if specified)
            - 'covariance': full covariance matrix (nt x nt)
        """
        super()._set_additional_info()

        # Parse covariance for each data file
        for data_file in self._get_data_file():
            cov = self._parse_covariance(data_file)
            if cov is not None:
                self.fitting_problem.additional_info["covariance"] = cov

    def _parse_covariance(self, data_file: str):
        """
        Extract covariance matrix from file.

        Reads from *_cov.txt (full covariance matrix).

        :param data_file: Path to the data file
        :type data_file: str
        :return: Covariance matrix, or None
        :rtype: np.ndarray or None
        """
        data_file = str(data_file)
        base = data_file.replace(".dat", "")
        cov_file = f"{base}_cov.txt"

        if not os.path.exists(cov_file):
            return None

        return np.loadtxt(cov_file)
