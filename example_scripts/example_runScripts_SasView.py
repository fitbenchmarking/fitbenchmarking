

from __future__ import (absolute_import, division, print_function)
import os
import sys

# Avoid reaching the maximum recursion depth by setting recursion limit
# This is useful when running multiple data set benchmarking
# Otherwise recursion limit is reached and the interpreter throws an error
sys.setrecursionlimit(10000)

# Insert path to where the scripts are located, relative to
# the example_scripts folder
current_path = os.path.dirname(os.path.realpath(__file__))
fitbenchmarking_folder = os.path.abspath(os.path.join(current_path, os.pardir))
scripts_folder = os.path.join(fitbenchmarking_folder, 'fitbenchmarking')
sys.path.insert(0, scripts_folder)

from fitting_benchmarking import do_fitting_benchmark as fitBenchmarking
from results_output import save_results_tables as printTables

# SPECIFY THE SOFTWARE/PACKAGE CONTAINING THE MINIMIZERS YOU WANT TO BENCHMARK
# software = 'mantid'
software = 'sasview'
software_options = {'software': software}

# User defined minimizers
# custom_minimizers = {"mantid": ["BFGS", "Simplex"],
              # "scipy": ["lm", "trf", "dogbox"]}
custom_minimizers = None

# SPECIFY THE MINIMIZERS YOU WANT TO BENCHMARK, AND AS A MINIMUM FOR THE SOFTWARE YOU SPECIFIED ABOVE
if len(sys.argv) > 1:
  # Read custom minimizer options from file
  software_options['minimizer_options'] = current_path + sys.argv[1]
elif custom_minimizers:
  # Custom minimizer options:
  software_options['minimizer_options'] = custom_minimizers
else:
  # Using default minimizers from
  # fitbenchmarking/fitbenchmarking/minimizers_list_default.json
  software_options['minimizer_options'] = None


print(software_options['minimizer_options'])

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
# "Muon_data" works for mantid minimizers
# problem_sets = ["Neutron_data", "NIST/average_difficulty"]
# problem_sets = ["CUTEst", "Muon_data", "Neutron_data", "NIST/average_difficulty", "NIST/high_difficulty", "NIST/low_difficulty"]
problem_sets = ["Neutron_data"]
for sub_dir in problem_sets:
  # generate group label/name used for problem set
  label = sub_dir.replace('/', '_')

  # Problem data directory
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
# from sasmodels.core import load_model
# from sasmodels.bumps_model import Model, Experiment
# from sasmodels.data import load_data
#
# from bumps.names import *
# from bumps.fitters import fit
# from bumps.formatnum import format_uncertainty
#
# import matplotlib.pyplot as plt
#
# import os
#
# current_path = os.path.realpath(__file__)
# dir_path = os.path.dirname(current_path)
# main_dir = os.path.dirname(dir_path)
# oneD_data_dir = os.path.join(main_dir, 'benchmark_problems', '1D_data', 'cyl_400_20.txt')
#
#
# test_data = load_data(oneD_data_dir)
# kernel = load_model('cylinder')
#
# #We set some errors for demonstration
# test_data.dy = 0.2*test_data.y
#
# pars = dict(radius=35,
#             length=350,
#             background=0.0,
#             scale=1.0,
#             sld=4.0,
#             sld_solvent=1.0)
# print(pars)
# model = Model(kernel, **pars)
#
# # SET THE FITTING PARAMETERS
# model.radius.range(1, 50)
# model.length.range(1, 500)
#
# M = Experiment(data=test_data, model=model)
# problem = FitProblem(M)
# print("Initial chisq", problem.chisq_str())
# problem.plot()
# # pylab.show()
# plt.show()
#
# result = fit(problem, method='amoeba')
# print("Final chisq", problem.chisq_str())
# for k, v, dv in zip(problem.labels(), result.x, result.dx):
#     print(k, ":", format_uncertainty(v, dv))
# problem.plot()
# plt.show()
