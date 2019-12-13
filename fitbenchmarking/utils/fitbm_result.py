from __future__ import (absolute_import, division, print_function)


class FittingResult(object):
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(self, problem=None, fit_status=None, chi_sq=None,
                 fit_wks=None, params=None, errors=None, runtime=None,
                 minimizer=None, ini_function_def=None, fin_function_def=None):
        self.problem = problem
        self.fit_status = fit_status
        self.chi_sq = chi_sq

        # Workspace with data to fit
        self.fit_wks = fit_wks
        self.params = params
        self.errors = errors

        # Time it took to run the Fit algorithm
        self.runtime = runtime

        # Best minimizer for a certain problem and its function definition
        self.minimizer = minimizer
        self.ini_function_def = ini_function_def
        self.fin_function_def = fin_function_def

    def __repr__(self):
        return 'Fitting problem class: minimizer = {0}'.format(self.minimizer)
