"""
Functions that prepare the function specified in NIST problem definition file
into the right format for SciPy.
"""

from __future__ import (absolute_import, division, print_function)

# This import is needed for dynamic scipy function def
import numpy as np


def nist_func_definitions(function, startvals):
    """
    Processing a function plus different set of starting values as specified in
    the NIST problem definition file into function definitions appropriate for
    the SciPy software.

    :param function : function string as defined in a NIST problem definition
                      file
    :param startvals: starting values for the function variables
                      provided in the definition file

    :return: array where each element contains function callable by SciPy,
             one set of starting parameter values and copy of the function
             string
    """
    param_names, all_values = get_nist_param_names_and_values(startvals)
    function_scipy_format = format_function_scipy(function)
    function_defs = []

    # Create a function def for each starting set in startvals
    if not is_safe(function_scipy_format):
        raise ValueError('Error while sanitizing input')
    # Sanitizing of function_scipy_format is done so exec use is valid
    # Param_names is sanitized in get_nist_param_names_and_values
    # pylint: disable=exec-used

    local_dict = {}
    global_dict = {'__builtins__': {}, 'np': np}
    exec("def fitting_function(x, " + param_names + "): return "
         + function_scipy_format, global_dict, local_dict)
    for values in all_values:
        # fitting function is created dynamically used exec
        # pylint: disable=undefined-variable
        function_defs.append(
            [local_dict['fitting_function'], values, function_scipy_format])

    return function_defs


def get_nist_param_names_and_values(startvals):
    """
    Parses startvals and retrieves the nist param names and values.
    """
    param_names = [row[0] for row in startvals]
    for p in param_names:
        if not p.isalnum():
            raise ValueError('Parameter names must be alphanumeric')
    param_names = ", ".join(param for param in param_names)
    all_values = [row[1] for row in startvals]
    all_values = map(list, zip(*all_values))

    return param_names, all_values


def format_function_scipy(function):
    """
    Formats the function string such that it is scipy-ready.
    """

    function = function.replace("exp", "np.exp")
    function = function.replace("^", "**")
    function = function.replace("cos", "np.cos")
    function = function.replace("sin", "np.sin")
    function = function.replace("tan", "np.tan")
    function = function.replace("pi", "np.pi")

    return function


def is_safe(func_str):
    """
    Verifies that a string is safe to be passed to exec in the context of an
    equation.

    :param func_str: The function to be checked
    :type func_str: string

    :returns: Whether the string is of the expected format for an equation
    :rtype: bool
    """
    # Remove whitespace
    func_str = func_str.replace(' ', '')

    # Empty string is safe
    if func_str == '':
        return True

    # These are all safe and can be stripped out
    if 'np' in func_str:
        np_funcs = ['np.exp', 'np.cos', 'np.sin', 'np.tan', 'np.pi']
        for s in np_funcs:
            func_str = func_str.replace(s, '')

    # Store valid symbols for later
    symbols = ['**', '/', '*', '+', '-']

    # Partition on outer brackets
    if '(' in func_str:
        if ')' not in func_str:
            # Number of brackets don't match
            return False

        # Split string "left(centre)right"
        left, remainder = func_str.split('(', 1)
        centre, right = remainder.split(')', 1)
        # Handle nested brackets
        while centre.count('(') != centre.count(')'):
            tmp, right = right.split(')', 1)
            centre = centre + ')' + tmp

        # If left is non-empty it should end with a symbol
        if left != '':
            left_ends_with_symbol = False
            for sym in symbols:
                if left.endswith(sym):
                    left = left.strip(sym)
                    left_ends_with_symbol = True
                    break
            if left_ends_with_symbol is False:
                return False

        # If right is non-empty it should start with a symbol
        if right != '':
            right_starts_with_symbol = False
            for sym in symbols:
                if right.startswith(sym):
                    right = right.strip(sym)
                    right_starts_with_symbol = True
                    break
            if right_starts_with_symbol is False:
                return False

        # Centre should not be empty
        if centre == '':
            return False

        # Return True if all sub parts are safe
        return is_safe(left) and is_safe(centre) and is_safe(right)

    # Split on a symbol and recurse
    for sym in symbols:
        if sym in func_str:
            left, right = func_str.split(sym, 1)

            # Symbol should not be at start or end of string (unless it's a -)
            if (left == '' and sym != '-') or right == '':
                return False

            # Return True if both sub parts are safe
            return is_safe(left) and is_safe(right)

    # Floating points are acceptable
    try:
        float(func_str)
        return True
    except ValueError:
        pass

    # Ints are acceptable
    try:
        int(func_str)
        return True
    except ValueError:
        pass

    # Only remaining acceptable strings are variables
    if func_str[0].isalpha() and func_str.isalnum():
        return True

    # Unparsed output remains
    return False
