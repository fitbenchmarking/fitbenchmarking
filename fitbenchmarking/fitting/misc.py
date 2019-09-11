"""
General utility functions for calculating some attributes of the fit.
"""

from __future__ import (absolute_import, division, print_function)
import numpy as np
from utils import fitbm_result


def compute_chisq(differences):
    """
    Simple function that calculates the sum of the differences squared
    between the data and the fit.

    @param differences :: differences between the actual data and the
                          fit points.

    @returns :: the sum of the square of each element in differences
    """
    chi_sq = np.sum(np.square(differences))

    return chi_sq


def create_result_entry(problem, status, chi_sq, runtime, minimizer,
                        ini_function_def, fin_function_def):
    """
    Helper function that creates a result object after fitting a problem
    with a certain function and minimizer.

    @param problem :: problem object containing info that was fitted
    @param status :: status of the fit, i.e. success or failure
    @param chi_sq :: the chi squared of the fit
    @param runtime :: the runtime of the fit
    @param minimizer :: the minimizer used for this particular fit
    @param ini_function_def :: the initial function definition for the fit
    @param fin_function_def :: the final function definition for the fit

    @returns :: the result object
    """

    if 'fitFunction' in ini_function_def:
        ini_function_def = ini_function_def.replace('fitFunction',problem.equation)
        fin_function_def = fin_function_def.replace('fitFunction',problem.equation)

    # Create empty fitting result object
    result = fitbm_result.FittingResult()

    # Populate result object
    result.problem = problem
    result.fit_status = status
    result.chi_sq = chi_sq
    result.runtime = runtime
    result.minimizer = minimizer
    result.ini_function_def = ini_function_def
    result.fin_function_def = fin_function_def

    return result
