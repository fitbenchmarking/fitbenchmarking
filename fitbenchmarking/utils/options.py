'''
This file will handle all interaction with the options configuration file.
'''

import configparser

import os

from fitbenchmarking.utils.exceptions import OptionsError


class Options(object):
    """
    An options class to store and handle all options for fitbenchmarking
    """

    DEFAULTS = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'default_options.ini'))

    def __init__(self, file_name=None):
        """
        Initialise the options from a file if file is given.
        Priority is values in the file, failing that, values are taken from
        DEFAULTS (stored in ./default_options.ini)

        :param file_name: The options file to load
        :type file_name: str
        """
        error_message = []
        template = "The option '{0}' must be of type {1}."
        self._results_dir = ''
        config = configparser.ConfigParser(converters={'list': read_list,
                                                       'str': str})

        config.read(self.DEFAULTS)
        if file_name is not None:
            config.read(file_name)

        minimizers = config['MINIMIZERS']
        self.minimizers = {}
        for key in minimizers.keys():
            self.minimizers[key] = minimizers.getlist(key)

        fitting = config['FITTING']
        try:
            self.num_runs = fitting.getint('num_runs')
        except ValueError:
            error_message.append(template.format('num_runs', "int"))
        self.algorithm_type = fitting.getstr('algorithm_type')
        self.software = fitting.getlist('software')
        try:
            self.use_errors = fitting.getboolean('use_errors')
        except ValueError:
            error_message.append(template.format('use_errors', "boolean"))
        self.jac_method = fitting.getstr('jac_method')

        plotting = config['PLOTTING']
        try:
            self.make_plots = plotting.getboolean('make_plots')
        except ValueError:
            error_message.append(template.format('make_plots', "boolean"))

        self.colour_scale = plotting.getlist('colour_scale')
        self.colour_scale = [(float(cs.split(',', 1)[0].strip()),
                              cs.split(',', 1)[1].strip())
                             for cs in self.colour_scale]
        self.comparison_mode = plotting.getstr('comparison_mode')
        self.table_type = plotting.getlist('table_type')
        self.results_dir = plotting.getstr('results_dir')

        logging = config['LOGGING']
        try:
            self.log_append = logging.getboolean('append')
        except ValueError:
            error_message.append(template.format('append', "boolean"))
        self.log_file = logging.getstr('file_name')
        self.log_level = logging.getstr('level')

        try:
            self.external_output = logging.getboolean('external_output')
        except ValueError:
            error_message.append(template.format('external_output', "boolean"))

        # sys.exit() will be addressed in future FitBenchmarking
        # error handling issue
        if error_message != []:
            raise OptionsError('\n'.join(error_message))

    @property
    def results_dir(self):
        return self._results_dir

    @results_dir.setter
    def results_dir(self, value):
        self._results_dir = os.path.abspath(value)

    def write(self, file_name):
        """
        Write the contents of the options object to a new options file.

        :param file_name: The path to the new options file
        :type file_name: str
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
                             'jac_method': self.jac_method}
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

        with open(file_name, 'w') as f:
            config.write(f)


def read_list(s):
    """
    Utility function to allow lists to be read by the config parser

    :param s: string to convert to a list
    :type s: string
    :return: list of items
    :rtype: list of str
    """
    return str(s).split('\n')
