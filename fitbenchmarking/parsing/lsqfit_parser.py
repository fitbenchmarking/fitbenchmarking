"""
This file implements a parser for lsqfit-specific problem definitions.
"""

import json
import os

import gvar as gv
import numpy as np

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser


class LSQfitParser(FitbenchmarkParser):
    """
    Parser for FitBenchmark problems with lsqfit-specific metadata.

    Extends FitbenchmarkParser to read prior specifications and covariance
    matrices from *_meta.json files, storing them in problem.additional_info.
    """

    def _set_additional_info(self):
        """
        Parse lsqfit metadata from *_meta.json files.

        Stores in problem.additional_info:
            - 'priors': dict of {param_name: gvar} (if available)
            - 'covariance': full covariance matrix (nt x nt)
            - 'lsqfit_metadata': raw metadata dict
        """
        super()._set_additional_info()

        # Parse metadata for each data file
        for data_file in self._get_data_file():
            self._parse_lsqfit_metadata(data_file)

    def _parse_lsqfit_metadata(self, data_file: str) -> None:
        """
        Parse and store lsqfit metadata and covariance info.

        :param data_file: Path to the data file
        :type data_file: str
        """
        meta = self._parse_metadata_file(data_file)
        if meta:
            self.fitting_problem.additional_info["lsqfit_metadata"] = meta

            # Extract priors if specified
            priors = self._parse_priors(meta)
            if priors:
                self.fitting_problem.additional_info["priors"] = priors

        # Extract covariance
        cov = self._parse_covariance(data_file)
        if cov is not None:
            self.fitting_problem.additional_info["covariance"] = cov

    def _parse_metadata_file(self, data_file: str):
        """
        Load and parse *_meta.json file associated with data file.

        :param data_file: Path to the data file
        :type data_file: str
        :return: Parsed JSON dict, or None if file not found
        :rtype: dict or None
        """
        meta_file = data_file.replace(".dat", "_meta.json")
        try:
            with open(meta_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def _parse_priors(self, metadata: dict):
        """
        Extract prior specifications from metadata.

        Expected metadata format:
            {
                "priors": {
                    "param_name": {"mean": 0.5, "sdev": 0.1},
                    ...
                }
            }

        :param metadata: Parsed metadata dict
        :type metadata: dict
        :return: Dict of {param_name: gvar}, or None
        :rtype: dict or None
        """
        priors_spec = metadata.get("priors", {})
        if not priors_spec:
            return None

        return {
            name: gv.gvar(spec["mean"], spec["sdev"])
            for name, spec in priors_spec.items()
        }

    def _parse_covariance(self, data_file: str):
        """
        Extract covariance matrix from file.

        Reads from *_cov.txt (full covariance matrix).

        :param data_file: Path to the data file
        :type data_file: str
        :return: Covariance matrix, or None
        :rtype: np.ndarray or None
        """
        base = data_file.replace(".dat", "")
        cov_file = f"{base}_cov.txt"

        if not os.path.exists(cov_file):
            return None

        return np.loadtxt(cov_file)
