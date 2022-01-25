'''
This file will handle all interaction with the options configuration file.
'''

import configparser
import os
import matplotlib.pyplot as plt

from fitbenchmarking.utils.exceptions import OptionsError


class Options:
    """
    An options class to store and handle all options for fitbenchmarking
    """

    DEFAULTS = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'default_options.ini'))
    VALID_SECTIONS = ['MINIMIZERS', 'FITTING', 'JACOBIAN', 'HESSIAN',
                      'PLOTTING', 'OUTPUT', 'LOGGING']
    VALID_MINIMIZERS = \
        {'bumps': ['amoeba', 'lm-bumps', 'newton', 'de', 'mp'],
         'dfo': ['dfogn', 'dfols'],
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
         'levmar': ['levmar'],
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
         'minuit': ['minuit'],
         'ralfit': ['gn', 'gn_reg', 'hybrid', 'hybrid_reg'],
         'scipy': ['Nelder-Mead', 'Powell', 'CG', 'BFGS',
                   'Newton-CG', 'L-BFGS-B', 'TNC', 'SLSQP'],
         'scipy_ls': ['lm-scipy', 'trf', 'dogbox'],
         'scipy_go': ['differential_evolution', 'shgo', 'dual_annealing']}
    VALID_FITTING = \
        {'algorithm_type': ['all', 'ls', 'deriv_free', 'general', 'simplex',
                            'trust_region', 'levenberg-marquardt',
                            'gauss_newton', 'bfgs', 'conjugate_gradient',
                            'steepest_descent', 'global_optimization'],
         'software': ['bumps', 'dfo', 'gradient_free', 'gsl', 'levmar',
                      'mantid', 'matlab', 'matlab_curve', 'matlab_opt',
                      'matlab_stats', 'minuit', 'ralfit', 'scipy',
                      'scipy_ls', 'scipy_go'],
         'jac_method': ['scipy', 'analytic', 'default', 'numdifftools'],
         'hes_method': ['scipy', 'analytic', 'default', 'numdifftools'],
         'cost_func_type': ['nlls', 'weighted_nlls', 'hellinger_nlls',
                            'poisson']}
    VALID_JACOBIAN = \
        {'scipy': ['2-point', '3-point', 'cs'],
         'analytic': ['default'],
         'default': ['default'],
         'numdifftools': ['central',
                          'complex', 'multicomplex',
                          'forward', 'backward']}
    VALID_HESSIAN = \
        {'scipy': ['2-point', '3-point', 'cs'],
         'analytic': ['default'],
         'default': ['default'],
         'numdifftools': ['central',
                          'complex', 'multicomplex',
                          'forward', 'backward']}
    VALID_PLOTTING = \
        {'make_plots': [True, False],
         'comparison_mode': ['abs', 'rel', 'both'],
         'table_type': ['acc', 'runtime', 'compare', 'local_min'],
         'colour_map': plt.colormaps()}
    VALID_OUTPUT = {}
    VALID_LOGGING = \
        {'level': ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR',
                   'CRITICAL'],
         'append': [True, False],
         'external_output': ['debug', 'display', 'log_only']}

    VALID = {'MINIMIZERS': VALID_MINIMIZERS,
             'FITTING': VALID_FITTING,
             'JACOBIAN': VALID_JACOBIAN,
             'HESSIAN': VALID_HESSIAN,
             'PLOTTING': VALID_PLOTTING,
             'OUTPUT': VALID_OUTPUT,
             'LOGGING': VALID_LOGGING}

    DEFAULT_MINIMZERS = \
        {'bumps': ['amoeba', 'lm-bumps', 'newton', 'mp'],
         'dfo': ['dfogn', 'dfols'],
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
         'levmar': ['levmar'],
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
         'minuit': ['minuit'],
         'ralfit': ['gn', 'gn_reg', 'hybrid', 'hybrid_reg'],
         'scipy': ['Nelder-Mead', 'Powell', 'CG', 'BFGS',
                   'Newton-CG', 'L-BFGS-B', 'TNC', 'SLSQP'],
         'scipy_ls': ['lm-scipy', 'trf', 'dogbox'],
         'scipy_go': ['differential_evolution', 'dual_annealing']}
    DEFAULT_FITTING = \
        {'num_runs': 5,
         'algorithm_type': ['all'],
         'software': ['scipy', 'scipy_ls'],
         'jac_method': ['scipy'],
         'hes_method': ['default'],
         'cost_func_type': ['weighted_nlls'],
         'max_runtime': 600}
    DEFAULT_JACOBIAN = \
        {'analytic': ['default'],
         'scipy': ['2-point'],
         'default': ['default'],
         'numdifftools': ['central']}
    DEFAULT_HESSIAN = \
        {'analytic': ['default'],
         'scipy': ['2-point'],
         'default': ['default'],
         'numdifftools': ['central']}
    DEFAULT_PLOTTING = \
        {'make_plots': True,
         'colour_map': 'magma_r',
         'colour_ulim': 100,
         'cmap_range': [0.2, 0.8],
         'comparison_mode': 'both',
         'table_type': ['acc', 'runtime', 'compare', 'local_min']}
    DEFAULT_OUTPUT = \
        {'results_dir': 'fitbenchmarking_results'}
    DEFAULT_LOGGING = \
        {'file_name': 'fitbenchmarking.log',
         'append': False,
         'level': 'INFO',
         'external_output': 'log_only'}
    DEFAULTS = {'MINIMIZERS': DEFAULT_MINIMZERS,
                'FITTING': DEFAULT_FITTING,
                'JACOBIAN': DEFAULT_JACOBIAN,
                'HESSIAN': DEFAULT_HESSIAN,
                'PLOTTING': DEFAULT_PLOTTING,
                'OUTPUT': DEFAULT_OUTPUT,
                'LOGGING': DEFAULT_LOGGING}

    def __init__(self, file_name=None, results_directory: str = ""):
        """
        Initialise the options from a file if file is given.
        Priority is values in the file, failing that, values are taken from
        DEFAULTS (stored in ./default_options.ini)

        :param results_directory: The directory to store the results in.
        :type results_directory: str
        :param file_name: The options file to load
        :type file_name: str
        """
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
                    "Invalid options sections set, {0}, the valid sections "
                    "are {1}".format(config.sections(), self.VALID_SECTIONS))
            config.sections()

            # Checks that the options within the sections are valid
            for key in self.VALID_SECTIONS:
                default_options_list = list(self.DEFAULTS[key].keys())
                user_options_list = [option[0] for option in config.items(key)]
                if not set(user_options_list) <= set(default_options_list):
                    raise OptionsError(
                        "Invalid options key set in the {2} Section: \n{0}, \n"
                        " the valid keys are: \n{1}".format(
                            user_options_list,
                            default_options_list,
                            key))

        minimizers = config['MINIMIZERS']
        self._minimizers = {}
        self.minimizer_alg_type = {}
        for key in self.VALID_FITTING["software"]:
            self._minimizers[key] = self.read_value(minimizers.getlist,
                                                    key)

        fitting = config['FITTING']
        self.num_runs = self.read_value(fitting.getint, 'num_runs')
        self.algorithm_type = self.read_value(
            fitting.getlist, 'algorithm_type')
        self.software = self.read_value(fitting.getlist, 'software')
        self.jac_method = self.read_value(fitting.getlist, 'jac_method')
        self.hes_method = self.read_value(fitting.getlist, 'hes_method')
        self.cost_func_type = self.read_value(
            fitting.getlist, 'cost_func_type')
        self.max_runtime = self.read_value(fitting.getfloat, 'max_runtime')

        jacobian = config['JACOBIAN']
        self.jac_num_method = {}
        for key in self.VALID_FITTING["jac_method"]:
            self.jac_num_method[key] = self.read_value(jacobian.getlist,
                                                       key)

        hessian = config['HESSIAN']
        self.hes_num_method = {}
        for key in self.VALID_FITTING["hes_method"]:
            self.hes_num_method[key] = self.read_value(hessian.getlist,
                                                       key)

        plotting = config['PLOTTING']
        self.make_plots = self.read_value(plotting.getboolean, 'make_plots')
        self.colour_map = self.read_value(plotting.getstr, 'colour_map')
        self.colour_ulim = self.read_value(plotting.getfloat, 'colour_ulim')
        self.cmap_range = self.read_value(plotting.getrng, 'cmap_range')

        self.comparison_mode = self.read_value(plotting.getstr,
                                               'comparison_mode')
        self.table_type = self.read_value(plotting.getlist, 'table_type')

        output = config['OUTPUT']
        if results_directory == "":
            self.results_dir = self.read_value(output.getstr, 'results_dir')
        else:
            self.results_dir = results_directory

        logging = config['LOGGING']
        self.log_append = self.read_value(logging.getboolean, 'append')
        self.log_file = self.read_value(logging.getstr, 'file_name')
        self.log_level = self.read_value(logging.getstr, 'level')

        self.external_output = self.read_value(logging.getstr,
                                               'external_output')

        if self.error_message != []:
            raise OptionsError('\n'.join(self.error_message))

    def reset(self):
        """
        Resets options object when running multiple problem groups.
        """
        self.__init__(self.stored_file_name, self.results_dir)

    def read_value(self, func, option):
        """
        Helper function which loads in the value

        :param func: configparser function
        :type func: callable
        :param option: option to be read for file
        :type option: str

        :return: value of the option
        :rtype: list/str/int/bool
        """
        section = func.__str__().split("Section: ")[1].split('>')[0]
        try:
            value = func(option, fallback=self.DEFAULTS[section][option])
        except ValueError as e:
            self.error_message.append(
                "Incorrect options type for {}.\n{}".format(option, e))
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
        config['FITTING'] = {'num_runs': self.num_runs,
                             'algorithm_type': list_to_string(
                                 self.algorithm_type),
                             'software': list_to_string(self.software),
                             'jac_method': list_to_string(self.jac_method),
                             'hes_method': list_to_string(self.hes_method),
                             'max_runtime': self.max_runtime}
        config['JACOBIAN'] = {k: list_to_string(m)
                              for k, m in self.jac_num_method.items()}
        config['HESSIAN'] = {k: list_to_string(m)
                             for k, m in self.hes_num_method.items()}

        config['PLOTTING'] = {'colour_map': self.colour_map,
                              'cmap_range': self.cmap_range,
                              'colour_ulim': self.colour_ulim,
                              'comparison_mode': self.comparison_mode,
                              'make_plots': self.make_plots,
                              'table_type': list_to_string(self.table_type)}
        config['OUTPUT'] = {'results_dir': self.results_dir}
        config['LOGGING'] = {'file_name': self.log_file,
                             'level': self.log_level,
                             'append': self.log_append,
                             'external_output': self.external_output}

        return config

    def write(self, file_name):
        """
        Write the contents of the options object to a new options file.

        :param file_name: The path to the new options file
        :type file_name: str
        """
        config = self._create_config()

        with open(file_name, 'w') as f:
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
