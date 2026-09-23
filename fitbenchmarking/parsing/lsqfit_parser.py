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

        # Handle both module names and module paths (with /)
        base_path = Path(self._filename).parent
        if "/" in module_path_str:
            # module_path_str is a path like "functions/functions"
            module_file_path = base_path / f"{module_path_str}.py"
            module_dir = module_file_path.parent
            module_name = module_file_path.stem
        else:
            # module_path_str is just a name like "functions"
            module_file_path = base_path / f"{module_path_str}.py"
            module_dir = base_path
            module_name = module_path_str

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

        # TODO: need to work on this
        # if "priors" in self._entries:
        #     priors = self._parse_priors_entry(self._entries["priors"])
        #     if priors:
        #         self.fitting_problem.additional_info["priors"] = priors

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

    # def _parse_priors_entry(self, priors_str: str) -> dict | None:
    #     """
    #     Parse priors from the problem definition file.

    #     Expected format: 'a=0.1(0.02),E=0.7(0.1)'
    #     where param=mean(sdev) creates gvar(mean, sdev).

    #     :param priors_str: The priors specification string
    #     :type priors_str: str
    #     :return: Dict of {param_name: gvar}, or None if empty/invalid
    #     :rtype: dict or None
    #     """
    #     if not priors_str or not priors_str.strip():
    #         return None

    #     priors = {}
    #     for item in priors_str.split(","):
    #         item = item.strip()
    #         if "=" not in item or "(" not in item or ")" not in item:
    #             continue
    #         name, val_str = item.split("=", 1)
    #         name = name.strip()
    #         val_str = val_str.strip()
    #         # Parse format: mean(sdev)
    #         if "(" in val_str and val_str.endswith(")"):
    #             parts = val_str.split("(")
    #             if len(parts) == 2:
    #                 try:
    #                     mean = float(parts[0].strip())
    #                     sdev = float(parts[1].rstrip(")").strip())
    #                     priors[name] = gv.gvar(mean, sdev)
    #                 except ValueError:
    #                     pass
    #     return priors if priors else None
