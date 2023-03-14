'''
Test the MINIMIZERS section for the options file
'''
import inspect
import shutil
import os
import unittest

from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


class MininimizerOptionTests(unittest.TestCase):
    """
    Checks that the default minimizers in the options file are set correctly
    """

    def setUp(self):
        """
        Initializes options class with defaults
        """
        self.options = Options()
        software = ['bumps', 'ceres', 'dfo', 'gofit', 'gradient_free', 'gsl',
                    'horace', 'levmar', 'lmfit', 'mantid', 'matlab',
                    'matlab_curve', 'matlab_opt', 'matlab_stats', 'minuit',
                    'ralfit', 'scipy', 'scipy_ls', 'scipy_go', 'theseus']
        self.options.software = software

    def test_minimizer_bumps(self):
        """
        Checks default bumps minimizers are set correctly
        """
        expected = ['amoeba', 'lm-bumps', 'newton', 'scipy-leastsq']
        actual = self.options.minimizers['bumps']
        self.assertEqual(expected, actual)

    def test_minimizer_dfo(self):
        """
        Checks default dfo minimizers are set correctly
        """
        expected = ['dfogn', 'dfols']
        actual = self.options.minimizers['dfo']
        self.assertEqual(expected, actual)

    def test_minimizer_gsl(self):
        """
        Checks default gsl minimizers are set correctly
        """
        expected = ['lmsder', 'lmder', 'nmsimplex', 'nmsimplex2',
                    'conjugate_pr', 'conjugate_fr', 'vector_bfgs',
                    'vector_bfgs2', 'steepest_descent']
        actual = self.options.minimizers['gsl']
        self.assertEqual(expected, actual)

    def test_minimizer_mantid(self):
        """
        Checks default mantid minimizers are set correctly
        """
        expected = ['BFGS',
                    'Conjugate gradient (Fletcher-Reeves imp.)',
                    'Conjugate gradient (Polak-Ribiere imp.)',
                    'Damped GaussNewton', 'Levenberg-Marquardt',
                    'Levenberg-MarquardtMD', 'Simplex',
                    'SteepestDescent', 'Trust Region']
        actual = self.options.minimizers['mantid']
        self.assertEqual(expected, actual)

    def test_minimizer_minuit(self):
        """
        Checks default minuit minimizers are set correctly
        """
        expected = ['minuit']
        actual = self.options.minimizers['minuit']
        self.assertEqual(expected, actual)

    def test_minimizer_ralfit(self):
        """
        Checks default ralfit minimizers are set correctly
        """
        expected = ['gn', 'gn_reg', 'hybrid', 'hybrid_reg',
                    'newton', 'newton_reg']
        actual = self.options.minimizers['ralfit']
        self.assertEqual(expected, actual)

    def test_minimizer_scipy(self):
        """
        Checks default scipy minimizers are set correctly
        """
        expected = ['Nelder-Mead',
                    'Powell',
                    'CG',
                    'BFGS',
                    'Newton-CG',
                    'L-BFGS-B',
                    'TNC',
                    'SLSQP',
                    'COBYLA']
        actual = self.options.minimizers['scipy']
        self.assertEqual(expected, actual)

    def test_minimizer_scipy_ls(self):
        """
        Checks default scipy_ls minimizers are set correctly
        """
        expected = ['lm-scipy', 'trf', 'dogbox']
        actual = self.options.minimizers['scipy_ls']
        self.assertEqual(expected, actual)

    def test_minimizer_ceres(self):
        """
        Checks default ceres minimizers are set correctly
        """
        expected = ['Levenberg_Marquardt', 'Dogleg', 'BFGS', 'LBFGS',
                    'steepest_descent', 'Fletcher_Reeves', 'Polak_Ribiere',
                    'Hestenes_Stiefel']
        actual = self.options.minimizers['ceres']
        self.assertEqual(expected, actual)

    def test_minimizer_gradient_free(self):
        """
        Checks default gradient free minimizers are set correctly
        """
        expected = ['HillClimbingOptimizer',
                    'RepulsingHillClimbingOptimizer',
                    'SimulatedAnnealingOptimizer',
                    'RandomSearchOptimizer',
                    'RandomRestartHillClimbingOptimizer',
                    'RandomAnnealingOptimizer',
                    'ParallelTemperingOptimizer',
                    'ParticleSwarmOptimizer',
                    'EvolutionStrategyOptimizer']
        actual = self.options.minimizers['gradient_free']
        self.assertEqual(expected, actual)

    def test_minimizer_horace(self):
        """
        Checks default horace minimizers are set correctly
        """
        expected = ['lm-lsqr']
        actual = self.options.minimizers['horace']
        self.assertEqual(expected, actual)

    def test_minimizer_levmar(self):
        """
        Checks default levmar minimizers are set correctly
        """
        expected = ['levmar']
        actual = self.options.minimizers['levmar']
        self.assertEqual(expected, actual)

    def test_minimizer_lmfit(self):
        """
        Checks default lmfit minimizers are set correctly
        """
        expected = ['powell',
                    'cobyla',
                    'slsqp',
                    'nelder',
                    'least_squares',
                    'leastsq',
                    'newton',
                    'tnc',
                    'lbfgsb',
                    'bfgs',
                    'cg',
                    'ampgo']
        actual = self.options.minimizers['lmfit']
        self.assertEqual(expected, actual)

    def test_minimizer_matlab(self):
        """
        Checks default matlab minimizers are set correctly
        """
        expected = ['Nelder-Mead Simplex']
        actual = self.options.minimizers['matlab']
        self.assertEqual(expected, actual)

    def test_minimizer_matlab_curve(self):
        """
        Checks default matlab curve minimizers are set correctly
        """
        expected = ['Levenberg-Marquardt', 'Trust-Region']
        actual = self.options.minimizers['matlab_curve']
        self.assertEqual(expected, actual)

    def test_minimizer_matlab_opt(self):
        """
        Checks default matlab opt minimizers are set correctly
        """
        expected = ['levenberg-marquardt', 'trust-region-reflective']
        actual = self.options.minimizers['matlab_opt']
        self.assertEqual(expected, actual)

    def test_minimizer_matlab_stats(self):
        """
        Checks default matlab stats minimizers are set correctly
        """
        expected = ['Levenberg-Marquardt']
        actual = self.options.minimizers['matlab_stats']
        self.assertEqual(expected, actual)

    def test_minimizer_theseus(self):
        """
        Checks default theseus minimizers are set correctly
        """
        expected = ['Levenberg_Marquardt', 'Gauss-Newton']
        actual = self.options.minimizers['theseus']
        self.assertEqual(expected, actual)

    def test_minimizer_scipy_go(self):
        """
        Checks default scipy go minimizers are set correctly
        """
        expected = ['differential_evolution', 'dual_annealing']
        actual = self.options.minimizers['scipy_go']
        self.assertEqual(expected, actual)


# pylint: disable=too-many-public-methods
class UserMininimizerOptionTests(unittest.TestCase):
    """
    Checks the minimizers in the options file are set correctly or raise errors
    """

    def setUp(self):
        """
        Sets the directory to save the temporary ini files in
        """
        options_dir = os.path.dirname(inspect.getfile(Options))
        self.test_files_dir = os.path.join(options_dir, 'tests', 'files')
        os.mkdir(self.test_files_dir)

    def tearDown(self):
        """
        Deletes temporary folder and results produced
        """
        if os.path.exists(self.test_files_dir):
            shutil.rmtree(self.test_files_dir)

    def generate_user_ini_file(self, options_set, software):
        """
        Generates user defined ini file to be parsed

        :param options_set: option set to be tested
        :type options_set: list
        :param software: software to be tests
        :type software: str

        :return: location of temporary ini file
        :rtype: str
        """
        new_line = '\n{}'.format(" " * (len(software) + 2))
        config_str = \
            "[MINIMIZERS]\n{0}: {1}".format(software,
                                            new_line.join(options_set))
        opts_file = os.path.join(self.test_files_dir,
                                 'test_{}_valid.ini'.format(software))
        with open(opts_file, 'w') as f:
            f.write(config_str)
        return opts_file

    def shared_valid(self, options_set, software):
        """
        Shared test to check that the minimizer option set is valid

        :param options_set: option set to be tested
        :type options_set: list
        :param software: software to be tests
        :type software: str
        """
        opts_file = self.generate_user_ini_file(options_set, software)
        options = Options(opts_file)
        if software not in options.software:
            options.software.append(software)
        actual = options.minimizers[software]
        self.assertEqual(options_set, actual)

    def shared_invalid(self, options_set, software):
        """
        Shared test to check that the minimizer option set is invalid

        :param options_set: option set to be tested
        :type options_set: list
        :param software: software to be tests
        :type software: str
        """
        opts_file = self.generate_user_ini_file(options_set, software)
        with self.assertRaises(exceptions.OptionsError):
            Options(opts_file)

    def test_invalid_option_key(self):
        """
        Tests that the user defined option key is invalid.
        """
        set_option = ['newton', 'de']
        self.shared_invalid(set_option, 'sasview')

    def test_minimizer_bumps_valid(self):
        """
        Checks user set bumps minimizers is valid
        """
        set_option = ['newton', 'de']
        self.shared_valid(set_option, 'bumps')

    def test_minimizer_bumps_invalid(self):
        """
        Checks user set bumps minimizers is invalid
        """
        set_option = ['random_minimizer']
        self.shared_invalid(set_option, 'bumps')

    def test_minimizer_dfo_valid(self):
        """
        Checks user set dfo minimizers is valid
        """
        set_option = ['dfogn', 'dfols']
        self.shared_valid(set_option, 'dfo')

    def test_minimizer_dfo_invalid(self):
        """
        Checks user set dfo minimizers is invalid
        """
        set_option = ['CG']
        self.shared_invalid(set_option, 'dfo')

    def test_minimizer_gsl_valid(self):
        """
        Checks user set gsl minimizers is valid
        """
        set_option = ['lmsder', 'lmder', 'nmsimplex']
        self.shared_valid(set_option, 'gsl')

    def test_minimizer_gsl_invalid(self):
        """
        Checks user set gsl minimizers is invalid
        """
        set_option = ['newton']
        self.shared_invalid(set_option, 'gsl')

    def test_minimizer_mantid_valid(self):
        """
        Checks user set mantid minimizers is valid
        """
        set_option = ['Damped GaussNewton', 'Levenberg-Marquardt',
                      'Levenberg-MarquardtMD']
        self.shared_valid(set_option, 'mantid')

    def test_minimizer_mantid_invalid(self):
        """
        Checks user set mantid minimizers is invalid
        """
        set_option = ['lm-mantid', 'Levenberg-Marquardt',
                      'Levenberg-MarquardtMD']
        self.shared_invalid(set_option, 'mantid')

    def test_minimizer_minuit_valid(self):
        """
        Checks user set minuit minimizers is valid
        """
        set_option = ['minuit']
        self.shared_valid(set_option, 'minuit')

    def test_minimizer_minuit_invalid(self):
        """
        Checks user set minuit minimizers is invalid
        """
        set_option = ['line search']
        self.shared_invalid(set_option, 'minuit')

    def test_minimizer_ralfit_valid(self):
        """
        Checks user set ralfit minimizers is valid
        """
        set_option = ['hybrid_reg']
        self.shared_valid(set_option, 'ralfit')

    def test_minimizer_ralfit_invalid(self):
        """
        Checks user set ralfit minimizers is invalid
        """
        set_option = ['Trust_region']
        self.shared_invalid(set_option, 'ralfit')

    def test_minimizer_scipy_valid(self):
        """
        Checks user set scipy minimizers is valid
        """
        set_option = ['Nelder-Mead', 'TNC', 'BFGS', 'CG']
        self.shared_valid(set_option, 'scipy')

    def test_minimizer_scipy_invalid(self):
        """
        Checks user set scipy minimizers is invalid
        """
        set_option = ['Nelder-Mead', 'TNC-scipy', 'BFGS', 'CG-NE']
        self.shared_invalid(set_option, 'scipy')

    def test_minimizer_scipy_ls_valid(self):
        """
        Checks user set scipy_ls minimizers is valid
        """
        set_option = ['lm-scipy', 'trf']
        self.shared_valid(set_option, 'scipy_ls')

    def test_minimizer_scipy_ls_invalid(self):
        """
        Checks user set scipy_ls minimizers is invalid
        """
        set_option = ['lm-minpack-jac', 'trf']
        self.shared_invalid(set_option, 'scipy_ls')

    def test_minimizer_ceres_valid(self):
        """
        Checks user set ceres minimizers is valid
        """
        set_option = ['Levenberg_Marquardt']
        self.shared_valid(set_option, 'ceres')

    def test_minimizer_ceres_invalid(self):
        """
        Checks user set ceres minimizers is invalid
        """
        set_option = ['lm']
        self.shared_invalid(set_option, 'ceres')

    def test_minimizer_theseus_valid(self):
        """
        Checks user set theseus minimizers is valid
        """
        set_option = ['Levenberg_Marquardt']
        self.shared_valid(set_option, 'theseus')

    def test_minimizer_theseus_invalid(self):
        """
        Checks user set theseus minimizers is invalid
        """
        set_option = ['lm']
        self.shared_invalid(set_option, 'theseus')

    def test_minimizer_gofit_valid(self):
        """
        Checks user set gofit minimizers is valid
        """
        set_option = ['regularisation']
        self.shared_valid(set_option, 'gofit')

    def test_minimizer_gofit_invalid(self):
        """
        Checks user set gofit minimizers is invalid
        """
        set_option = ['levenberg-marquardt']
        self.shared_invalid(set_option, 'gofit')

    def test_minimizer_horace_valid(self):
        """
        Checks user set horace minimizers is valid
        """
        set_option = ['lm-lsqr']
        self.shared_valid(set_option, 'horace')

    def test_minimizer_horace_invalid(self):
        """
        Checks user set horace minimizers is invalid
        """
        set_option = ['levenberg-marquardt']
        self.shared_invalid(set_option, 'horace')

    def test_minimizer_levmar_valid(self):
        """
        Checks user set levmar minimizers is valid
        """
        set_option = ['levmar']
        self.shared_valid(set_option, 'levmar')

    def test_minimizer_levmar_invalid(self):
        """
        Checks user set levmar minimizers is invalid
        """
        set_option = ['levenberg-marquardt']
        self.shared_invalid(set_option, 'levmar')

    def test_minimizer_matlab_valid(self):
        """
        Checks user set matlab minimizers is valid
        """
        set_option = ['Nelder-Mead Simplex']
        self.shared_valid(set_option, 'matlab')

    def test_minimizer_matlab_invalid(self):
        """
        Checks user set matlab minimizers is invalid
        """
        set_option = ['simplex']
        self.shared_invalid(set_option, 'matlab')

    def test_minimizer_matlab_curve_valid(self):
        """
        Checks user set matlab curve minimizers is valid
        """
        set_option = ['Trust-Region', 'Levenberg-Marquardt']
        self.shared_valid(set_option, 'matlab_curve')

    def test_minimizer_matlab_curve_invalid(self):
        """
        Checks user set matlab curve minimizers is invalid
        """
        set_option = ['lm', 'TR']
        self.shared_invalid(set_option, 'matlab_curve')

    def test_minimizer_matlab_opt_valid(self):
        """
        Checks user set matlab opt minimizers is valid
        """
        set_option = ['levenberg-marquardt', 'trust-region-reflective']
        self.shared_valid(set_option, 'matlab_opt')

    def test_minimizer_matlab_opt_invalid(self):
        """
        Checks user set matlab opt minimizers is invalid
        """
        set_option = ['Trust-Region', 'Levenberg-Marquardt']
        self.shared_invalid(set_option, 'matlab_opt')

    def test_minimizer_matlab_stats_valid(self):
        """
        Checks user set matlab stats minimizers is valid
        """
        set_option = ['Levenberg-Marquardt']
        self.shared_valid(set_option, 'matlab_stats')

    def test_minimizer_matlab_stats_invalid(self):
        """
        Checks user set matlab opt minimizers is invalid
        """
        set_option = ['lm']
        self.shared_invalid(set_option, 'matlab_stats')

    def test_minimizer_scipy_go_valid(self):
        """
        Checks user set scipy_go minimizers is valid
        """
        set_option = ['differential_evolution', 'shgo']
        self.shared_valid(set_option, 'scipy_go')

    def test_minimizer_scipy_go_invalid(self):
        """
        Checks user set scipy_go minimizers is invalid
        """
        set_option = ['de', 'shgo']
        self.shared_invalid(set_option, 'scipy_go')

    def test_minimizer_gradient_free_valid(self):
        """
        Checks user set gradient free minimizers is valid
        """
        set_option = ['HillClimbingOptimizer',
                      'RepulsingHillClimbingOptimizer',
                      'SimulatedAnnealingOptimizer']
        self.shared_valid(set_option, 'gradient_free')

    def test_minimizer_gradient_free_invalid(self):
        """
        Checks user set gradient free minimizers is invalid
        """
        set_option = ['random_minimizer_1', 'random_minimizer_2',
                      'random_minimizer_3']
        self.shared_invalid(set_option, 'gradient_free')
