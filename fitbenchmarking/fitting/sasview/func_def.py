"""
Methods that prepare the function definitions to be used by the mantid
fitting software.
"""
# Copyright &copy; 2016 ISIS Rutherford Appleton Laboratory, NScD
# Oak Ridge National Laboratory & European Spallation Source
#
# This file is part of Mantid.
# Mantid is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Mantid is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# File change history is stored at:
# <https://github.com/mantidproject/fitbenchmarking>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>

from __future__ import (absolute_import, division, print_function)

from utils.logging_setup import logger
from sasmodels.core import load_model
import numpy as np


def function_definitions(problem, data_obj):
    """
    Transforms the prob.equation field into a function that can be
    understood by the mantid fitting software.

    @param problem :: object holding the problem information

    @returns :: a function definitions string with functions that
                mantid understands
    """

    problem_type = extract_problem_type(problem)

    if problem_type == 'SasView'.upper():
        model_name = (problem.equation.split('='))[1]

        kernel = load_model(model_name)

        function_defs = [[kernel]]
    # if isinstance((problem.get_function())[0][0], FunctionWrapper):
    #     function_defs = [problem.get_function()[0][0]]
    # elif problem_type == 'NIST':
    #     nb_start_vals = len(problem.starting_values[0][1])
    #     function_defs = parse_function_definitions(problem, nb_start_vals)
    # else:
    #     raise NameError('Currently data types supported are FitBenchmark'
    #                     ' and nist, data type supplied was {}'.format(problem_type))

    return function_defs

def extract_problem_type(problem):
    """
    This function gets the problem object and figures out the problem type
    from the file name that the class that it has been sent from

    @param problem :: object holding the problem information

    @returns :: the type of the problem in capital letters (e.g. NIST)
    """
    problem_file_name = problem.__class__.__module__
    problem_type = (problem_file_name.split('_')[1]).upper()

    return problem_type

def get_fin_function_def(model_wrapper, problem):
    """

    :param model_wrapper:
    :param problem:
    :return:
    """

    param_names = [(param.split('='))[0] for param in problem.starting_values.split(',')]

    param_dict = model_wrapper.state()

    fin_function_def = problem.equation+','
    for name in param_names:
        fin_function_def += name+ '=' + str(param_dict[name]) + ','

    fin_function_def = fin_function_def[:-1]

    return fin_function_def

