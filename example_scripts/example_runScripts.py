"""
Script that runs the fitbenchmarking tool with various problems and minimizers.
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
# ==============================================================================

from __future__ import (absolute_import, division, print_function)

import os
import sys
# Avoid reaching the maximum recursion depth by setting recursion limit
sys.setrecursionlimit(10000)

# Insert path to where the scripts are located, relative to
# the example_scripts folder
current_path = os.path.dirname(os.path.realpath(__file__))
fitbenchmarking_path = os.path.abspath(os.path.join(current_path, os.pardir))
scripts_path = os.path.join(fitbenchmarking_path, 'fitbenchmarking')
sys.path.insert(0, scripts_path)

from fitting_benchmarking import do_fitting_benchmark as fitBenchmarking
from results_output import save_results_tables as printTables


minimizers = ['BFGS', 'Conjugate gradient (Fletcher-Reeves imp.)',
              'Conjugate gradient (Polak-Ribiere imp.)',
              'Damped GaussNewton',
              'Levenberg-Marquardt', 'Levenberg-MarquardtMD',
              'Simplex','SteepestDescent',
              'Trust Region']

# Parameters of how the final tables are colored
# e.g. lower that 1.1 -> light yellow, higher than 3 -> dark red
color_scale = [(1.1, 'ranking-top-1'),
               (1.33, 'ranking-top-2'),
               (1.75, 'ranking-med-3'),
               (3, 'ranking-low-4'),
               (float('nan'), 'ranking-low-5')]


benchmark_problems_dir = os.path.join(fitbenchmarking_path,
                                      'benchmark_problems')

nist_data_dir = os.path.join(benchmark_problems_dir,
                             'NIST_nonlinear_regression')
neutron_data_dir = os.path.join(benchmark_problems_dir,
                                'Neutron_data')

# Modify results_dir to specify where the results of the fit should be saved
# If left as None, they will be saved in a "results" folder in the working dir
# When specifying a results_dir, please GIVE THE FULL PATH
# If the full path is not given and the results_dir name is valid
#  ../fitbenchmarking/fitbenchmarking/ is taken as the path
results_dir = None

# Whether to use errors in the fitting process
use_errors = True

for run_data in ["neutron", "nist"]:

    if run_data == "neutron":
        group_suffix_names = ['neutron_data']
        group_names = ["Neutron data"]
        results_per_group, results_dir = \
        fitBenchmarking(data_dir=neutron_data_dir,
                        minimizers=minimizers,
                        use_errors=use_errors,
                        results_dir=results_dir)
    elif run_data == "nist":
        group_names = ['NIST, "lower" difficulty', 'NIST, "average" difficulty',
                       'NIST, "higher" difficulty']
        group_suffix_names = ['nist_lower', 'nist_average', 'nist_higher']
        results_per_group, results_dir = \
        fitBenchmarking(data_dir=nist_data_dir,
                        minimizers=minimizers,
                        use_errors=use_errors,
                        results_dir=results_dir)
    else:
        raise RuntimeError("Invalid run_data, please check if the array"
                           "contains the correct names!")

    for idx, group_results in enumerate(results_per_group):
        printTables(minimizers, group_results,
                    group_name=group_suffix_names[idx],
                    use_errors=use_errors, color_scale=color_scale,
                    results_dir=results_dir)
