"""
Classes and utility functions to support benchmarking of fitting minimizers in
Mantid or other packages useable from Python.  These benchmarks are
focused on comparing different minimizers in terms of accuracy and
computation time.
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
# File change history is stored at: <https://github.com/mantidproject/mantid>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>

from __future__ import (absolute_import, division, print_function)


import os, sys, shutil
import time, glob

import numpy as np
import mantid.simpleapi as msapi

import input_parsing as iparsing
import test_result
from plotHelper import *
from logging_setup import logger



def do_fitting_benchmark(data_dir, minimizers=None, use_errors=True,
                         results_dir=None):
    """
    Run a fit minimizer benchmark against groups of fitting problems.

    Unless group directories of fitting problems are specified
    no fitting benchmarking is done. The same is valid for the minimizers.

    @param data_dir :: directory where the data is located
    @param minimizers :: list of minimizers to test
    @param use_errors :: whether to use observational errors as weights
                         in the cost function
    @param results_dir :: where the results directory is located/its name
    """

    results_dir = setup_results_dir(results_dir)

    problem_groups = {}
    if 'NIST' in data_dir:
        problem_groups['nist'] = get_nist_problem_files(data_dir)
    elif 'Neutron' in data_dir:
        problem_groups['neutron'] = get_neutron_problem_files(data_dir)
    else:
        raise NameError("Data directory not recognised!")

    prob_results = None
    for group_name in problem_groups:
        group_results_dir = setup_group_results_dir(results_dir, group_name)
        prob_results = [do_fitting_benchmark_group(group_name,
                                                   group_results_dir,
                                                   problem_block, minimizers,
                                                   use_errors=use_errors)
                        for problem_block in problem_groups[group_name]]

    return prob_results, results_dir


def do_fitting_benchmark_group(group_name, group_results_dir, problem_files,
                               minimizers, use_errors=True):
    """
    Applies minimizers to a group (collection) of test problems.
    For example the collection of all NIST problems

    @param group_name :: name of the group
    @param group_results_dir :: directory in which the group results
                                are stored
    @param problem_files :: a list of list of files that define a group of
                            test problems. For example all the NIST files
                            sub-groupped according to level of fitting
                            difficulty, where the lowest list level list
                            the file names
    @param minimizers :: list of minimizers to test
    @param use_errors :: whether to use observational errors as weights
                         in the cost function

    @returns :: problem definitions loaded from the files, and results of
                running them with the minimizers requested
    """

    results_per_problem = []
    for prob_file in problem_files:
        prob = parse_problem_file(group_name, prob_file)
        results_prob = do_fitting_benchmark_one_problem(prob, group_results_dir,
                                                        minimizers, use_errors)
        results_per_problem.extend(results_prob)

    return results_per_problem


def do_fitting_benchmark_one_problem(prob, group_results_dir, minimizers,
                                     use_errors=True, count=0):
    """
    One problem with potentially several starting points, returns a list
    (start points) of lists (minimizers).

    @param prob :: fitting problem
    @param group_results_dir :: directory of results for the teste group
    @param minimizers :: list of minimizers to evaluate/compare
    @param use_errors :: whether to use observational errors when evaluating
                         accuracy (in the cost function)
    @param count :: the current count for the number of different start
                    values for a given problem
    @param previous_name :: name of the previous problem
    """

    previous_name = "none"
    max_possible_float = sys.float_info.max
    wks, cost_function = prepare_wks_cost_function(prob, use_errors)
    function_definitions = get_function_definitions(prob)
    results_fit_problem = []

    for fit_function in function_definitions:

        # Store the minimum chi_squared found, initialised to max value
        min_chi_sq = max_possible_float
        # Holds the data points of the best fit
        best_fit = None
        # Holds the starting guess data points of the fit
        results_problem = []

        for minimizer_name in minimizers:
            chi_sq = np.nan
            runtime = np.nan

            t_start = time.clock()
            (status, fit_wks,
             params, errors) = run_fit(wks, prob, function=fit_function,
                                       minimizer=minimizer_name,
                                       cost_function=cost_function)
            t_end = time.clock()

            if not status == 'failed':
                (chi_sq, min_chi_sq,
                 best_fit) = calculate_chi_sq(fit_wks, min_chi_sq, best_fit,
                                              minimizer_name)
                runtime = t_end - t_start

            result = test_result.FittingTestResult()
            result.problem = prob
            result.fit_status = status
            result.params = params
            result.errors = errors
            result.chi_sq = chi_sq
            result.runtime = runtime
            result.minimizer = minimizer_name
            result.function_def = fit_function
            results_problem.append(result)

            logger.info("*** Using minimizer {0}, Status: {1}".
                        format(minimizer_name, status))

        results_fit_problem.append(results_problem)

        if not best_fit is None:
            previous_name, count = make_plots(prob, group_results_dir, best_fit,
                                              wks, previous_name, count,
                                              fit_function)

    return results_fit_problem


def calculate_chi_sq(fit_wks, min_chi_sq, best_fit, minimizer_name):
    """ Function that calculates chi squared given a vector of differences
        between the actual data points and the data points of the fit.
        It also produces a value of the minimum chi_sq, the best fit, minimizer
        used to obtain the best fit and the function.

        @param fit_wks :: vector of differences
        @param min_chi_sq :: minimum chi squared value
        @param best_fit :: data points of the best fit
        @param minimizer_name :: minimizer used to obtain the best fit
        @param best_function :: function used to obtain the best fit
    """

    if fit_wks:
        chi_sq = np.sum(np.square(fit_wks.readY(2)))
        if chi_sq < min_chi_sq:
            tmp = msapi.ConvertToPointData(fit_wks)
            best_fit = data(minimizer_name, tmp.readX(1), tmp.readY(1))
            min_chi_sq = chi_sq
    else:
        chi_sq = np.nan
        logger.warning("No output fit workspace")

    logger.info("Chi_sq: {0}".format(chi_sq))

    return chi_sq, min_chi_sq, best_fit


def make_plots(prob, visuals_dir, best_fit, wks, previous_name, count,
               fit_function):
    """
    Makes a plot of the best fit considering multiple starting points of a
    problem.

    @param prob: fitting problem
    @param best_fit :: best fit data
    @param wks :: workspace with problem data
    @param previous_name :: name of the previous problem
    @param count :: number of different starting points for one problem
    @param fit_function :: fitting function
    """

    # Set up the directories to organise the figures in
    support_pages_dir = os.path.join(visuals_dir, "support_pages_dir")
    if not os.path.exists(support_pages_dir):
            os.makedirs(support_pages_dir)
    figures_dir = os.path.join(support_pages_dir, "figures")
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)

    if prob.name == previous_name:
        count += 1
    else:
        count = 1
        previous_name = prob.name

    raw_data = get_data_points(wks)
    make_data_plot(prob.name, raw_data, count, figures_dir)
    make_best_fit_plot(prob.name, raw_data, best_fit, count, figures_dir)
    make_starting_guess_plot(raw_data, fit_function, wks, prob, count,
                             figures_dir)

    return previous_name, count


def get_data_points(wks):
    """
    Function that returns the data points as they are in wks.

    @param wks :: workspace that contains data
    """

    tmp = msapi.ConvertToPointData(wks)
    xData = tmp.readX(0)
    yData = tmp.readY(0)
    eData = tmp.readE(0)
    raw_data = data("Data", xData, yData, eData)
    raw_data.showError = True
    raw_data.linestyle = ''

    return raw_data


def make_data_plot(name, raw_data, count, figures_dir):
    """
    Function that makes a scatter plot of a set of given data points.

    @param raw_data :: array that contains the raw data point information
    @param previous_name :: name of the previous set of data points
    @param figures_dir :: directory that holds the figures
    """

    data_fig=plot()
    data_fig.add_data(raw_data)
    data_fig.labels['y'] = "Arbitrary units"
    data_fig.labels['x'] = "Time ($\mu s$)"
    data_fig.labels['title'] = name + " " + str(count)
    data_fig.title_size=10
    data_fig.make_scatter_plot(figures_dir + os.sep + "Data Plot " + name +
                               " " + str(count)+".png")


def make_best_fit_plot(name, raw_data, best_fit, count, figures_dir):
    """
    Function that make a plot of the best fit against the raw data.

    @param raw_data :: array that contains the raw data point information
    @param best_fit :: the data describing the best fit
    @param count :: the starting point number
    @param figures_dir :: directory that holds the figures
    """

    fig=plot()
    fig.add_data(raw_data)
    best_fit.markers=''
    best_fit.linestyle='-'
    best_fit.colour='green'
    best_fit.order_data()
    fig.add_data(best_fit)

    fig.labels['y'] = "Arbitrary units"
    fig.labels['x'] = "Time ($\mu s$)"
    fig.labels['title'] = name + " " + str(count)
    fig.title_size=10
    figure_name = (figures_dir + os.sep + "Fit for " + name + " " +
                   str(count) + ".png")
    fig.make_scatter_plot(figure_name)


def make_starting_guess_plot(raw_data, fit_function, wks, prob, count,
                             figures_dir):
    """
    Function that makes a plot of the starting guess.

    @param raw_data :: array that contains the raw data point information
    @param fit_function :: function that must be fitted
    @param wks :: workspace containing the data points information
    @param prob :: problem object containing all problem information
    @param figures_dir :: directory that holds the figures
    """

    fit_result = msapi.Fit(fit_function, wks, Output='ws_fitting_test',
                           Minimizer='Levenberg-Marquardt',
                           CostFunction='Least squares',IgnoreInvalidData=True,
                           StartX=prob.start_x, EndX=prob.end_x,
                           MaxIterations=0)

    tmp = msapi.ConvertToPointData(fit_result.OutputWorkspace)
    xData = tmp.readX(1)
    yData = tmp.readY(1)
    startData = data("Start Guess", xData, yData)
    startData.order_data()
    startData.colour = "blue"
    startData.markers = ''
    startData.linestyle = "-"
    start_fig = plot()
    start_fig.add_data(raw_data)
    start_fig.add_data(startData)
    start_fig.labels['x'] = "Time ($\mu s$)"
    start_fig.labels['y'] = "Arbitrary units"
    start_fig.labels['title'] = prob.name + " " + str(count)
    start_fig.title_size = 10
    start_figure_name = (figures_dir + os.sep + "start for " + prob.name +
                         " " + str(count) + ".png")
    start_fig.make_scatter_plot(start_figure_name)


def run_fit(wks, prob, function, minimizer='Levenberg-Marquardt',
            cost_function='Least squares'):
    """
    Fits the data in a workspace with a function, using the algorithm Fit.
    Importantly, the option IgnoreInvalidData is enabled.
    Check the documentation of Fit for the implications of this.

    @param wks :: MatrixWorkspace with data to fit, in the format expected
                  by the algorithm Fit
    @param prob :: Problem definition
    @param function :: function definition as used in the algorithm Fit
    @param minimizer :: minimizer to use in Fit
    @param cost_function :: cost function to use in Fit

    @returns the fitted parameter values and error estimates for these
    """

    fit_result = None
    param_tbl = None

    try:
        # When using 'Least squares' (weighted by errors),
        # ignore nans and zero errors, but don't ignore them
        # when using 'Unweighted least squares'
        # as that would ignore all values!
        ignore_invalid = cost_function == 'Least squares'

        # Note the ugly adhoc exception.
        # We need to reconsider these WISH problems:
        if 'WISH17701' in prob.name:
            ignore_invalid = False

        fit_result = msapi.Fit(function, wks, Output='ws_fitting_test',
                               Minimizer=minimizer,
                               CostFunction=cost_function,
                               IgnoreInvalidData=ignore_invalid,
                               StartX=prob.start_x, EndX=prob.end_x)

    except (RuntimeError, ValueError) as err:
        logger.error("Warning, fit probably failed. Going on. Error: " +
                     str(err))


    if fit_result is None:
        return 'failed', None, None, None
    else:
        param_tbl = fit_result.OutputParameters
        if param_tbl:
            params = param_tbl.column(1)[:-1]
            errors = param_tbl.column(2)[:-1]
        else:
            params = None
            errors = None

        return (fit_result.OutputStatus, fit_result.OutputWorkspace, params,
                errors)


def prepare_wks_cost_function(prob, use_errors):
    """
    Build a workspace ready for Fit() and a cost function string according
    to the problem definition.
    """

    if use_errors:
        data_e = None
        if prob.data_pattern_obs_errors is None:
            # Fake observational errors - no correct answer (since we do not
            # know where the y values come from), but we are taking
            # the errrors to be the square root of the absolute y value
            data_e = np.sqrt(abs(prob.data_y))
        else:
            data_e = prob.data_pattern_obs_errors

        wks = msapi.CreateWorkspace(DataX=prob.data_x, DataY=prob.data_y,
                                    DataE=data_e)
        cost_function = 'Least squares'
    else:
        wks = msapi.CreateWorkspace(DataX=prob.data_x, DataY=prob.data_y)
        cost_function = 'Unweighted least squares'

    return wks, cost_function


def get_function_definitions(prob):
    """
    Produces function definition strings (as a full definition in
    muparser format, including the function and the initial values for
    the parameters), one for every different starting point defined in
    the test problem.

    @param prob :: fitting test problem object

    @returns :: list of function strings ready for Fit()
    """

    function_defs = []
    if prob.starting_values:
        starting_values = len(prob.starting_values[0][1])
        for start_idx in range(0, starting_values):
            starting_value_str = ''
            for param in prob.starting_values:
                starting_value_str += ('{0}={1},'.
                                        format(param[0], param[1][start_idx]))
            function_defs.append("name=UserFunction, Formula={0}, {1}".
                                 format(prob.equation, starting_value_str))
    else:
        # Equation from a neutron data spec file ready to be used
        function_defs.append(prob.equation)

    return function_defs


def get_nist_problem_files(search_dir):
    """
    Group the NIST problem files into separeate blocks according
    to assumed fitting different levels: lower, average,
    higher.

    @returns :: list of list of problem files
    """

    # Grouped by "level of difficulty"
    nist_lower = ['Misra1a.dat', 'Chwirut2.dat', 'Chwirut1.dat', 'Lanczos3.dat',
                  'Gauss1.dat', 'Gauss2.dat', 'DanWood.dat', 'Misra1b.dat']
    nist_average = ['Kirby2.dat', 'Hahn1.dat', 'MGH17.dat', 'Lanczos1.dat',
                    'Lanczos2.dat', 'Gauss3.dat', 'Misra1c.dat', 'Misra1d.dat',
                    'ENSO.dat']
    nist_higher = ['MGH09.dat', 'Thurber.dat', 'BoxBOD.dat', 'Rat42.dat',
                   'MGH10.dat', 'Eckerle4.dat', 'Rat43.dat', 'Bennett5.dat']

    nist_lower_files = [os.path.join(search_dir, fname)
                        for fname in nist_lower]
    nist_average_files = [os.path.join(search_dir, fname)
                          for fname in nist_average]
    nist_higher_files = [os.path.join(search_dir, fname)
                         for fname in nist_higher]
    problem_files = [nist_lower_files, nist_average_files, nist_higher_files]

    return problem_files


def get_neutron_problem_files(search_dir):
    """
    Gets all the neutron problem files in search_dir.

    @param search_dir :: directory in which the neutron problem files
                         should be located
    """
    search_str = os.path.join(search_dir, "*.txt")
    probs = glob.glob(search_str)
    probs.sort()

    for problem in probs:
        logger.info(problem)

    return [probs]


def parse_problem_file(group_name, prob_file):
    """
    Helper function that calls the parsing and fitting of a specific problem
    file.

    @param group_name :: name of the group of problems
    @param prob_file :: name and path of the problem file
    """

    if group_name in ['nist']:
        prob = iparsing.load_nist_fitting_problem_file(prob_file)
    elif group_name in ['neutron']:
        prob = iparsing.load_neutron_data_fitting_problem_file(prob_file)
    else:
        raise NameError("Could not find group name! Please check if it was"
                        "given correctly...")

    print("* Testing fitting of problem {0}".format(prob.name))
    logger.info("* Testing fitting of problem {0}".format(prob.name))

    return prob


def empty_contents_of_folder(directory):
    """
    Deletes everything in the directory given by directory.

    @param directory :: path to the directory that gets wiped
    """

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def setup_group_results_dir(results_dir, group_name):
    """
    Creates a directory in which results for each problem group are stored.

    @param results_dir :: main directory in which the results are stored
    @param group_name :: name of the group for which the results are obtained
    """

    group_results_dir = os.path.join(results_dir, group_name)
    if os.path.exists(group_results_dir):
        empty_contents_of_folder(group_results_dir)
    else:
        os.makedirs(group_results_dir)

    return group_results_dir


def setup_results_dir(results_dir):
    """
    Creates the results directory with name and path given in results_dir.

    @param results_dir :: name (or path) of the results directory.
    """

    working_dir = os.getcwd()
    if results_dir is None:
        results_dir = os.path.join(working_dir, "results")
    elif not isinstance(results_dir, str):
        TypeError("results_dir must be a string!")
    elif not os.sep in results_dir:
        results_dir = os.path.join(working_dir, results_dir)
    else:
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

    return results_dir
