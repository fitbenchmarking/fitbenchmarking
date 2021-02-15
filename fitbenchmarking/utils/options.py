'''
This file will handle all interaction with the options configuration file.
'''

import configparser

import os
import numpy as np

from fitbenchmarking.utils.exceptions import OptionsError


class Options(object):
    """
    An options class to store and handle all options for fitbenchmarking
    """

    DEFAULTS = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'default_options.ini'))
    VALID_SECTIONS = ['MINIMIZERS', 'FITTING', 'PLOTTING', 'LOGGING']
    VALID_MINIMIZERS = \
        {'bumps': ['amoeba', 'lm-bumps', 'newton', 'de', 'mp'],
         'dfo': ['dfogn', 'dfols'],
         'gsl': ['lmsder', 'lmder', 'nmsimplex', 'nmsimplex2',
                 'conjugate_pr', 'conjugate_fr', 'vector_bfgs',
                 'vector_bfgs2', 'steepest_descent'],
         'mantid': ['BFGS',
                    'Conjugate gradient (Fletcher-Reeves imp.)',
                    'Conjugate gradient (Polak-Ribiere imp.)',
                    'Damped GaussNewton', 'Levenberg-Marquardt',
                    'Levenberg-MarquardtMD', 'Simplex',
                    'SteepestDescent', 'Trust Region'],
         'minuit': ['minuit'],
         'ralfit': ['gn', 'gn_reg', 'hybrid', 'hybrid_reg'],
         'scipy': ['Nelder-Mead', 'Powell', 'CG', 'BFGS',
                   'Newton-CG', 'L-BFGS-B', 'TNC', 'SLSQP'],
         'scipy_ls': ['lm-scipy-no-jac', 'lm-scipy', 'trf',
                      'dogbox']}
    VALID_FITTING = \
        {'algorithm_type': ['all', 'ls', 'deriv_free', 'general'],
         'software': ['bumps', 'dfo', 'gsl', 'mantid', 'minuit',
                      'ralfit', 'scipy', 'scipy_ls'],
         'use_errors': [True, False],
         'jac_method': ['SciPyFD'],
         'num_method': ['2point', '3point', 'cs']}
    VALID_PLOTTING = \
        {'make_plots': [True, False],
         'comparison_mode': ['abs', 'rel', 'both'],
         'table_type': ['acc', 'runtime', 'compare', 'local_min']}
    VALID_LOGGING = \
        {'level': ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR',
                   'CRITICAL'],
         'append': [True, False],
         'external_output': ['debug','display','log_only']}

    VALID = {'MINIMIZERS': VALID_MINIMIZERS,
             'FITTING': VALID_FITTING,
             'PLOTTING': VALID_PLOTTING,
             'LOGGING': VALID_LOGGING}

    DEFAULT_MINIMZERS = \
        {'bumps': ['amoeba', 'lm-bumps', 'newton', 'mp'],
         'dfo': ['dfogn', 'dfols'],
         'gsl': ['lmsder', 'lmder', 'nmsimplex', 'nmsimplex2',
                 'conjugate_pr', 'conjugate_fr', 'vector_bfgs',
                 'vector_bfgs2', 'steepest_descent'],
         'mantid': ['BFGS',
                    'Conjugate gradient (Fletcher-Reeves imp.)',
                    'Conjugate gradient (Polak-Ribiere imp.)',
                    'Damped GaussNewton', 'Levenberg-Marquardt',
                    'Levenberg-MarquardtMD', 'Simplex',
                    'SteepestDescent', 'Trust Region'],
         'minuit': ['minuit'],
         'ralfit': ['gn', 'gn_reg', 'hybrid', 'hybrid_reg'],
         'scipy': ['Nelder-Mead', 'Powell', 'CG', 'BFGS',
                   'Newton-CG', 'L-BFGS-B', 'TNC'],
         'scipy_ls': ['lm-scipy-no-jac', 'lm-scipy', 'trf',
                      'dogbox']}
    DEFAULT_FITTING = \
        {'num_runs': 5,
         'algorithm_type': 'all',
         'software': ['scipy', 'scipy_ls'],
         'use_errors': True,
         'jac_method': 'SciPyFD',
         'num_method': '2point'}
    DEFAULT_PLOTTING = \
        {'make_plots': True,
         'colour_scale': [(1.1, "#fef0d9"),
                          (1.33, "#fdcc8a"),
                          (1.75, "#fc8d59"),
                          (3, "#e34a33"),
                          (np.inf, "#b30000")],
         'comparison_mode': 'both',
         'table_type': ['acc', 'runtime', 'compare', 'local_min'],
         'results_dir': 'fitbenchmarking_results'}
    DEFAULT_LOGGING = \
        {'file_name': 'fitbenchmarking.log',
         'append': False,
         'level': 'INFO',
         'external_output': 'log_only'}
    DEFAULTS = {'MINIMIZERS': DEFAULT_MINIMZERS,
                'FITTING': DEFAULT_FITTING,
                'PLOTTING': DEFAULT_PLOTTING,
                'LOGGING': DEFAULT_LOGGING}

    def __init__(self, file_name=None):
        """
        Initialise the options from a file if file is given.
        Priority is values in the file, failing that, values are taken from
        DEFAULTS (stored in ./default_options.ini)

        :param file_name: The options file to load
        :type file_name: str
        """
        # stores the file name to be used to reset options for multiple
        # problem groups
        self.stored_file_name = file_name
        self.error_message = []
        self._results_dir = ''
        config = configparser.ConfigParser(converters={'list': read_list,
                                                       'str': str},
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
                if not (set(user_options_list) <= set(default_options_list)):
                    raise OptionsError(
                        "Invalid options key set: \n{0}, \n the valid keys "
                        "are: \n{1}".format(user_options_list,
                                            default_options_list))

        minimizers = config['MINIMIZERS']
        self._minimizers = {}
        for key in self.VALID_FITTING["software"]:
            self._minimizers[key] = self.read_value(minimizers.getlist,
                                                    key)

        fitting = config['FITTING']
        self.num_runs = self.read_value(fitting.getint, 'num_runs')
        self.algorithm_type = self.read_value(fitting.getstr, 'algorithm_type')
        self.software = self.read_value(fitting.getlist, 'software')
        self.use_errors = self.read_value(fitting.getboolean, 'use_errors')
        self.jac_method = self.read_value(fitting.getstr, 'jac_method')
        self.num_method = self.read_value(fitting.getstr, 'num_method')

        plotting = config['PLOTTING']
        self.make_plots = self.read_value(plotting.getboolean, 'make_plots')
        self.colour_scale = self.read_value(plotting.getlist, 'colour_scale')
        check = [isinstance(c, tuple) for c in self.colour_scale]
        if check.count(False) == len(check):
            self.colour_scale = [(float(cs.split(',', 1)[0].strip()),
                                  cs.split(',', 1)[1].strip())
                                 for cs in self.colour_scale]
        self.comparison_mode = self.read_value(plotting.getstr,
                                               'comparison_mode')
        self.table_type = self.read_value(plotting.getlist, 'table_type')
        self.results_dir = self.read_value(plotting.getstr, 'results_dir')

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
        self.__init__(self.stored_file_name)

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
        except ValueError:
            self.error_message.append(
                "Incorrect options type for {}".format(option))
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
                    "The option '{0}: {1}' in the ini file is invalid. {0} "
                    "must be on or more of {2}".format(
                        option, value, self.VALID[section][option]))
        return value

    @property
    def results_dir(self):
        return self._results_dir

    @results_dir.setter
    def results_dir(self, value):
        self._results_dir = os.path.abspath(value)

    @property
    def minimizers(self):
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
                                                       'str': str})

        def list_to_string(l):
            return '\n'.join(l)

        config['MINIMIZERS'] = {k: list_to_string(m)
                                for k, m in self.minimizers.items()}
        config['FITTING'] = {'num_runs': self.num_runs,
                             'algorithm_type': self.algorithm_type,
                             'software': list_to_string(self.software),
                             'use_errors': self.use_errors,
                             'jac_method': self.jac_method,
                             'num_method': self.num_method}
        cs = list_to_string(['{0}, {1}'.format(*pair)
                             for pair in self.colour_scale])
        config['PLOTTING'] = {'colour_scale': cs,
                              'comparison_mode': self.comparison_mode,
                              'make_plots': self.make_plots,
                              'results_dir': self.results_dir,
                              'table_type': list_to_string(self.table_type)}
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
