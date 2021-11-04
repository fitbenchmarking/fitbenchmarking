"""
Functions that prepare the function specified in NIST problem definition file
into the right format for SciPy.
"""

from __future__ import (absolute_import, division, print_function)

# This import is needed for dynamic scipy function def
import numpy as np

from fitbenchmarking.utils.exceptions import ParsingError


def nist_func_definition(function, param_names):
    """
    Processing a function plus different set of starting values as specified in
    the NIST problem definition file into a callable

    :param function: function string as defined in a NIST problem definition
                     file
    :type function: str
    :param param_names: names of the parameters in the function
    :type param_names: list

    :return: callable function
    :rtype: callable
    """
    function_scipy_format = format_function_scipy(function)

    # Create a function def for each starting set in startvals
    if not is_safe(function_scipy_format):
        raise ParsingError('Error while sanitizing input')
    # Sanitizing of function_scipy_format is done so exec use is valid
    # Param_names is sanitized in get_nist_param_names_and_values
    # pylint: disable=exec-used

    local_dict = {}
    global_dict = {'__builtins__': {}, 'np': np}
    exec("def fitting_function(x, " + ','.join(param_names) + "): return "
         + function_scipy_format, global_dict, local_dict)

    return local_dict['fitting_function']


def nist_jacobian_definition(jacobian, param_names):
    """
    Processing a Jacobian plus different set of starting values as specified in
    the NIST problem definition file into a callable

    :param jacobian: Jacobian string as defined in the data files for the
                     corresponding NIST problem definition file
    :type jacobian: str
    :param param_names: names of the parameters in the function
    :type param_names: list

    :return: callable function
    :rtype: callable
    """

    scipy_jacobian = []
    for jacobian_lines in jacobian:
        jacobian_scipy_format = format_function_scipy(jacobian_lines)
        # Create a function def for each starting set in startvals
        if not is_safe(jacobian_scipy_format):
            raise ParsingError('Error while sanitizing Jacobian input')

        # Checks to see if the value is an integer and if so reformats the
        # value to be a constant vector.
        if is_int(jacobian_scipy_format):
            jacobian_scipy_format += "*(np.ones(x.shape[0]))"
        scipy_jacobian.append(jacobian_scipy_format)
    jacobian_format = "np.array([{}]).T".format(",".join(scipy_jacobian))

    new_param_name = "params"
    for i, name in enumerate(param_names):
        jacobian_format = jacobian_format.replace(
            name, "{0}[{1}]".format(new_param_name, i))

    # Sanitizing of jacobian_scipy_format is done so exec use is valid
    # Param_names is sanitized in get_nist_param_names_and_values
    # pylint: disable=exec-used
    local_dict = {}
    global_dict = {'__builtins__': {}, 'np': np}
    exec("def jacobian_function(x, " + new_param_name + "): return "
         + jacobian_format, global_dict, local_dict)

    return local_dict['jacobian_function']


def nist_hessian_definition(hessian, param_names):
    """
    Processing a Hessian into a callable

    :param hessian: Hessian string as defined in the data files for the
                     corresponding NIST problem definition file
    :type hessian: str
    :param param_names: names of the parameters in the function
    :type param_names: list

    :return: callable function
    :rtype: callable
    """

    scipy_hessian = []
    for hessian_lines in hessian:
        hessian_scipy_format = format_function_scipy(hessian_lines)
        # Create a function def for each starting set in startvals
        if not is_safe(hessian_scipy_format):
            raise ParsingError('Error while sanitizing Hessian input')

        # Checks to see if the value is an integer and if so reformats the
        # value to be a constant vector.
        if is_int(hessian_scipy_format):
            hessian_scipy_format += "*(np.ones(x.shape[0]))"

        new_param_name = "params"
        for i, name in enumerate(param_names):
            hessian_scipy_format = hessian_scipy_format.replace(
                name, "{0}[{1}]".format(new_param_name, i))
        scipy_hessian.append(hessian_scipy_format)

    dim = len(param_names)
    # reshape into Hessian matrix
    scipy_hessian = np.reshape(scipy_hessian, (dim, dim))

    hessian_matrix = ''
    for i in range(dim):
        hess_row = ",".join(scipy_hessian[:, i])
        hessian_matrix += '[' + hess_row + '],'
    hessian_format = "np.array([{}])".format(hessian_matrix)

    # Sanitizing of hessian_scipy_format is done so exec use is valid
    # param_names is sanitized in get_nist_param_names_and_values
    # pylint: disable=exec-used
    local_dict = {}
    global_dict = {'__builtins__': {}, 'np': np}
    exec("def hessian_function(x, " + new_param_name + "): return "
         + hessian_format, global_dict, local_dict)

    return local_dict['hessian_function']


def is_int(value):
    """
    Checks to see if a value is an integer or not

    :param value: String representation of an equation
    :type value: str

    :return: Whether or not value is an int
    :rtype: bool
    """
    try:
        int(value)
        value_bool = True
    except ValueError:
        value_bool = False
    return value_bool


def format_function_scipy(function):
    """
    Formats the function string such that it is scipy-ready.

    :param function: The function to be formatted
    :type function: str

    :return: The formatted function
    :rtype: str
    """

    function = function.replace("exp", "np.exp")
    function = function.replace("^", "**")
    function = function.replace("cos", "np.cos")
    function = function.replace("sin", "np.sin")
    function = function.replace("tan", "np.tan")
    function = function.replace("pi", "np.pi")
    function = function.replace("log", "np.log")
    function = function.replace("Log", "np.log")

    return function


# Due to the nature of this function it is necessary to be able to return at
# multiple places
# pylint: disable=too-many-return-statements, too-many-branches
def is_safe(func_str):
    """
    Verifies that a string is safe to be passed to exec in the context of an
    equation.

    :param func_str: The function to be checked
    :type func_str: string

    :return: Whether the string is of the expected format for an equation
    :rtype: bool
    """
    # Remove whitespace
    func_str = func_str.replace(' ', '')

    # Empty string is safe
    if func_str == '':
        return True

    # These are all safe and can be stripped out
    if 'np' in func_str:
        np_funcs = ['np.exp', 'np.cos', 'np.sin', 'np.tan', 'np.log']
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

    # np.pi is acceptable
    if func_str == 'np.pi':
        return True

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
