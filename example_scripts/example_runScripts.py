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
from fitbenchmarking.utils.options import Options


def main(args):
    # Find the options file
    current_path = os.path.dirname(os.path.realpath(__file__))
    if len(args) > 1:
        # Read custom minimizer options from file
        options_file = os.path.join(current_path, args[1])
        options = Options(options_file)
    else:
        options = Options()

    ############################################################
    # User defined options #####################################
    ############################################################
    options.software = ['scipy']
    # options.minimizers = {"scipy": ["lm", "trf", "dogbox"],
    #                      "sasview": ["amoeba", "lm", "newton", "de", "mp"]}
    # options.use_errors = True
    # options.results_dir = None
    # options.colour_scale = [(1.1, 'ranking-top-1'),
    #                        (1.33, 'ranking-top-2'),
    #                        (1.75, 'ranking-med-3'),
    #                        (3, 'ranking-low-4'),
    #                        (float('nan'), 'ranking-low-5')]
    ############################################################

    # ADD WHICH PROBLEM SETS TO TEST AGAINST HERE
    # Do this, in this example file, by selecting sub-folders in
    # benchmark_probs_dir
    # problem_sets = ["CUTEst",
    #                 "Muon",
    #                 "Neutron",
    #                 "NIST/average_difficulty",
    #                 "NIST/high_difficulty",
    #                 "NIST/low_difficulty",
    #                 "SAS_modelling/1D",
    #                 "simple_tests"]
    problem_sets = ["NIST/average_difficulty"]

    # Benchmark problem directories
    fitbenchmarking_folder = os.path.abspath(
        os.path.join(current_path, os.pardir))
    benchmark_probs_dir = os.path.join(fitbenchmarking_folder,
                                       'benchmark_problems')

    for sub_dir in problem_sets:
        # generate group label/name used for problem set
        label = sub_dir.replace('/', '_')

        # Create full path for the directory that holds a group of
        # problem definition files
        data_dir = os.path.join(benchmark_probs_dir, sub_dir)

        test_data = glob.glob(data_dir + '/*.*')

        if test_data == []:
            print('Problem set {} not found'.format(sub_dir))
            continue

        print('\nRunning the benchmarking on the {} problem set\n'.format(
            label))
        results = fitbenchmark_group(group_name=label,
                                     options=options,
                                     data_dir=data_dir)

        print('\nProducing output for the {} problem set\n'.format(label))
        # Display the runtime and accuracy results in a table
        save_results_tables(group_name=label,
                            results=results,
                            options=options)

        print('\nCompleted benchmarking for {} problem set\n'.format(sub_dir))


if __name__ == '__main__':
    main(sys.argv)
