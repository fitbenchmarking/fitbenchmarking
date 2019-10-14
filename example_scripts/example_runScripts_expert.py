"""
Script that runs the fitbenchmarking tool with various problems and minimizers
for an expert user. This script will show exactly what fitbenchmarking is doing
at each stage to enable a user to customize their problem to their needs.
"""


from __future__ import (absolute_import, division, print_function)
import os
import sys
import glob

from fitbenchmarking.fitting_benchmarking import _benchmark
from fitbenchmarking.utils import misc
from fitbenchmarking.utils import create_dirs
from fitbenchmarking.results_output import save_tables, generate_tables, \
    create_acc_tbl, create_runtime_tbl
from fitbenchmarking.resproc import visual_pages


def main(argv):
    # SPECIFY THE SOFTWARE/PACKAGE CONTAINING THE MINIMIZERS YOU WANT TO BENCHMARK
    software = ['scipy']
    software_options = {'software': software}

    # User defined minimizers
    # custom_minimizers = {"mantid": ["BFGS",
    #                                 "Damped GaussNewton"],
    #                      "scipy": ["lm", "trf"]}
    custom_minimizers = None

    # SPECIFY THE MINIMIZERS YOU WANT TO BENCHMARK, AND AS A MINIMUM FOR THE SOFTWARE YOU SPECIFIED ABOVE
    current_path = os.path.dirname(os.path.realpath(__file__))
    if len(argv) > 1:
        # Read custom minimizer options from file
        software_options['minimizer_options'] = None
        software_options['options_file'] = current_path + argv[1]
    elif custom_minimizers:
        # Custom minimizer options:
        software_options['minimizer_options'] = custom_minimizers
    else:
        # Using default minimizers from
        # fitbenchmarking/fitbenchmarking/fitbenchmarking_default_options.json
        software_options['minimizer_options'] = None

    # Benchmark problem directories
    fitbenchmarking_folder = os.path.abspath(os.path.join(current_path, os.pardir))
    benchmark_probs_dir = os.path.join(fitbenchmarking_folder,
                                       'benchmark_problems')

    """
    Modify results_dir to specify where the results of the fit should be saved
    If left as None, they will be saved in a "results" folder in the working dir
    If the full path is not given results_dir is created relative to the working dir
    """
    results_dir = None

    # Whether to use errors in the fitting process
    use_errors = True

    # Parameters of how the final tables are colored
    # e.g. lower that 1.1 -> light yellow, higher than 3 -> dark red
    # Change these values to suit your needs
    color_scale = [(1.1, 'ranking-top-1'),
                   (1.33, 'ranking-top-2'),
                   (1.75, 'ranking-med-3'),
                   (3, 'ranking-low-4'),
                   (float('nan'), 'ranking-low-5')]

    # ADD WHICH PROBLEM SETS TO TEST AGAINST HERE
    # Do this, in this example file, by selecting sub-folders in benchmark_probs_dir
    # "Muon_data" works for mantid minimizers
    # problem_sets = ["Neutron_data", "NIST/average_difficulty"]
    problem_sets = ["CUTEst"]
    for sub_dir in problem_sets:
        # generate group group_name/name used for problem set
        group_name = sub_dir.replace('/', '_')

        # Create full path for the directory that holds a group of problem definition files
        data_dir = os.path.join(benchmark_probs_dir, sub_dir)

        test_data = glob.glob(data_dir + '/*.*')

        if test_data == []:
            print('Problem set {} not found'.format(sub_dir))
            continue

        print('\nRunning the benchmarking on the {} problem set\n'.format(group_name))

        # Processes software_options dictionary into Fitbenchmarking format
        minimizers, software = misc.get_minimizers(software_options)

        # Sets up the problem group specified by the user by providing
        # a respective data directory.
        problem_group = misc.get_problem_files(data_dir)

        # Create output dirs
        results_dir = create_dirs.results(results_dir)
        group_results_dir = create_dirs.group_results(results_dir, group_name)

        # All parameters inputted by the user are stored in an object
        user_input = misc.save_user_input(software, minimizers, group_name,
                                          group_results_dir, use_errors)

        # Loops through group of problems and benchmark them
        prob_results = _benchmark(user_input, problem_group)

        print('\nProducing output for the {} problem set\n'.format(group_name))

        # Creates the results directory where the tables are located
        tables_dir = create_dirs.restables_dir(results_dir, group_name)

        if isinstance(software, list):
            minimizers = sum(minimizers, [])

        # Creates the problem names with links to the visual display pages
        # in rst
        linked_problems = visual_pages.create_linked_probs(prob_results,
                                                           group_name, results_dir)

        # Generates accuracy and runtime tables and summary tables
        acc_rankings, runtimes, sum_cells_acc, sum_cells_runtime = generate_tables(prob_results, minimizers)

        # Creates an accuracy table
        acc_tbl = create_acc_tbl(minimizers, linked_problems, acc_rankings, use_errors, color_scale)

        # Creates an runtime table
        runtime_tbl = create_runtime_tbl(minimizers, linked_problems, runtimes, use_errors, color_scale)

        # Saves accuracy minimizer results
        save_tables(tables_dir, acc_tbl, use_errors, group_name, 'acc')

        # Saves runtime minimizer results
        save_tables(tables_dir, runtime_tbl, use_errors, group_name, 'runtime')

        print('\nCompleted benchmarking for {} problem set\n'.format(sub_dir))


if __name__ == '__main__':
    main(sys.argv)
