"""
Fit benchmark one problem functions.
"""

from __future__ import absolute_import, division, print_function

import time

import numpy as np

from fitbenchmarking.fitting import misc
from fitbenchmarking.fitting.plotting import plot_helper, plots
from fitbenchmarking.fitting.software_controllers import (sasview_controller,
                                                          scipy_controller)


def fitbm_one_prob(user_input, problem):
    """
    Sets up the controller for a particular problem and fits the models
    provided in the problem object. The best fit, along with the data and a
    starting guess is then plotted on a visual display page.

    @param user_input :: all the information specified by the user
    @param problem :: a problem object containing information used in fitting

    @returns :: nested array of result objects, per function definition
                containing the fit information
    """

    results_fit_problem = []

    if user_input.software.lower() == 'scipy':
        controller = scipy_controller.ScipyController(problem, user_input.use_errors)
    elif user_input.software.lower() == 'sasview':
        controller = sasview_controller.SasviewController(problem, user_input.use_errors)
    else:
        raise NotImplementedError('The chosen software is not implemented yet: {}'.format(user_input.software))

    problem.data_x = controller.data_x
    problem.data_y = controller.data_y
    problem.data_e = controller.data_e

    for i in range(len(controller.functions)):
        controller.prepare(function_id=i)

        results_problem, best_fit = benchmark(controller=controller,
                                              minimizers=user_input.minimizers)

        if best_fit is not None:
            # Make the plot of the best fit
            plots.make_plots(problem=problem,
                             best_fit=best_fit,
                             count=i,
                             group_results_dir=user_input.group_results_dir)

        results_fit_problem.append(results_problem)

    return results_fit_problem


def benchmark(controller, minimizers):
    """
    Fit benchmark one problem, with one function definition and all
    the selected minimizers, using the chosen fitting software.

    @param controller :: The software controller for the fitting
    @param minimizers :: array of minimizers used in fitting

    @returns :: nested array of result objects, per minimizer
                and data object for the best fit data
    """
    min_chi_sq, best_fit = None, None
    results_problem = []

    init_function_def = controller.problem.get_function_def(params=controller.initial_params,
                                                            function_id=controller.function_id)

    for minimizer in minimizers:
        controller.prepare(minimizer=minimizer)

        try:
            start_time = time.time()
            controller.fit()
            end_time = time.time()
        except:
            controller.success = False
            end_time = np.inf

        runtime = end_time - start_time

        controller.cleanup()

        fin_function_def = controller.problem.get_function_def(params=controller.final_params,
                                                               function_id=controller.function_id)

        if not controller.success:
            chi_sq = np.nan
            status = 'failed'
        else:
            chi_sq = misc.compute_chisq(fitted=controller.results,
                                        actual=controller.data_y)
            status = 'success'

        if min_chi_sq is None:
            min_chi_sq = chi_sq + 1

        if chi_sq < min_chi_sq:
            min_chi_sq = chi_sq
            best_fit = plot_helper.data(name=minimizer,
                                        x=controller.data_x,
                                        y=controller.results,
                                        E=controller.data_e)

        individual_result = \
            misc.create_result_entry(problem=controller.problem,
                                     status=status,
                                     chi_sq=chi_sq,
                                     runtime=runtime,
                                     minimizer=minimizer,
                                     ini_function_def=init_function_def,
                                     fin_function_def=fin_function_def)

        results_problem.append(individual_result)

    return results_problem, best_fit
