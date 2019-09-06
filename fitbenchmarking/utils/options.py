'''
This file will handle all interaction with the options configuration file.
'''

import json


def get_option(options_file='fitbenchmarking/fitbenchmarking_default_options.json', option=None):
    '''
    Get a value for the given option from a config file.

    The options file should contain json formatted data
    The default path is fitbenchmarking/fitbenchmarking_default_options.json

    @param options_file :: The file name for the options configuration.
    @param option :: String for specifying the option to return.
    @returns :: json parsed item from the options file
    '''
    options = json.load(open(options_file, 'r'))
    if option is None:
        return options
    else:
        try:
            return options[option]
        except KeyError:
            raise ValueError('Option not found in file: {}'.format(options_file))
