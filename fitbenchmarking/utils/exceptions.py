"""
This file holds all FitBenchmarking exceptions, organised by exception id
"""


class FitBenchmarkException(Exception):
    """
    The base class for all FitBenchmarking exceptions

    To define a new exception, inherrit from this and override the
    _class_message
    """
    class_message = 'An unknown exception occurred.'
    error_code = 1

    def __init__(self, message=''):
        super().__init__(message)
        self._obj_message = message
        self._error_string = None

    def __str__(self):
        if self._obj_message != '':
            self._error_string = '{}\nDetails: {}'.format(self.class_message,
                                                          self._obj_message)
        else:
            self._error_string = self.class_message

        return self._error_string.strip()


class ValidationException(FitBenchmarkException):
    """
    This should be subclassed to indicate any validation errors that preclude
    a combination from running.
    """
    class_message = "An error occured while verifying controller."


class OptionsError(FitBenchmarkException):
    """
    Indicates an error during processing options.
    """
    class_message = 'Failed to process options.'
    error_code = 2


class ParsingError(FitBenchmarkException):
    """
    Indicates an error during parsing.
    """
    class_message = 'Could not parse problem.'
    error_code = 3


class NoParserError(FitBenchmarkException):
    """
    Indicates a parser could not be found.
    """
    class_message = 'Could not find parser.'
    error_code = 4


class MissingSoftwareError(FitBenchmarkException):
    """
    Indicates that the requirements for a software package are not available.
    """
    class_message = 'Missing dependencies for fit.'
    error_code = 5


class NoControllerError(FitBenchmarkException):
    """
    Indicates a controller could not be found
    """
    class_message = 'Could not find controller.'
    error_code = 6


class ControllerAttributeError(FitBenchmarkException):
    """
    Indicates an issue with the attributes within a controller
    """
    class_message = 'Error in the controller attributes.'
    error_code = 7


class NoDataError(FitBenchmarkException):
    """
    Indicates that no data could be found.
    """
    class_message = 'No data found.'
    error_code = 8


class UnknownMinimizerError(FitBenchmarkException):
    """
    Indicates that the controller does not support a given minimizer given
    the current "algorithm_type" option set.
    """
    class_message = 'Minimizer cannot be run with Controller with ' \
                    'current "algorithm_type" option set.'
    error_code = 9


class FittingProblemError(FitBenchmarkException):
    """
    Indicates a problem with the fitting problem.
    """
    class_message = 'Fitting Problem raised and exception.'
    error_code = 10


class NoJacobianError(FitBenchmarkException):
    """
    Indicates a problem with the Jacobian import.
    """
    class_message = 'Could not find Jacobian class'
    error_code = 11


class NoAnalyticJacobian(FitBenchmarkException):
    """
    Indicates when no Jacobian data files can be found
    """
    class_message = 'Could not find Jacobian data files'
    error_code = 12


class UnknownTableError(FitBenchmarkException):
    """
    Indicates a problem with the fitting problem.
    """
    class_message = 'Set table option could not be found'
    error_code = 13


class NoResultsError(FitBenchmarkException):
    """
    Indicates a problem with the fitting problem.
    """
    class_message = 'FitBenchmarking ran with no results'
    error_code = 14


class UnsupportedMinimizerError(FitBenchmarkException):
    """
    Indicates that the controller does not support a given minimizer.
    """
    class_message = 'FitBenchmarking ran with no results'
    error_code = 15


class CostFuncError(FitBenchmarkException):
    """
    Indicates a problem with the cost function class.
    """
    class_message = 'FitBenchmarking ran with no results'
    error_code = 16


class IncompatibleMinimizerError(FitBenchmarkException):
    """
    Indicates that the selected minimizer is not compatible
    with selected options/problem set
    """
    class_message = 'Minimizer cannot be used with ' \
                    'selected options/problem set'
    error_code = 17


class IncompatibleTableError(FitBenchmarkException):
    """
    Indicates that selected cost function and table are
    not compatible
    """
    class_message = 'The table type selected is not ' \
                    'compatible with the selected ' \
                    'cost function'
    error_code = 18


class IncorrectBoundsError(FitBenchmarkException):
    """
    Indicates that `parameter_ranges` have been set incorrectly
    """
    class_message = 'Bounds for this problem are ' \
                    'unable to be set, so this ' \
                    'problem will be skipped.'
    error_code = 19


class MissingBoundsError(FitBenchmarkException):
    """
    Indicates that `parameter_ranges` have not been set but are required
    """
    class_message = 'Bounds on all parameters ' \
                    'are required to use this ' \
                    'software.'
    error_code = 20


class PlottingError(FitBenchmarkException):
    """
    Indicates an error during plotting results
    """
    class_message = 'An error occurred during plotting.'
    error_code = 21


class NoHessianError(FitBenchmarkException):
    """
    Indicated a problem with Hessian import
    """
    class_message = 'Could not find Hessian class'
    error_code = 22


class MaxRuntimeError(FitBenchmarkException):
    """
    Indicates a minimizer has taken too long to run
    """
    class_message = 'Minimizer runtime exceeded maximum runtime'
    error_code = 23


class IncompatibleJacobianError(ValidationException):
    """
    Indicates that the selected jacobian method is not compatible
    with selected options/problem set
    """
    class_message = 'The provided Jacobian method cannot be used with ' \
                    'the selected options or problem set.'
    error_code = 24


class FilepathTooLongError(FitBenchmarkException):
    """
    Indicates the filepath to save a file to is too long.
    """
    class_message = 'The filepath for saving a file is too long.'
    error_code = 25


class IncompatibleHessianError(ValidationException):
    """
    Indicates that the selected Hessian method is not compatible
    with selected options/problem set
    """
    class_message = 'The provided Hessian method cannot be used with ' \
                    'the selected options or problem set.'
    error_code = 26


class IncompatibleProblemError(ValidationException):
    """
    Indicates that the selected problem is not compatible with the selected
    options.
    """
    class_message = 'The selected software can not be used with the given ' \
                    'problem.'
    error_code = 27
