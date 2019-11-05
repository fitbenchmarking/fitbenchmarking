"""
Fit benchmark one problem functions.
"""

from __future__ import absolute_import, division, print_function

import timeit

import numpy as np

from fitbenchmarking.fitting import misc
from fitbenchmarking.fitting.plotting import plot_helper, plots
try:
    from fitbenchmarking.fitting.controllers.dfogn_controller import DFOGNController
except ImportError:
    DFOGNController = None
try:
    from fitbenchmarking.fitting.controllers.mantid_controller import MantidController
except ImportError:
    MantidController = None
try:
    from fitbenchmarking.fitting.controllers.sasview_controller import SasviewController
except ImportError:
    SasviewController = None
try:
    from fitbenchmarking.fitting.controllers.scipy_controller import ScipyController
except ImportError:
    ScipyController = None


def fitbm_one_prob(user_input, problem, num_runs):
    """
    Sets up the controller for a particular problem and fits the models
    provided in the problem object. The best fit, along with the data and a
    starting guess is then plotted on a visual display page.

    @param user_input :: all the information specified by the user
    @param problem :: a problem object containing information used in fitting
    @param num_runs :: number of times controller.fit() is run to
                       generate an average runtime

    @returns :: nested array of result objects, per function definition
                containing the fit information
    """

    results_fit_problem = []

    software = user_input.software.lower()

    controllers = {'dfogn': DFOGNController,
                   'mantid': MantidController,
                   'sasview': SasviewController,
                   'scipy': ScipyController}

    if software in controllers:
        controller = controllers[software](problem, user_input.use_errors)
    else:
        raise NotImplementedError('The chosen software is not implemented yet:'
                                  '{}'.format(user_input.software))

    # The controller reformats the data to fit within a start- and end-x bound
    # It also estimates errors if not provided.
    # Copy this back to the problem as it is used in plotting.
    problem.data_x = controller.data_x
    problem.data_y = controller.data_y
    problem.data_e = controller.data_e

    for i in range(len(controller.functions)):
        controller.function_id = i

        results_problem, best_fit = benchmark(controller=controller,
                                              minimizers=user_input.minimizers,
                                              num_runs=num_runs)

        if best_fit is not None:
            # Make the plot of the best fit
            plots.make_plots(problem=problem,
                             best_fit=best_fit,
                             count=i + 1,
                             group_results_dir=user_input.group_results_dir)

        results_fit_problem.append(results_problem)

    return results_fit_problem


def benchmark(controller, minimizers, num_runs):
    """
    Fit benchmark one problem, with one function definition and all
    the selected minimizers, using the chosen fitting software.

    @param controller :: The software controller for the fitting
    @param minimizers :: array of minimizers used in fitting
    @param num_runs :: number of times controller.fit() is run to
                       generate an average runtime

    @returns :: nested array of result objects, per minimizer
                and data object for the best fit data
    """
    min_chi_sq, best_fit = None, None
    results_problem = []

    for minimizer in minimizers:
        controller.minimizer = minimizer

        controller.prepare()

        init_function_def = controller.problem.get_function_def(
            params=controller.initial_params,
            function_id=controller.function_id)
        try:
            runtime = timeit.timeit(controller.fit, number=num_runs) / num_runs
        except Exception as e:
            print(e.message)
            controller.success = False
            runtime = np.inf

        controller.cleanup()

        fin_function_def = controller.problem.get_function_def(
            params=controller.final_params,
            function_id=controller.function_id)

        if not controller.success:
            chi_sq = np.nan
            status = 'failed'
        else:
            chi_sq = misc.compute_chisq(fitted=controller.results,
                                        actual=controller.data_y,
                                        errors=controller.data_e)
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
