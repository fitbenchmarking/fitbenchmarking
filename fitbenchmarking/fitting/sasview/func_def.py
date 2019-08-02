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
from sasmodels.bumps_model import Model, Experiment
import numpy as np


def function_definitions(problem):
    """
    Transforms the prob.equation field into a function that can be
    understood by the mantid fitting software.

    @param problem :: object holding the problem information

    @returns :: a function definitions string with functions that
                mantid understands
    """

    problem_type = extract_problem_type(problem)

    if problem_type == 'SasView'.upper():
        model_name_and_param_list = problem.equation.split(',')
        model_name = ((model_name_and_param_list[0]).split('='))[1]
        model_param = model_name_and_param_list[1:]
        param_name = [(param.split('='))[0] for param in model_param]
        param_val = [(param.split('='))[1] for param in model_param]

        kernel = load_model(model_name)

        zipParam = zip(param_name, param_val)

        # pars = dict(zipParam)
        pars = dict(radius=35,
                    length=350,
                    background=0.0,
                    scale=1.0,
                    sld=4.0,
                    sld_solvent=1.0)

        model = Model(kernel, **pars)

        model.radius.range(1, 50)
        model.length.range(1, 500)

        function_defs = [[model, np.array(param_val)]]
    # if isinstance((problem.get_function())[0][0], FunctionWrapper):
    #     function_defs = [problem.get_function()[0][0]]
    # elif problem_type == 'NIST':
    #     nb_start_vals = len(problem.starting_values[0][1])
    #     function_defs = parse_function_definitions(problem, nb_start_vals)
    # else:
    #     raise NameError('Currently data types supported are FitBenchmark'
    #                     ' and nist, data type supplied was {}'.format(problem_type))

    return function_defs

def parse_function_definition(problem):
    """

    :param problem:
    :return:
    """

    function_list = (problem.equation).split(';')
    func_params_list = [(function.split(','))[1:] for function in function_list]
    formatted_param_list = ['f'+str(func_params_list.index(func_params))+'.'+param for func_params in func_params_list for param in func_params]

    param_names = [(param.split('='))[0] for param in formatted_param_list]
    param_values = [(param.split('='))[1] for param in formatted_param_list]

    class fitFunction(IFunction1D):
        def init(self):

            for param in param_names:
                if not param.endswith('BinWidth'):
                    self.declareParameter(param)

        def function1D(self, xdata):

            fit_param = ''
            for param in param_names:
                if not param.endswith('BinWidth'):
                    fit_param += param + '=' + str(self.getParameterValue(param)) +','
            fit_param = fit_param[:-1]

            return problem.eval_f(xdata, fit_param)

    FunctionFactory.subscribe(fitFunction)

    function_defs = []
    start_val_str = ''
    for param, value in zip(param_names, param_values):
        if not param.endswith('BinWidth'):
            start_val_str += param + '=' + str(value) + ','
    start_val_str = start_val_str[:-1]
    function_defs.append("name=fitFunction,{}".format(start_val_str))

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
