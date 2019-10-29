"""
This example script is designed to demonstrate the features of fitbenchmarking to benchmark
the performance of Scipy and SasView minimizers against the NIST-type problem definition files
and the SAS_modelling problems.
"""


from __future__ import (absolute_import, division, print_function)
import os
import sys
import glob

from fitbenchmarking.fitting_benchmarking import fitbenchmark_group
from fitbenchmarking.results_output import save_results_tables


def main(args):
    # SPECIFY THE SOFTWARE/PACKAGE CONTAINING THE MINIMIZERS YOU WANT TO BENCHMARK
    software = ['scipy', 'sasview']
    software_options = {'software': software}

    # User defined minimizers
    # custom_minimizers = {"scipy": ["lm", "trf", "dogbox"],
    #                      "sasview": ["amoeba", "lm", "newton", "de", "pt", "mp"]}
    # None will default to the list on the options file
    custom_minimizers = None

    # SPECIFY THE MINIMIZERS YOU WANT TO BENCHMARK, AND AS A MINIMUM FOR THE SOFTWARE YOU SPECIFIED ABOVE
    current_path = os.path.dirname(os.path.realpath(__file__))
    if len(args) > 1:
        # Read custom minimizer options from file
        software_options['minimizer_options'] = None
        software_options['options_file'] = current_path + args[1]
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
    # problem_sets = ["CUTEst", "Muon", "Neutron", "NIST/average_difficulty", "NIST/high_difficulty", "NIST/low_difficulty",
    #                "SAS_modelling/1D"]

    problem_sets = ["simple_tests"]

    for sub_dir in problem_sets:
        # generate group label/name used for problem set
        label = sub_dir.replace('/', '_')

        # Create full path for the directory that holds a group of problem definition files
        data_dir = os.path.join(benchmark_probs_dir, sub_dir)

        test_data = glob.glob(data_dir + '/*.*')

        if test_data == []:
            print('Problem set {} not found'.format(sub_dir))
            continue

        print('\nRunning the benchmarking on the {} problem set\n'.format(label))
        results, results_dir = \
            fitbenchmark_group(group_name=label,
                               software_options=software_options,
                               data_dir=data_dir,
                               use_errors=use_errors,
                               results_dir=results_dir)

        print('\nProducing output for the {} problem set\n'.format(label))
        # Display the runtime and accuracy results in a table
        save_results_tables(software_options=software_options,
                            results_per_test=results,
                            group_name=label,
                            use_errors=use_errors,
                            color_scale=color_scale,
                            results_dir=results_dir)

        print('\nCompleted benchmarking for {} problem set\n'.format(sub_dir))


if __name__ == '__main__':
    main(sys.argv)
