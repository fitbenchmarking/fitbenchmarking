# script for running fit benchmarking and comparising the relative performance of local minimzers on
# fit problems

import os
from fitting_benchmarking import do_fitting_benchmark as fitBenchmarking
from results_output import print_group_results_tables as printTables

minimizers = ['BFGS', 'Conjugate gradient (Fletcher-Reeves imp.)',
              'Conjugate gradient (Polak-Ribiere imp.)',
              'Damped GaussNewton',
              'Levenberg-Marquardt', 'Levenberg-MarquardtMD',
              'Simplex','SteepestDescent',
              'Trust Region']

group_names = ['NIST, "lower" difficulty', 'NIST, "average" difficulty',
               'NIST, "higher" difficulty', "CUTEst", "Neutron data"]
group_suffix_names = ['nist_lower', 'nist_average', 'nist_higher', 'cutest', 'neutron_data']
color_scale = [(1.1, 'ranking-top-1'),
               (1.33, 'ranking-top-2'),
               (1.75, 'ranking-med-3'),
               (3, 'ranking-low-4'),
               (float('nan'), 'ranking-low-5')]


input_data_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(input_data_dir))
base_problem_files_dir = os.path.join(parent_dir, 'benchmark_problems')

use_errors = True

nist_group_dir = os.path.join(base_problem_files_dir, 'NIST_nonlinear_regression')
cutest_group_dir = os.path.join(base_problem_files_dir, 'CUTEst')
neutron_data_group_dirs = [os.path.join(base_problem_files_dir, 'Neutron_data')]
muon_data_group_dir = [os.path.join(base_problem_files_dir, 'Muon_data')]



# Modify results_dir to specify where the results of the fit should be saved
# If left as None, they will be saved in a "results" folder in the working dir
# When specifying a results_dir, please GIVE THE FULL PATH
results_dir = None

# choice the data to run
run_data = "neutron"

if run_data == "neutron":
    problems, results_per_group = fitBenchmarking(neutron_data_group_dirs=neutron_data_group_dirs,
                                                             minimizers=minimizers, use_errors=use_errors,
                                                             results_dir=results_dir)
elif run_data == "muon":
    group_names = ['MUON']
    group_suffix_names = ['MUON']
    problems, results_per_group = fitBenchmarking(muon_data_group_dir=muon_data_group_dir,
                                                             minimizers=minimizers, use_errors=use_errors,
                                                             results_dir=results_dir)
elif run_data == "nist":
    # NIST data
    problems, results_per_group = fitBenchmarking(nist_group_dir=nist_group_dir,
                                                             minimizers=minimizers, use_errors=use_errors,
                                                             results_dir=results_dir)

for idx, group_results in enumerate(results_per_group):
    printTables(minimizers, group_results, problems[idx],
                group_name=group_suffix_names[idx],
                use_errors=use_errors,
                rst=True, save_to_file=True, color_scale=color_scale,
                results_dir=results_dir)

