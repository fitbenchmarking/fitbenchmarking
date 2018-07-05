# script for running fit benchmarking and comparising the relative performance of local minimzers on
# fit problems

import os
import fitting_benchmarking as fitbk
import results_output as fitout




minimizers = ['BFGS', 'Conjugate gradient (Fletcher-Reeves imp.)',
              'Conjugate gradient (Polak-Ribiere imp.)',
              'Levenberg-Marquardt', 'Levenberg-MarquardtMD',
              'Simplex','SteepestDescent',
              'Trust Region', 'Damped GaussNewton']

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

# choice the data to run
run_data = "neutron"

if run_data == "neutron":
    problems, results_per_group = fitbk.do_fitting_benchmark(neutron_data_group_dirs=neutron_data_group_dirs,
                                                             minimizers=minimizers, use_errors=use_errors)
elif run_data == "muon":
    group_names = ['MUON']
    group_suffix_names = ['MUON']
    problems, results_per_group = fitbk.do_fitting_benchmark(muon_data_group_dir=muon_data_group_dir,
                                                             minimizers=minimizers, use_errors=use_errors)
elif run_data == "nist":
    # NIST data
    problems, results_per_group = fitbk.do_fitting_benchmark(nist_group_dir=nist_group_dir,
                                                             minimizers=minimizers, use_errors=use_errors)

for idx, group_results in enumerate(results_per_group):
        print("\n\n")
        print("********************************************************")
        print("**************** RESULTS FOR GROUP {0}, {1} ************".format(idx+1,
                                                                                group_names[idx]))
        print("********************************************************")
        fitout.print_group_results_tables(minimizers, group_results, problems[idx],
                                          group_name=group_suffix_names[idx],
                                          use_errors=use_errors,
                                          simple_text=False, rst=True, save_to_file=True, color_scale=color_scale)
                                          
                                          
header = '\n\n**************** OVERALL SUMMARY - ALL GROUPS ******** \n\n'
print(header)
fitout.print_overall_results_table(minimizers, results_per_group, problems, group_names,
                                   use_errors=use_errors, save_to_file=True)
