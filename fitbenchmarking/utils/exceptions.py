"""
This file holds all FitBenchmarking exceptions, organised by exception id
"""


class FitBenchmarkException(Exception):
    """
    The base class for all FitBenchmarking exceptions

    To define a new exception, inherrit from this and override the
    _class_message
    """

    def __init__(self, message=''):
        super(FitBenchmarkException, self).__init__(message)
        self._class_message = 'An unknown exception occurred.'
        self._obj_message = message
        self.error_code = 1
        self._error_string = None

    def __str__(self):
        if self._obj_message != '':
            self._error_string = '{}\nDetails: {}'.format(self._class_message,
                                                          self._obj_message)
        else:
            self._error_string = self._class_message

        return self._error_string.strip()


class OptionsError(FitBenchmarkException):
    """
    Indicates an error during processing options.
    """

    def __init__(self, message=''):
        super(OptionsError, self).__init__(message)

        self._class_message = 'Failed to process options.'
        self.error_code = 2


class ParsingError(FitBenchmarkException):
    """
    Indicates an error during parsing.
    """

    def __init__(self, message=''):
        super(ParsingError, self).__init__(message)

        self._class_message = 'Could not parse problem.'
        self.error_code = 3


class NoParserError(FitBenchmarkException):
    """
    Indicates a parser could not be found.
    """

    def __init__(self, message=''):
        super(NoParserError, self).__init__(message)

        self._class_message = 'Could not find parser.'
        self.error_code = 4


class MissingSoftwareError(FitBenchmarkException):
    """
    Indicates that the requirements for a software package are not available.
    """

    def __init__(self, message=''):
        super(MissingSoftwareError, self).__init__(message)

        self._class_message = 'Missing dependencies for fit.'
        self.error_code = 5


class NoControllerError(FitBenchmarkException):
    """
    Indicates a controller could not be found
    """

    def __init__(self, message=''):
        super(NoControllerError, self).__init__(message)

        self._class_message = 'Could not find controller.'
        self.error_code = 6


class ControllerAttributeError(FitBenchmarkException):
    """
    Indicates an issue with the attributes within a controller
    """

    def __init__(self, message=''):
        super(ControllerAttributeError, self).__init__(message)

        self._class_message = 'Error in the controller attributes.'
        self.error_code = 7


class NoDataError(FitBenchmarkException):
    """
    Indicates that no data could be found.
    """

    def __init__(self, message=''):
        super(NoDataError, self).__init__(message)

        self._class_message = 'No data found.'
        self.error_code = 8


class UnknownMinimizerError(FitBenchmarkException):
    """
    Indicates that the controller does not support a given minimizer given
    the current "algorithm_type" option set.
    """

    def __init__(self, message=''):
        super(UnknownMinimizerError, self).__init__(message)

        self._class_message = 'Minimizer cannot be run with Controller with ' \
                              'current "algorithm_type" option set.'
        self.error_code = 9


class FittingProblemError(FitBenchmarkException):
    """
    Indicates a problem with the fitting problem.
    """

    def __init__(self, message=''):
        super(FittingProblemError, self).__init__(message)

        self._class_message = 'Fitting Problem raised and exception.'
        self.error_code = 10


class NoJacobianError(FitBenchmarkException):
    """
    Indicates a problem with the Jacobian import.
    """

    def __init__(self, message=''):
        super(NoJacobianError, self).__init__(message)

        self._class_message = 'Could not find Jacobian class'
        self.error_code = 11


class UnknownTableError(FitBenchmarkException):
    """
    Indicates a problem with the fitting problem.
    """

    def __init__(self, message=''):
        super(UnknownTableError, self).__init__(message)

        self._class_message = 'Set table option could not be found'
        self.error_code = 12


class NoResultsError(FitBenchmarkException):
    """
    Indicates a problem with the fitting problem.
    """

    def __init__(self, message=''):
        super(NoResultsError, self).__init__(message)

        self._class_message = 'FitBenchmarking ran with no results'
        self.error_code = 13


class UnsupportedMinimizerError(FitBenchmarkException):
    """
    Indicates that the controller does not support a given minimizer.
    """

    def __init__(self, message=''):
        super(UnsupportedMinimizerError, self).__init__(message)

        self._class_message = 'FitBenchmarking ran with no results'
        self.error_code = 14
