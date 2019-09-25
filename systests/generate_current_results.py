"""
Generates the current results outputted by the script in a folder titled
results.
"""

from __future__ import (absolute_import, division, print_function)

import os
import sys

current_path = os.path.dirname(os.path.realpath(__file__))
fitbenchmarking_path = os.path.abspath(os.path.join(current_path, os.pardir))
scripts_path = os.path.join(fitbenchmarking_path, 'fitbenchmarking')
sys.path.insert(0, scripts_path)

from fitting_benchmarking import do_fitting_benchmark as fitBenchmarking
from results_output import save_results_tables as printTables


# SPECIFY THE SOFTWARE/PACKAGE CONTAINING THE MINIMIZERS YOU WANT TO BENCHMARK
# SPECIFY THE SOFTWARE/PACKAGE CONTAINING THE MINIMIZERS YOU WANT TO BENCHMARK
software = 'scipy'
software_options = {'software': software, 'minimizer_options': None}

color_scale = [(1.1, 'ranking-top-1'),
               (1.33, 'ranking-top-2'),
               (1.75, 'ranking-med-3'),
               (3, 'ranking-low-4'),
               (float('nan'), 'ranking-low-5')]


benchmark_probs_dir = os.path.join(fitbenchmarking_path,
                                   'benchmark_problems')

results_dir = None
use_errors = True

problem_sets = ["Neutron_data", "NIST/low_difficulty",
                "NIST/average_difficulty", "NIST/high_difficulty"]

for sub_dir in problem_sets:
  # generate group label/name used for problem set
  label = sub_dir.replace('/', '_')

  results_dir = None

  # Problem data directory
  data_dir = os.path.join(benchmark_probs_dir, sub_dir)

  # Running the benchmarking on problem set
  results_per_group, results_dir = \
      fitBenchmarking(group_name=label, software_options=software_options,
                      data_dir=data_dir,
                      use_errors=use_errors, results_dir=results_dir)

  # Producing output for the problem set
  for idx, group_results in enumerate(results_per_group):
    # Display the runtime and accuracy results in a table
    printTables(software_options, group_results,
                group_name=label, use_errors=use_errors,
                color_scale=color_scale, results_dir=results_dir)
