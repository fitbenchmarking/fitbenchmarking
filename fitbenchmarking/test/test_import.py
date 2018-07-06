# Unit testing the file importing functions
import unittest
import os

# DELETE RELATIVE PATH WHEN GIT TESTS ARE ENABLED
import sys
sys.path.insert(0, 'D:\\fitbenchmarking\\fitbenchmarking')

from fitting_benchmarking import get_nist_problem_files
from fitting_benchmarking import get_data_groups
# from fitting_benchmarking import get_muon_problem_files
# from fitting_benchmarking import get_cutest_problem_files

class GetProblemFilesTest(unittest.TestCase):

    def basePath(self):
        return 'arbitrary_path' + os.sep + 'fitbenchmarking' + os.sep + 'benchmark_problems' + os.sep

    def test_get_nist_problem_files(self):
        base_path_nist = self.basePath()
        nist_problems = [['Misra1a.dat', 'Chwirut2.dat', 'Chwirut1.dat', 'Lanczos3.dat',
                          'Gauss1.dat', 'Gauss2.dat', 'DanWood.dat', 'Misra1b.dat'],
                          ['Kirby2.dat', 'Hahn1.dat','MGH17.dat', 'Lanczos1.dat', 'Lanczos2.dat', 
                          'Gauss3.dat','Misra1c.dat', 'Misra1d.dat','ENSO.dat'], 
                          ['MGH09.dat', 'Thurber.dat', 'BoxBOD.dat', 'Rat42.dat',
                          'MGH10.dat', 'Eckerle4.dat', 'Rat43.dat', 'Bennett5.dat']]

        paths_to_nist_problems = []                  
        for nist_level_group in nist_problems:
            paths_to_level_group = [base_path_nist + nist_prob_name for nist_prob_name in nist_level_group]
            paths_to_nist_problems.append(paths_to_level_group)

        self.assertListEqual(get_nist_problem_files(base_path_nist), paths_to_nist_problems)

    def test_get_nist_problem_files_fail_empty_arrays(self):

        base_path_nist = self.basePath()
        self.assertListEqual(get_nist_problem_files(base_path_nist), [[],[],[]])

    def test_get_data_groups(self):
    	
        current_dir = os.path.dirname(os.path.realpath(__file__))
    	base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        base_path_neutron = [os.path.join(base_dir,'benchmark_problems','Neutron_data')]

    	neutron_problems = [['ENGINX193749_calibration_peak19.txt', 'ENGINX193749_calibration_peak20.txt',
							 'ENGINX193749_calibration_peak23.txt', 'ENGINX193749_calibration_peak5.txt',
							 'ENGINX193749_calibration_peak6.txt', 
							 'ENGINX236516_vanadium_bank1_10brk.txt', 'ENGINX236516_vanadium_bank1_20brk.txt',
							 'EVS14188-90_Gaussian_peaks_1.txt', 'EVS14188-90_Gaussian_peaks_2.txt',
							 'GEMpeak1.txt',
							 'WISH17701_peak1.txt', 'WISH17701_peak2.txt',
							 'WISH17701_peak3.txt', 'WISH17701_peak4.txt',
							 'WISH17701_peak5.txt', 'WISH17701_peak6.txt',
							 'WISH17701_peak7.txt', 'WISH17701_peak8.txt',
							 'WISH17701_peak9.txt']]

        paths_to_neutron_problems = []
    	for neutron_level_group in neutron_problems:
    		paths_to_level_group = [base_path_neutron[0]+ os.sep + neutron_prob_name for neutron_prob_name in neutron_level_group]
    		paths_to_neutron_problems.append(paths_to_level_group)


        print(base_path_neutron)
        self.assertListEqual(get_data_groups(base_path_neutron)[0], paths_to_neutron_problems[0])

    def test_get_data_groups_fail_empty_arrays(self):

    	current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        base_path_neutron = [os.path.join(base_dir,'benchmark_problems','Neutron_data')]

    	self.assertListEqual(get_data_groups(base_path_neutron)[0], [])


if __name__ == "__main__":
    unittest.main()
