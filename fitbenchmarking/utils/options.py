'''
This file will handle all interaction with the options configuration file.
'''

import configparser

from json import loads
import os


class Options(object):
    """
    An options class to store and handle all options for fitbenchmarking
    """

    DEFAULTS = u"""
        #################################################################################
        # This section is used to declare the minimizers to use for each fitting software
        # In most cases this can be left out, and defaults will be sufficient
        #################################################################################
        [MINIMIZERS]
        # To override the selection that is made by default, you should provide an entry
        # for the software with a newline separated list of minimizers
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
        ralfit: gn
                gn_reg
                hybrid
                hybrid_reg
        sasview: amoeba
                 lm-bumps
                 newton
                 de
                 mp
        scipy: lm-scipy
               trf
               dogbox

        ###########################################################################
        # The fitting section is used for options specific to running the benchmark
        ###########################################################################
        [FITTING]
        # num_runs sets the number of runs to average each fit over
        # default is 5
        num_runs: 5
        # software is used to select the fitting software to benchmark
        # this should be a newline-separated list
        # default is dfon, mantid, ralfit, sasview, and scipy
        software: dfogn
                  mantid
                  ralfit
                  sasview
                  scipy
        # use_errors will switch between weighted and unweighted least squares
        # default is True (yes/no can also be used)
        use_errors: yes

        ############################################################################
        # The plotting section contains options to control how results are presented
        ############################################################################
        [PLOTTING]
        # colour_scale lists thresholds for each colour in the html table
        #              In the below example, this means that values less than 1.1
        #              will have the top ranking (brightest) and values over 3
        #              will show as the worst ranking (deep red)
        # default thresholds are 1.1, 1.33, 1.75, 3, and inf
        colour_scale: 1.1, ranking-top-1
                      1.33, ranking-top-2
                      1.75, ranking-med-3
                      3, ranking-low-4
                      inf, ranking-low-5
        # comparison_mode selects the mode for displaying values in the resulting table
        #                 options are 'abs', 'rel', 'both'
        #                 'abs' indicates that the absolute values should be displayed
        #                 'rel' indicates that the values should all be relative to
        #                       the best performing
        #                 'both' will show data in the form "abs (rel)"
        # default is both
        comparison_mode: both
        # results_dir is used to select where the output should be saved
        # default is results
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
        self._results_dir = ''

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

    @property
    def results_dir(self):
        return self._results_dir

    @results_dir.setter
    def results_dir(self, value):
        self._results_dir = os.path.abspath(value)


def read_list(s):
    return str(s).split('\n')
