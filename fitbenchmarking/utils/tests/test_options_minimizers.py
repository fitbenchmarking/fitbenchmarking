"""
Test the MINIMIZERS section for the options file
"""

import inspect
import os
import shutil
import unittest

from parameterized import parameterized

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
        software = [
            "bumps",
            "ceres",
            "dfo",
            "gofit",
            "gradient_free",
            "gsl",
            "horace",
            "levmar",
            "lmfit",
            "mantid",
            "matlab",
            "matlab_curve",
            "matlab_opt",
            "matlab_stats",
            "minuit",
            "nlopt",
            "ralfit",
            "scipy",
            "scipy_ls",
            "scipy_leastsq",
            "scipy_go",
            "theseus",
        ]
        self.options.software = software

    @parameterized.expand(
        [
            ("bumps", ["amoeba", "lm-bumps", "newton", "scipy-leastsq"]),
            ("dfo", ["dfols"]),
            (
                "gsl",
                [
                    "lmsder",
                    "lmder",
                    "nmsimplex",
                    "nmsimplex2",
                    "conjugate_pr",
                    "conjugate_fr",
                    "vector_bfgs",
                    "vector_bfgs2",
                    "steepest_descent",
                ],
            ),
            (
                "mantid",
                [
                    "BFGS",
                    "Conjugate gradient (Fletcher-Reeves imp.)",
                    "Conjugate gradient (Polak-Ribiere imp.)",
                    "Damped GaussNewton",
                    "Levenberg-Marquardt",
                    "Levenberg-MarquardtMD",
                    "Simplex",
                    "SteepestDescent",
                    "Trust Region",
                ],
            ),
            ("minuit", ["migrad", "simplex"]),
            (
                "ralfit",
                [
                    "gn",
                    "gn_reg",
                    "hybrid",
                    "hybrid_reg",
                    "newton",
                    "newton_reg",
                ],
            ),
            (
                "scipy",
                [
                    "Nelder-Mead",
                    "Powell",
                    "CG",
                    "BFGS",
                    "Newton-CG",
                    "L-BFGS-B",
                    "TNC",
                    "SLSQP",
                    "COBYLA",
                ],
            ),
            ("scipy_ls", ["lm-scipy", "trf", "dogbox"]),
            ("scipy_leastsq", ["lm-leastsq"]),
            (
                "nlopt",
                [
                    "LN_BOBYQA",
                    "LN_NEWUOA",
                    "LN_NEWUOA_BOUND",
                    "LN_PRAXIS",
                    "LD_SLSQP",
                    "LD_VAR2",
                    "LD_VAR1",
                    "AUGLAG",
                    "AUGLAG_EQ",
                    "LN_NELDERMEAD",
                    "LN_SBPLX",
                    "LN_COBYLA",
                    "LD_CCSAQ",
                    "LD_MMA",
                    "LD_TNEWTON_PRECOND_RESTART",
                    "LD_TNEWTON_PRECOND",
                    "LD_TNEWTON_RESTART",
                    "LD_TNEWTON",
                    "LD_LBFGS",
                ],
            ),
            (
                "ceres",
                [
                    "Levenberg_Marquardt",
                    "Dogleg",
                    "BFGS",
                    "LBFGS",
                    "steepest_descent",
                    "Fletcher_Reeves",
                    "Polak_Ribiere",
                    "Hestenes_Stiefel",
                ],
            ),
            (
                "gradient_free",
                [
                    "HillClimbingOptimizer",
                    "RepulsingHillClimbingOptimizer",
                    "SimulatedAnnealingOptimizer",
                    "RandomSearchOptimizer",
                    "RandomRestartHillClimbingOptimizer",
                    "RandomAnnealingOptimizer",
                    "ParallelTemperingOptimizer",
                    "ParticleSwarmOptimizer",
                    "EvolutionStrategyOptimizer",
                ],
            ),
            ("horace", ["lm-lsqr"]),
            ("levmar", ["levmar"]),
            (
                "lmfit",
                [
                    "powell",
                    "cobyla",
                    "slsqp",
                    "nelder",
                    "least_squares",
                    "leastsq",
                    "newton",
                    "tnc",
                    "lbfgsb",
                    "bfgs",
                    "cg",
                    "ampgo",
                ],
            ),
            ("matlab", ["Nelder-Mead Simplex"]),
            ("matlab_curve", ["Levenberg-Marquardt", "Trust-Region"]),
            ("matlab_opt", ["levenberg-marquardt", "trust-region-reflective"]),
            ("matlab_stats", ["Levenberg-Marquardt"]),
            ("theseus", ["Levenberg_Marquardt", "Gauss-Newton"]),
            ("scipy_go", ["differential_evolution", "dual_annealing"]),
        ]
    )
    def test_minimizers_for_softwares_in_options(self, software, expected):
        """
        Checks default minimizers are set correctly for softwares
        """
        actual = self.options.minimizers[software]
        self.assertEqual(expected, actual)


class UserMininimizerOptionTests(unittest.TestCase):
    """
    Checks the minimizers in the options file are set correctly or raise errors
    """

    def setUp(self):
        """
        Sets the directory to save the temporary ini files in
        """
        options_dir = os.path.dirname(inspect.getfile(Options))
        self.test_files_dir = os.path.join(options_dir, "tests", "files")
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
        new_line = f"\n{' ' * (len(software) + 2)}"
        config_str = f"[MINIMIZERS]\n{software}: {new_line.join(options_set)}"
        opts_file = os.path.join(
            self.test_files_dir, f"test_{software}_valid.ini"
        )
        with open(opts_file, "w", encoding="utf-8") as f:
            f.write(config_str)
        return opts_file

    @parameterized.expand(
        [
            (["newton", "de"], "bumps"),
            (["dfols"], "dfo"),
            (["lmsder", "lmder", "nmsimplex"], "gsl"),
            (
                [
                    "Damped GaussNewton",
                    "Levenberg-Marquardt",
                    "Levenberg-MarquardtMD",
                ],
                "mantid",
            ),
            (["migrad", "simplex"], "minuit"),
            (["hybrid_reg"], "ralfit"),
            (["Nelder-Mead", "TNC", "BFGS", "CG"], "scipy"),
            (["lm-scipy", "trf"], "scipy_ls"),
            (["lm-leastsq"], "scipy_leastsq"),
            (["LD_TNEWTON", "LD_LBFGS"], "nlopt"),
            (["Levenberg_Marquardt"], "ceres"),
            (["Levenberg_Marquardt"], "theseus"),
            (["regularisation"], "gofit"),
            (["lm-lsqr"], "horace"),
            (["levmar"], "levmar"),
            (["Nelder-Mead Simplex"], "matlab"),
            (["Trust-Region", "Levenberg-Marquardt"], "matlab_curve"),
            (["levenberg-marquardt", "trust-region-reflective"], "matlab_opt"),
            (["Levenberg-Marquardt"], "matlab_stats"),
            (["differential_evolution", "shgo"], "scipy_go"),
            (
                [
                    "HillClimbingOptimizer",
                    "RepulsingHillClimbingOptimizer",
                    "SimulatedAnnealingOptimizer",
                ],
                "gradient_free",
            ),
        ]
    )
    def test_minimizer_choice_valid(self, options_set, software):
        """
        Test to check that the minimizer option set is valid

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

    @parameterized.expand(
        [
            (["newton", "de"], "sasview"),
            (["random_minimizer"], "bumps"),
            (["CG"], "dfo"),
            (["newton"], "gsl"),
            (
                ["lm-mantid", "Levenberg-Marquardt", "Levenberg-MarquardtMD"],
                "mantid",
            ),
            (["line search"], "minuit"),
            (["Trust_region"], "ralfit"),
            (["Nelder-Mead", "TNC-scipy", "BFGS", "CG-NE"], "scipy"),
            (["lm-minpack-jac", "trf"], "scipy_ls"),
            (["dogbox", "lm-leastsq"], "scipy_leastsq"),
            (["newton", "lbfgs"], "nlopt"),
            (["lm"], "ceres"),
            (["lm"], "theseus"),
            (["levenberg-marquardt"], "gofit"),
            (["levenberg-marquardt"], "horace"),
            (["levenberg-marquardt"], "levmar"),
            (["simplex"], "matlab"),
            (["lm", "TR"], "matlab_curve"),
            (["Trust-Region", "Levenberg-Marquardt"], "matlab_opt"),
            (["lm"], "matlab_stats"),
            (["de", "shgo"], "scipy_go"),
            (
                [
                    "random_minimizer_1",
                    "random_minimizer_2",
                    "random_minimizer_3",
                ],
                "gradient_free",
            ),
        ]
    )
    def test_minimizer_choice_invalid(self, options_set, software):
        """
        Test to check that the minimizer option set is invalid

        :param options_set: option set to be tested
        :type options_set: list
        :param software: software to be tests
        :type software: str
        """
        opts_file = self.generate_user_ini_file(options_set, software)
        with self.assertRaises(exceptions.OptionsError):
            Options(opts_file)

    def test_error_msg(self):
        """
        Tests the error msg when wrong minimizer is selected.
        """
        opts_file = self.generate_user_ini_file(["ameoba", "de"], "bumps")
        msg = (
            "Failed to process options.\nDetails: The option 'bumps:"
            " ['ameoba', 'de']' in the ini file is invalid. ['ameoba']"
            " is not a valid option. bumps must be one or more of"
            " ['amoeba', 'lm-bumps', 'newton', 'de', 'scipy-leastsq',"
            " 'dream']"
        )
        with self.assertRaises(exceptions.OptionsError) as exp:
            Options(opts_file)
        self.assertEqual(str(exp.exception), msg)
