"""
Fit benchmark one problem functions.
"""

from __future__ import absolute_import, division, print_function

import numpy as np
import timeit
import warnings

from fitbenchmarking.fitting import misc
from fitbenchmarking.fitting.controllers.controller_factory \
    import ControllerFactory
from fitbenchmarking.fitting.plotting import plot_helper, plots


def fitbm_one_prob(problem, options, directory):
    """
    Sets up the controller for a particular problem and fits the models
    provided in the problem object. The best fit, along with the data and a
    starting guess is then plotted on a visual display page.

    :param problem: a problem object containing information used in fitting
    :type problem: FittingProblem
    :param options: all the information specified by the user
    :type options: fitbenchmarking.utils.options.Options
    :param directory: The directory to store the results in
    :type directory: string

    :returns: nested array of result objects, per function definition
               containing the fit information
    :rtype: list
    """

    results = []

    software = options.software
    if not isinstance(software, list):
        software = [software]

    for s in software:
        try:
            minimizers = options.minimizers[s]
        except KeyError:
            raise ValueError(
                'Minimizers could not be found for software: {}'.format(s))

        controller_cls = ControllerFactory.create_controller(software=s)
        controller = controller_cls(problem=problem,
                                    use_errors=options.use_errors)

        # The controller reformats the data to fit within a start- and end-x
        # bound
        # It also estimates errors if not provided.
        # Copy this back to the problem as it is used in plotting.
        problem.data_x = controller.data_x
        problem.data_y = controller.data_y
        problem.data_e = controller.data_e

        for i in range(len(controller.starting_values)):
            if len(results) <= i:
                results.append({})

            controller.parameter_set = i

            problem_result, best_fit = benchmark(controller=controller,
                                                 minimizers=minimizers,
                                                 options=options)
            if best_fit is not None:
                # Make the plot of the best fit
                plots.make_plots(problem=problem,
                                 best_fit=best_fit,
                                 count=i + 1,
                                 group_results_dir=directory)

            results[i][s] = problem_result

    return results


def benchmark(controller, minimizers, options):
    """
    Fit benchmark one problem, with one function definition and all
    the selected minimizers, using the chosen fitting software.

    :param controller: The software controller for the fitting
    :type controller: Object derived from BaseSoftwareController
    :param minimizers: array of minimizers used in fitting
    :type minimizers: list
    :param options: all the information specified by the user
    :type options: fitbenchmarking.utils.options.Options

    :returns: tuple(results_problem, best_fit) nested array of
              result objects, per minimizer and data object for
              the best fit data
    :rtype: (list of FittingResult, plot_helper.data instance)
    """
    min_chi_sq, best_fit = None, None
    results_problem = []
    num_runs = options.num_runs
    min_chi_sq = np.inf
    min_runtime = np.inf
    for minimizer in minimizers:
        controller.minimizer = minimizer

        init_function_def = controller.problem.get_function_def(
            params=controller.initial_params)

        try:
            # Calls timeit repeat with repeat = num_runs and number = 1
            runtime_list = \
                timeit.Timer(setup=controller.prepare,
                             stmt=controller.fit).repeat(num_runs, 1)
            runtime = sum(runtime_list) / num_runs

        # Catching all exceptions as this means runtime cannot be calculated
        # pylint: disable=broad-except
        except Exception as excp:
            print(str(excp))
            controller.success = False
            runtime = np.inf

        controller.cleanup()

        fin_function_def = controller.problem.get_function_def(
            params=controller.final_params)

        if not controller.success:
            chi_sq = np.nan
            status = 'failed'
        else:
            ratio = np.max(runtime_list) / np.min(runtime_list)
            tol = 4
            if ratio > tol:
                warnings.warn('The ratio of the max time to the min is {0}'
                              ' which is  larger than the tolerance of {1},'
                              ' which may indicate that caching has occurred'
                              ' in the timing results'.format(ratio, tol))
            chi_sq = misc.compute_chisq(fitted=controller.results,
                                        actual=controller.data_y,
                                        errors=controller.data_e)
            status = 'success'

        if min_chi_sq is None:
            min_chi_sq = chi_sq + 1

        if chi_sq < min_chi_sq:
            min_chi_sq = chi_sq
            index = controller.sorted_index
            best_fit = plot_helper.data(name=minimizer,
                                        x=controller.data_x,
                                        y=controller.results,
                                        E=controller.data_e,
                                        sorted_index=index)

        individual_result = \
            misc.create_result_entry(options=options,
                                     problem=controller.problem,
                                     status=status,
                                     chi_sq=chi_sq,
                                     runtime=runtime,
                                     minimizer=minimizer,
                                     ini_function_def=init_function_def,
                                     fin_function_def=fin_function_def)
        if chi_sq < min_chi_sq:
            min_chi_sq = chi_sq
        if runtime < min_runtime:
            min_runtime = runtime
        results_problem.append(individual_result)

    for r in results_problem:
        r.min_chi_sq = min_chi_sq
        r.min_runtime = min_runtime
        r.set_normalised_data()
        r.set_colour_scale()

    return results_problem, best_fit
