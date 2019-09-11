"""
Functions that are dependent on mantid api and are used by external methods
(e.g. scipy).
"""

from __future__ import (absolute_import, division, print_function)

import mantid.simpleapi as msapi
from utils.logging_setup import logger


def gen_func_obj(function_name, params_set):
    """
    Generates a mantid function object.

    @param function_name :: the name of the function to be generated
    @params_set :: set of parameters per function extracted from the problem definition file

    @returns :: mantid function object that can be called in python
    """
    params_set = (params_set.split(', ties'))[0]

    exec "function_object = msapi." + function_name + "("+ params_set +")"

    return function_object


def set_ties(function_object, ties):
    """
    Sets the ties for a function/composite function object.

    @param function_object :: mantid function object
    @param ties :: array of strings containing the ties

    @returns :: mantid function object with ties
    """

    for idx, ties_per_func in enumerate(ties):
        for tie in ties_per_func:
            """
            param_str is a string of the parameter name in the mantid format
            For a Mantid Composite Function, a formatted parameter name would 
            start with the function number and end with the parameter name.
            For instance, f0.A would refer to a parameter A of the first 
            function is a Composite Function.
            """
            param_str = 'f'+str(idx)+'.'+(tie.split("'"))[0]
            function_object.fix(param_str)

    return function_object


def store_main_problem_data(fname, problem):
    """
    Stores the main problem data into the relevant attributes of the
    problem object.

    @param fname :: path to the neutron problem definition file
    @param problem :: object holding the problem information
    """

    wks_imported = msapi.Load(Filename=fname)
    problem.data_x = wks_imported.readX(0)
    problem.data_y = wks_imported.readY(0)
    problem.data_e = wks_imported.readE(0)
    problem.ref_residual_sum_sq = 0
