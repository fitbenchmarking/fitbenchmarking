'''
This file will handle all interaction with the options configuration file.
'''
# pylint: disable=too-many-branches

import configparser
import glob
import os

import matplotlib.pyplot as plt

from fitbenchmarking.utils.exceptions import OptionsError


class Options:
    """
    An options class to store and handle all options for fitbenchmarking
    """
    VALID_SECTIONS = ['MINIMIZERS', 'FITTING', 'JACOBIAN', 'HESSIAN',
                      'OUTPUT', 'LOGGING', 'RUNTIME', 'DASH']
    VALID_MINIMIZERS = \
        {'bumps': ['amoeba',
                   'lm-bumps',
                   'newton',
                   'de',
                   'scipy-leastsq',
                   'dream'],
         'ceres': ['Levenberg_Marquardt', 'Dogleg', 'BFGS', 'LBFGS',
                   'steepest_descent', 'Fletcher_Reeves', 'Polak_Ribiere',
                   'Hestenes_Stiefel'],
         'dfo': ['dfols'],
         'gofit': ['alternating', 'multistart', 'regularisation'],
         'gradient_free': ['HillClimbingOptimizer',
                           'RepulsingHillClimbingOptimizer',
                           'SimulatedAnnealingOptimizer',
                           'RandomSearchOptimizer',
                           'RandomRestartHillClimbingOptimizer',
                           'RandomAnnealingOptimizer',
                           'ParallelTemperingOptimizer',
                           'ParticleSwarmOptimizer',
                           'EvolutionStrategyOptimizer',
                           'BayesianOptimizer',
                           'TreeStructuredParzenEstimators',
                           'DecisionTreeOptimizer'],
         'gsl': ['lmsder', 'lmder', 'nmsimplex', 'nmsimplex2',
                 'conjugate_pr', 'conjugate_fr', 'vector_bfgs',
                 'vector_bfgs2', 'steepest_descent'],
         'horace': ['lm-lsqr'],
         'levmar': ['levmar'],
         'lmfit': ['differential_evolution',
                   'brute',
                   'basinhopping',
                   'powell',
                   'cobyla',
                   'slsqp',
                   'emcee',
                   'nelder',
                   'least_squares',
                   'trust-ncg',
                   'trust-exact',
                   'trust-krylov',
                   'trust-constr',
                   'dogleg',
                   'leastsq',
                   'newton',
                   'tnc',
                   'lbfgsb',
                   'bfgs',
                   'cg',
                   'ampgo',
                   'shgo',
                   'dual_annealing'],
         'mantid': ['BFGS',
                    'Conjugate gradient (Fletcher-Reeves imp.)',
                    'Conjugate gradient (Polak-Ribiere imp.)',
                    'Damped GaussNewton', 'Levenberg-Marquardt',
                    'Levenberg-MarquardtMD', 'Simplex',
                    'SteepestDescent', 'Trust Region', 'FABADA'],
         'matlab': ['Nelder-Mead Simplex'],
         'matlab_curve': ['Levenberg-Marquardt', 'Trust-Region'],
         'matlab_opt': ['levenberg-marquardt', 'trust-region-reflective'],
         'matlab_stats': ['Levenberg-Marquardt'],
         'minuit': ['migrad', 'simplex'],
         'paramonte': ['paraDram_sampler'],
         'pyro': ['NUTS'],
         'nlopt': ['LN_BOBYQA',
                   'LN_NEWUOA',
                   'LN_NEWUOA_BOUND',
                   'LN_PRAXIS',
                   'LD_SLSQP',
                   'LD_VAR2',
                   'LD_VAR1',
                   'AUGLAG',
                   'AUGLAG_EQ',
                   'LN_NELDERMEAD',
                   'LN_SBPLX',
                   'LN_COBYLA',
                   'LD_CCSAQ',
                   'LD_MMA',
                   'LD_TNEWTON_PRECOND_RESTART',
                   'LD_TNEWTON_PRECOND',
                   'LD_TNEWTON_RESTART',
                   'LD_TNEWTON',
                   'LD_LBFGS',
                   'GN_DIRECT',
                   'GN_DIRECT_L',
                   'GN_DIRECT_L_RAND',
                   'GNL_DIRECT_NOSCAL',
                   'GN_DIRECT_L_NOSCAL',
                   'GN_DIRECT_L_RAND_NOSCAL',
                   'GN_ORIG_DIRECT',
                   'GN_ORIG_DIRECT_L',
                   'GN_CRS2_LM',
                   'G_MLSL_LDS',
                   'G_MLSL',
                   'GD_STOGO',
                   'GD_STOGO_RAND',
                   'GN_AGS',
                   'GN_ISRES'],
         'ralfit': ['gn', 'gn_reg', 'hybrid', 'hybrid_reg',
                    'newton', 'newton_reg',
                    'newton-tensor', 'newton-tensor_reg'],
         'scipy': ['Nelder-Mead',
                   'Powell',
                   'CG',
                   'BFGS',
                   'Newton-CG',
                   'L-BFGS-B',
                   'TNC',
                   'SLSQP',
                   'COBYLA',
                   'trust-ncg',
                   'trust-exact',
                   'trust-krylov',
                   'trust-constr',
                   'dogleg'],
         'scipy_ls': ['lm-scipy', 'trf', 'dogbox'],
         'scipy_leastsq': ['lm-leastsq'],
         'scipy_go': ['differential_evolution', 'shgo', 'dual_annealing'],
         'theseus': ['Levenberg_Marquardt', 'Gauss-Newton']}
    VALID_FITTING = \
        {'algorithm_type': ['all', 'ls', 'deriv_free', 'general', 'simplex',
                            'trust_region', 'levenberg-marquardt',
                            'gauss_newton', 'bfgs', 'conjugate_gradient',
                            'steepest_descent', 'global_optimization', 'MCMC'],
         'software': ['bumps', 'ceres', 'dfo', 'gofit', 'gradient_free', 'gsl',
                      'horace', 'levmar', 'lmfit', 'mantid', 'matlab',
                      'matlab_curve', 'matlab_opt', 'matlab_stats', 'minuit',
                      'nlopt', 'paramonte', 'pyro', 'ralfit', 'scipy',
                      'scipy_ls', 'scipy_leastsq', 'scipy_go', 'theseus'],
         'jac_method': ['best_available', 'scipy', 'analytic', 'default',
                        'numdifftools'],
         'hes_method': ['best_available', 'scipy', 'analytic', 'default',
                        'numdifftools'],
         'cost_func_type': ['nlls', 'weighted_nlls', 'hellinger_nlls',
                            'loglike_nlls', 'poisson']}
    VALID_JACOBIAN = \
        {'scipy': ['2-point', '3-point', 'cs', '2-point_sparse'],
         'best_available': ['default'],
         'analytic': ['default', 'sparse'],
         'default': ['default'],
         'numdifftools': ['central',
                          'complex', 'multicomplex',
                          'forward', 'backward']}
    VALID_HESSIAN = \
        {'scipy': ['2-point', '3-point', 'cs'],
         'best_available': ['default'],
         'analytic': ['default'],
         'default': ['default'],
         'numdifftools': ['central',
                          'complex', 'multicomplex',
                          'forward', 'backward']}
    VALID_OUTPUT = \
        {'level': ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR',
                   'CRITICAL'],
         'append': [True, False],
         'external_output': ['debug', 'display', 'log_only'],
         'make_plots': [True, False],
         'pbar': [True, False],
         'comparison_mode': ['abs', 'rel', 'both'],
         'table_type': ['acc', 'runtime', 'compare', 'local_min', 'emissions'],
         'results_browser': [True, False],
         'run_dash': [True, False],
         'colour_map': plt.colormaps()}
    VALID_LOGGING = \
        {'level': ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR',
                   'CRITICAL'],
         'append': [True, False],
         'external_output': ['debug', 'display', 'log_only']}
    VALID_RUNTIME = \
        ['mean', 'minimum', 'maximum', 'first', 'median', 'harmonic', 'trim']
    VALID_DASH = {}

    VALID = {'MINIMIZERS': VALID_MINIMIZERS,
             'FITTING': VALID_FITTING,
             'JACOBIAN': VALID_JACOBIAN,
             'HESSIAN': VALID_HESSIAN,
             'OUTPUT': VALID_OUTPUT,
             'LOGGING': VALID_LOGGING,
             'RUNTIME': VALID_RUNTIME,
             'DASH': VALID_DASH}

    DEFAULT_MINIMZERS = \
        {'bumps': ['amoeba',
                   'lm-bumps',
                   'newton',
                   'scipy-leastsq'],
         'ceres': ['Levenberg_Marquardt', 'Dogleg', 'BFGS', 'LBFGS',
                   'steepest_descent', 'Fletcher_Reeves', 'Polak_Ribiere',
                   'Hestenes_Stiefel'],
         'dfo': ['dfols'],
         'gofit': ['multistart'],
         'gradient_free': ['HillClimbingOptimizer',
                           'RepulsingHillClimbingOptimizer',
                           'SimulatedAnnealingOptimizer',
                           'RandomSearchOptimizer',
                           'RandomRestartHillClimbingOptimizer',
                           'RandomAnnealingOptimizer',
                           'ParallelTemperingOptimizer',
                           'ParticleSwarmOptimizer',
                           'EvolutionStrategyOptimizer'],
         'gsl': ['lmsder', 'lmder', 'nmsimplex', 'nmsimplex2',
                 'conjugate_pr', 'conjugate_fr', 'vector_bfgs',
                 'vector_bfgs2', 'steepest_descent'],
         'horace': ['lm-lsqr'],
         'levmar': ['levmar'],
         'lmfit': ['powell',
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
                   'ampgo'],
         'mantid': ['BFGS',
                    'Conjugate gradient (Fletcher-Reeves imp.)',
                    'Conjugate gradient (Polak-Ribiere imp.)',
                    'Damped GaussNewton', 'Levenberg-Marquardt',
                    'Levenberg-MarquardtMD', 'Simplex',
                    'SteepestDescent', 'Trust Region'],
         'matlab': ['Nelder-Mead Simplex'],
         'matlab_curve': ['Levenberg-Marquardt', 'Trust-Region'],
         'matlab_opt': ['levenberg-marquardt', 'trust-region-reflective'],
         'matlab_stats': ['Levenberg-Marquardt'],
         'minuit': ['migrad', 'simplex'],
         'paramonte': ['paraDram_sampler'],
         'pyro': ['NUTS'],
         'nlopt': ['LN_BOBYQA',
                   'LN_NEWUOA',
                   'LN_NEWUOA_BOUND',
                   'LN_PRAXIS',
                   'LD_SLSQP',
                   'LD_VAR2',
                   'LD_VAR1',
                   'AUGLAG',
                   'AUGLAG_EQ',
                   'LN_NELDERMEAD',
                   'LN_SBPLX',
                   'LN_COBYLA',
                   'LD_CCSAQ',
                   'LD_MMA',
                   'LD_TNEWTON_PRECOND_RESTART',
                   'LD_TNEWTON_PRECOND',
                   'LD_TNEWTON_RESTART',
                   'LD_TNEWTON',
                   'LD_LBFGS'],
         'ralfit': ['gn', 'gn_reg', 'hybrid', 'hybrid_reg',
                    'newton', 'newton_reg'],
         'scipy': ['Nelder-Mead',
                   'Powell',
                   'CG',
                   'BFGS',
                   'Newton-CG',
                   'L-BFGS-B',
                   'TNC',
                   'SLSQP',
                   'COBYLA'],
         'scipy_ls': ['lm-scipy', 'trf', 'dogbox'],
         'scipy_leastsq': ['lm-leastsq'],
         'scipy_go': ['differential_evolution', 'dual_annealing'],
         'theseus': ['Levenberg_Marquardt', 'Gauss-Newton']}
    DEFAULT_FITTING = \
        {'num_runs': 5,
         'algorithm_type': ['all'],
         'software': ['scipy', 'scipy_ls'],
         'jac_method': ['best_available'],
         'hes_method': ['best_available'],
         'cost_func_type': ['weighted_nlls'],
         'max_runtime': 600}
    DEFAULT_JACOBIAN = \
        {'analytic': ['default'],
         'best_available': ['default'],
         'scipy': ['2-point'],
         'default': ['default'],
         'numdifftools': ['central']}
    DEFAULT_HESSIAN = \
        {'analytic': ['default'],
         'best_available': ['default'],
         'scipy': ['2-point'],
         'default': ['default'],
         'numdifftools': ['central']}
    DEFAULT_OUTPUT = \
        {'results_dir': 'fitbenchmarking_results',
         'make_plots': True,
         'pbar': True,
         'colour_map': 'magma_r',
         'colour_ulim': 100,
         'cmap_range': [0.2, 0.8],
         'comparison_mode': 'both',
         'results_browser': True,
         'run_dash': True,
         'table_type': ['acc', 'runtime', 'compare', 'local_min', 'emissions'],
         'run_name': '',
         'checkpoint_filename': 'checkpoint.json'}
    DEFAULT_LOGGING = \
        {'file_name': 'fitbenchmarking.log',
         'append': False,
         'level': 'INFO',
         'external_output': 'log_only'}
    DEFAULT_RUNTIME = \
        {'runtime_metric': 'mean'}
    DEFAULT_DASH = \
        {'port': 4000}
    DEFAULTS = {'MINIMIZERS': DEFAULT_MINIMZERS,
                'FITTING': DEFAULT_FITTING,
                'JACOBIAN': DEFAULT_JACOBIAN,
                'HESSIAN': DEFAULT_HESSIAN,
                'OUTPUT': DEFAULT_OUTPUT,
                'LOGGING': DEFAULT_LOGGING,
                'RUNTIME': DEFAULT_RUNTIME,
                'DASH': DEFAULT_DASH}

    # pylint: disable=too-many-statements
    def __init__(self, file_name=None, additional_options=None):
        """
        Initialise the options from a file if file is given.
        Priority is values in the file, failing that, values are taken from
        DEFAULTS (stored in ./default_options.ini)

        :param file_name: The options file to load
        :type file_name: str
        :param additional_options: A dictionary of options input
        by the user into the command line.
        :type additional_options: dict

        """
        # additional_options is initialied to an empty dict if
        # no value is given
        if additional_options is None:
            additional_options = {}

        # stores the file name to be used to reset options for multiple
        # problem groups
        self.stored_file_name = file_name
        self.error_message = []
        self._results_dir: str = ""
        config = configparser.ConfigParser(converters={'list': read_list,
                                                       'str': str,
                                                       'rng': read_range},
                                           allow_no_value=True)

        for section in self.VALID_SECTIONS:
            config.add_section(section)

        if file_name is not None:
            config.read(file_name)

            # Checks that the user defined sections are valid
            if config.sections() != self.VALID_SECTIONS:
                raise OptionsError(
                    f"Invalid options sections set, {config.sections()}, "
                    f"the valid sections are {self.VALID_SECTIONS}")
            config.sections()

            # Checks that the options within the sections are valid
            for key in self.VALID_SECTIONS:
                default_options_list = list(self.DEFAULTS[key].keys())
                user_options_list = [option[0] for option in config.items(key)]
                if not set(user_options_list) <= set(default_options_list):
                    raise OptionsError(
                        f"Invalid options key set in the {key} Section: \n"
                        f"{user_options_list}, \n "
                        f"the valid keys are: \n{default_options_list}")

        minimizers = config['MINIMIZERS']
        self._minimizers = {}
        self.minimizer_alg_type = {}
        for key in self.VALID_FITTING["software"]:
            self._minimizers[key] = self.read_value(minimizers.getlist,
                                                    key, additional_options)

        fitting = config['FITTING']

        self.num_runs = self.read_value(fitting.getint, 'num_runs',
                                        additional_options)

        self.algorithm_type = self.read_value(fitting.getlist,
                                              'algorithm_type',
                                              additional_options)

        self.software = self.read_value(fitting.getlist, 'software',
                                        additional_options)

        self.jac_method = self.read_value(fitting.getlist, 'jac_method',
                                          additional_options)

        self.hes_method = self.read_value(fitting.getlist, 'hes_method',
                                          additional_options)

        self.cost_func_type = self.read_value(fitting.getlist,
                                              'cost_func_type',
                                              additional_options)

        self.max_runtime = self.read_value(fitting.getfloat, 'max_runtime',
                                           additional_options)

        jacobian = config['JACOBIAN']
        self.jac_num_method = {}
        for key in self.VALID_FITTING["jac_method"]:
            self.jac_num_method[key] = self.read_value(jacobian.getlist,
                                                       key,
                                                       additional_options)

        hessian = config['HESSIAN']
        self.hes_num_method = {}
        for key in self.VALID_FITTING["hes_method"]:
            self.hes_num_method[key] = self.read_value(hessian.getlist,
                                                       key,
                                                       additional_options)

        output = config['OUTPUT']

        if 'make_plots' in additional_options:
            self.make_plots = additional_options['make_plots']
        else:
            self.make_plots = self.read_value(
                output.getboolean, 'make_plots', additional_options)

        if 'results_browser' in additional_options:
            self.results_browser = additional_options['results_browser']
        else:
            self.results_browser = self.read_value(
                output.getboolean, 'results_browser', additional_options)

        if 'run_dash' in additional_options:
            self.run_dash = additional_options['run_dash']
        else:
            self.run_dash = self.read_value(
                output.getboolean, 'run_dash', additional_options)

        if 'pbar' in additional_options:
            self.pbar = additional_options['pbar']
        else:
            self.pbar = self.read_value(
                output.getboolean, 'pbar', additional_options)

        self.colour_map = self.read_value(
            output.getstr, 'colour_map', additional_options)
        self.colour_ulim = self.read_value(
            output.getfloat, 'colour_ulim', additional_options)
        self.cmap_range = self.read_value(
            output.getrng, 'cmap_range', additional_options)

        self.comparison_mode = self.read_value(output.getstr,
                                               'comparison_mode',
                                               additional_options)

        self.table_type = self.read_value(output.getlist, 'table_type',
                                          additional_options)

        self.results_dir = self.read_value(output.getstr, 'results_dir',
                                           additional_options)
        self.checkpoint_filename = self.read_value(
            output.getstr, 'checkpoint_filename', additional_options)

        self.run_name = self.read_value(output.getstr,
                                        'run_name',
                                        additional_options)

        runtime = config['RUNTIME']
        self.runtime_metric = self.read_value(runtime.getstr,
                                              'runtime_metric',
                                              additional_options)

        dash_settings = config['DASH']
        self.port = self.read_value(dash_settings.getint,
                                    'port',
                                    additional_options)

        logging = config['LOGGING']

        self.log_append = self.read_value(logging.getboolean, 'append',
                                          additional_options)

        self.log_file = self.read_value(logging.getstr, 'file_name',
                                        additional_options)

        self.log_level = self.read_value(logging.getstr, 'level',
                                         additional_options)

        self.external_output = self.read_value(logging.getstr,
                                               'external_output',
                                               additional_options)

        if self.error_message:
            raise OptionsError('\n'.join(self.error_message))

    # pylint: enable=too-many-statements

    def read_value(self, func, option, additional_options):
        """
        Helper function which loads in the value

        :param func: configparser function
        :type func: callable
        :param option: option to be read for file
        :type option: str
        :param additional_options: A dictionary of options
        input by the user into the command line.
        :type additional_options: dict

        :return: value of the option
        :rtype: list/str/int/bool
        """
        section = str(func).split("Section: ")[1].split('>')[0]
        try:
            if (option in additional_options and
                    additional_options[option]):
                value = additional_options[option]
            else:
                value = func(option, fallback=self.DEFAULTS[section][option])

        except ValueError as e:
            self.error_message.append(
                f"Incorrect options type for {option}.\n{e}")
            value = None

        if option in self.VALID[section]:
            if isinstance(value, list):
                set1 = set(value)
                set2 = set(self.VALID[section][option])
                value_check = set1.issubset(set2)
            else:
                value_check = value in self.VALID[section][option]
            if not value_check:
                self.error_message.append(
                    f"The option '{option}: {value}' in the ini file is "
                    f"invalid. {option} must be one or more of "
                    f"{self.VALID[section][option]}")
        return value

    @property
    def results_dir(self) -> str:
        """
        Returns the directory to store the results in.
        """
        return self._results_dir

    @results_dir.setter
    def results_dir(self, directory: str) -> None:
        """
        Sets the directory to store the results.
        """
        self._results_dir = os.path.abspath(directory)

    @property
    def minimizers(self):
        """
        Returns the minimizers in a software package
        """
        return {s: self._minimizers[s] for s in self.software}

    @minimizers.setter
    def minimizers(self, value):
        self._minimizers = value

    def _create_config(self):
        """
        Return the contents of the options object as a ConfigParser object,
        which e.g. then can be written to a file object or other stream

        :return: ConfigParser
        """
        config = configparser.ConfigParser(converters={'list': read_list,
                                                       'str': str,
                                                       'rng': read_range})

        def list_to_string(mylist):
            return '\n'.join(mylist)

        config['MINIMIZERS'] = {k: list_to_string(m)
                                for k, m in self.minimizers.items()}
        config['FITTING'] = {
            'num_runs': self.num_runs,
            'algorithm_type': list_to_string(
                self.algorithm_type),
            'software': list_to_string(self.software),
            'jac_method': list_to_string(self.jac_method),
            'hes_method': list_to_string(self.hes_method),
            'max_runtime': self.max_runtime,
            'cost_func_type': list_to_string(self.cost_func_type),
        }
        config['JACOBIAN'] = {k: list_to_string(m)
                              for k, m in self.jac_num_method.items()}
        config['HESSIAN'] = {k: list_to_string(m)
                             for k, m in self.hes_num_method.items()}

        config['OUTPUT'] = {'results_dir': self.results_dir,
                            'colour_map': self.colour_map,
                            'cmap_range': self.cmap_range,
                            'colour_ulim': self.colour_ulim,
                            'comparison_mode': self.comparison_mode,
                            'make_plots': self.make_plots,
                            'results_browser': self.results_browser,
                            'run_dash': self.run_dash,
                            'pbar': self.pbar,
                            'table_type': list_to_string(self.table_type),
                            'run_name': self.run_name}

        config['LOGGING'] = {'file_name': self.log_file,
                             'level': self.log_level,
                             'append': self.log_append,
                             'external_output': self.external_output}

        config['RUNTIME'] = {'runtime_metric': self.runtime_metric}

        config['DASH'] = {'port': self.port}

        return config

    def write(self, file_name):
        """
        Write the contents of the options object to a new options file.

        :param file_name: The path to the new options file
        :type file_name: str
        """
        config = self._create_config()

        with open(file_name, 'w', encoding='utf-8') as f:
            config.write(f)

    def write_to_stream(self, file_object):
        """
        Write the contents of the options object to a file object.

        :type file_object: file object
        """
        self._create_config().write(file_object)


def read_list(s):
    """
    Utility function to allow lists to be read by the config parser

    :param s: string to convert to a list
    :type s: string

    :return: list of items
    :rtype: list of str
    """
    return str(s).split('\n')


def read_range(s):
    """
    Utility function to allow ranges to be read by the config parser

    :param s: string to convert to a list
    :type s: string

    :return: two element list [lower_lim, upper lim]
    :rtype: list
    """

    if s[0] != '[' or s[-1] != ']':
        raise ValueError("range specified without [] parentheses.")
    rng = [float(item) for item in s[1:-1].split(",")]
    if len(rng) != 2:
        raise ValueError("range not specified with 2 elements.")
    if rng[0] > rng[1]:
        raise ValueError("Incorrect element order;"
                         "range[0] > range[1] detected."
                         "The elements must satisfy "
                         "range[0] < range[1].")
    if rng[0] < 0 or rng[0] > 1 or rng[1] < 0 or rng[1] > 1:
        raise ValueError("One or more elements in range are "
                         "outside of the permitted range 0 <= a <= 1.")
    return rng


def find_options_file(options_file: str, additional_options: dict) -> Options:
    """
    Attempts to find the options file and creates an Options object for it.
    Wildcards are accepted in the parameters of this function.

    :param options_file: The path or glob pattern for an options file.
    :type options_file: str
    :param additional_options: A dictionary of options input by the user into
                               the command line.
    :type additional_options: dict
    :return: An Options object.
    :rtype: fitbenchmarking.utils.options.Options
    """
    if options_file != '':
        # Read custom minimizer options from file
        glob_options_file = glob.glob(options_file)

        if not glob_options_file:
            raise OptionsError(f'Could not find file {options_file}')
        if not options_file.endswith(".ini"):
            raise OptionsError('Options file must be a ".ini" file')

        return Options(file_name=glob_options_file,
                       additional_options=additional_options)
    return Options(additional_options=additional_options)
