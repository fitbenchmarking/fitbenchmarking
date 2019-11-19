'''
This file will handle all interaction with the options configuration file.
'''

import configparser
from json import loads


class Options:
    """
    An options class to store and handle all options for fitbenchmarking
    """

    DEFAULTS = u"""
        [MINIMIZERS]
        dfogn: dfogn
        mantid: BFGS
                Conjugate gradient (Fletcher-Reeves imp.)
                Conjugate gradient (Polak-Ribiere imp.)
                Damped GaussNewton
                Levenberg-Marquardt
                Levenberg-MarquardtMD
                Simplex
                SteepestDescent
                Trust Region
        ralfit: ralfit
        sasview: amoeba
                 lm
                 newton
                 de
                 mp
        scipy: lm
               trf
               dogbox

        [FITTING]
        comparison_mode: both
        num_runs: 5
        software: dfogn
                  mantid
                  ralfit
                  sasview
                  scipy
        use_errors: yes

        [PLOTTING]
        colour_scale: 1.1, ranking-top-1
                      1.33, ranking-top-2
                      1.75, ranking-med-3
                      3, ranking-low-4
                      nan, ranking-low-5
        comparison_mode: both
        results_dir: results
        """

    def __init__(self, file_name=None):
        """
        Initialise the options from a file if  file is given.
        Priority is values in the file, failing that, values are taken from
        DEFAULTS (above)

        :param file_name: The options file to load
        :type file_name: str
        """
        config = configparser.ConfigParser(converters={'list': read_list, 'str': str})

        config.read_string(self.DEFAULTS)
        if file_name is not None:
            config.read(file_name)

        minimizers = config['MINIMIZERS']
        self.minimizers = {}
        for key in minimizers.keys():
            self.minimizers[key] = minimizers.getlist(key)

        fitting = config['FITTING']
        self.num_runs = fitting.getint('num_runs')
        self.software = fitting.getlist('software')
        self.use_errors = fitting.getboolean('use_errors')

        plotting = config['PLOTTING']
        self.colour_scale = plotting.getlist('colour_scale')
        self.colour_scale = [(float(cs.split(',', 1)[0].strip()),
                              cs.split(',', 1)[1].strip())
                             for cs in self.colour_scale]
        self.comparison_mode = plotting.getstr('comparison_mode')
        self.results_dir = plotting.getstr('results_dir')


def read_list(s):
    return str(s).split('\n')
