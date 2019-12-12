from __future__ import (absolute_import, division, print_function)


class FittingResult(object):
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(self):
        self.problem = None
        self.fit_status = None
        self.chi_sq = None

        # Workspace with data to fit
        self.fit_wks = None
        self.params = None
        self.errors = None

        # Time it took to run the Fit algorithm
        self.runtime = None

        # Best minimizer for a certain problem and its function definition
        self.minimizer = None
        self.ini_function_def = None
        self.fin_function_def = None

    def __repr__(self):
        return 'Fitting problem class: minimizer = {0}'.format(self.minimizer)
