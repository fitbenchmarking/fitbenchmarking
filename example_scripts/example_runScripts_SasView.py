

from __future__ import (absolute_import, division, print_function)
import os
import sys

# Insert path to where the scripts are located, relative to
# the example_scripts folder
current_path = os.path.dirname(os.path.realpath(__file__))
fitbenchmarking_folder = os.path.abspath(os.path.join(current_path, os.pardir))
scripts_folder = os.path.join(fitbenchmarking_folder, 'fitbenchmarking')
sys.path.insert(0, scripts_folder)
sys.path.insert(1, fitbenchmarking_folder)

try:
    import bumps
except:
    print('******************************************\n'
          'Bumps is not yet installed on your computer\n'
          'To install, type the following command:\n'
          'python -m pip install bumps\n'
          '******************************************')
    sys.exit()

try:
    import sasmodels.data
except:
    print('******************************************\n'
          'sasmodels is not yet installed on your computer\n'
          'To install, type the following command:\n'
          'python -m pip install sasmodels\n'
          '******************************************')
    sys.exit()

try:
    import sas
except:
    print('******************************************\n'
          'sas is not yet installed on your computer\n'
          'To install, clone a version of SasView from https://github.com/SasView/sasview\n'
          'After that, copy a folder called "sas" inside the sub-folder sasview/src to the fitbenchmarking directory\n'
          '******************************************')
    sys.exit()

from fitting_benchmarking import do_fitting_benchmark as fitBenchmarking
from results_output import save_results_tables as printTables

# SPECIFY THE SOFTWARE/PACKAGE CONTAINING THE MINIMIZERS YOU WANT TO BENCHMARK
software = ['sasview']
software_options = {'software': software}

# User defined minimizers
custom_minimizers = {"mantid": ["BFGS", "Simplex"],
              "scipy": ["lm", "trf", "dogbox"],
              "sasview": ["amoeba"]}
# custom_minimizers = None
# "amoeba", "lm", "newton", "de", "pt", "mp"

# SPECIFY THE MINIMIZERS YOU WANT TO BENCHMARK, AND AS A MINIMUM FOR THE SOFTWARE YOU SPECIFIED ABOVE
if len(sys.argv) > 1:
  # Read custom minimizer options from file
  software_options['minimizer_options'] = None
  software_options['options_file'] = current_path + sys.argv[1]
elif custom_minimizers:
  # Custom minimizer options:
  software_options['minimizer_options'] = custom_minimizers
else:
  # Using default minimizers from
  # fitbenchmarking/fitbenchmarking/fitbenchmarking_default_options.json
  software_options['minimizer_options'] = None

# Benchmark problem directories
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
problem_sets = ["SAS_modelling/1D"]

for sub_dir in problem_sets:
  # generate group label/name used for problem set
  label = sub_dir.replace('/', '_')

  # Create full path for the directory that holds a group of problem definition files
  data_dir = os.path.join(benchmark_probs_dir, sub_dir)

  print('\nRunning the benchmarking on the {} problem set\n'.format(label))
  results_per_group, results_dir = fitBenchmarking(group_name=label, software_options=software_options,
                                                   data_dir=data_dir,
                                                   use_errors=use_errors, results_dir=results_dir)

  print('\nProducing output for the {} problem set\n'.format(label))
  for idx, group_results in enumerate(results_per_group):
    # Display the runtime and accuracy results in a table
    printTables(software_options, group_results,
                group_name=label, use_errors=use_errors,
                color_scale=color_scale, results_dir=results_dir)

  print('\nCompleted benchmarking for {} problem set\n'.format(sub_dir))
