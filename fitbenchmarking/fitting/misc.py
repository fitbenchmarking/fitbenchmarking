"""
General utility functions for calculating some attributes of the fit.
"""

from __future__ import (absolute_import, division, print_function)
import numpy as np
from fitbenchmarking.utils import fitbm_result


def compute_chisq(actual, fitted, errors=None):
    """
    Simple function that calculates the sum of the differences squared
    between the data and the fit.

    :param actual: y data given in the fitting problem
    :type actual: numpy.array
    :param fitted: fitted result
    :type fitted: numpy.array
    :param errors: array of error values
    :type errors: numpy.array or None

    :returns: weighted or unweighted chi_sq value
    :rtype: float
    """
    r = fitted - actual
    if errors is not None:
        r = r / errors
    chi_sq = np.dot(r, r)

    return chi_sq


def create_result_entry(options, problem, status, chi_sq, runtime, minimizer,
                        ini_function_def, fin_function_def):
    """
    Helper function that creates a result object after fitting a problem
    with a certain function and minimizer.

    :param options: all the information specified by the user
    :type options: fitbenchmarking.utils.options.Options
    :param problem: problem object containing info that was fitted
    :type problem: fitbenchmarking/parsing/fitting_problem/FittingProblem
    :param status: status of the fit, i.e. success or failure
    :type status: bool
    :param chi_sq: the chi squared of the fit
    :type chi_sq: float
    :param runtime: the runtime of the fit
    :type runtime: float
    :param minimizer: the minimizer used for this particular fit
    :type minimizer: str
    :param ini_function_def: the initial function definition for the fit
    :type ini_function_def: str
    :param fin_function_def: the final function definition for the fit
    :type fin_function_def: str

    :returns: results object
    :rtype: fitbenchmarking/utils/fitbm_result/FittingResult
    """

    if 'fitFunction' in ini_function_def:
        ini_function_def = ini_function_def.replace(
            'fitFunction', problem.equation)
        fin_function_def = fin_function_def.replace(
            'fitFunction', problem.equation)

    # Create empty fitting result object
    result = fitbm_result.FittingResult()

    # Populate result object
    result.options = options
    result.problem = problem
    result.fit_status = status
    result.chi_sq = chi_sq
    result.runtime = runtime
    result.minimizer = minimizer
    result.ini_function_def = ini_function_def
    result.fin_function_def = fin_function_def

    return result
