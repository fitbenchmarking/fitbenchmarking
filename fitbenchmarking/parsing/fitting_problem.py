"""
Implements the FittingProblem class, this will be the object that inputs are
parsed into before being passed to the controllers
"""

from __future__ import (absolute_import, division, print_function)

try:
    from itertools import izip_longest
except ImportError:
    # python3
    from itertools import zip_longest as izip_longest
import numpy as np

from fitbenchmarking.utils.debug import get_printable_table
from fitbenchmarking.utils.exceptions import FittingProblemError, \
    IncorrectBoundsError
from fitbenchmarking.utils.timer import TimerWithMaxTime


# Using property getters and setters means that the setter does not always use
# self
# pylint: disable=no-self-use
class FittingProblem:
    r"""
    Definition of a fitting problem, which will be populated by a parser from a
    problem definition file.

    Onces populated, this should include the data, the function and any other
    additional requirements from the data.
    """

    def __init__(self, options):
        """
        Initialises variable used for temporary storage.

        :param options: all the information specified by the user
        :type options: fitbenchmarking.utils.options.Options
        """
        self.options = options
        #: *string* Name (title) of the fitting problem
        self.name = None

        #: *string* Name of the problem definition type (e.g., 'cutest')
        self.format = None

        #: *string* Equation (function or model) to fit against data
        self.equation = None

        #: *string* Description of the fitting problem
        self.description = ''

        #: *float* The start of the range to fit model data over
        #: (if different from entire range)
        self.start_x = None

        #: *float* The end of the range to fit model data over
        #: (if different from entire range) (/float/)
        self.end_x = None

        #: *numpy array* The x-data
        self.data_x = None

        #: *numpy array* The y-data
        self.data_y = None

        #: *numpy array* The errors or weights
        self.data_e = None

        #: *list of dict*
        #: Starting values of the fitting parameters
        #:
        #: e.g.
        #: :code:`[{p1_name: p1_val1, p2_name: p2_val1, ...},
        #: {p1_name: p1_val2, ...}, ...]`
        self.starting_values: list = []

        #: *list*
        #: Smallest and largest values of interest in the data
        #:
        #: e.g.
        #: :code:`[(p1_min, p1_max), (p2_min, p2_max),...]`
        self.value_ranges = None

        #: Callable function
        self.function = None

        self._param_names = None

        #: *numpy array* The index for sorting the data (used in plotting)
        self.sorted_index = None

        #: *dict*
        #: Container for software specific information.
        #: This should be avoided if possible.
        self.additional_info = {}

        #: *bool* Used to check if a problem is using multifit.
        self.multifit = False

        #: Callable function for the Jacobian
        self.jacobian = None

        #: *bool*
        #: Whether the function has been wrapped to reduce the dimension of x
        #: on function calls
        self.multivariate = False

        #: Callable function for the Hessian
        self.hessian = None

        # The timer used to check if the 'max_runtime' is exceeded.
        self.timer = TimerWithMaxTime(self.options.max_runtime)

    def __str__(self):
        info = {"Name": self.name,
                "Format": self.format,
                "Equation": self.equation,
                "Params": self._param_names,
                "Start X": self.start_x,
                "End X": self.end_x,
                "MultiFit": self.multifit}

        return get_printable_table("FittingProblem", info)

    def eval_model(self, params, **kwargs):
        """
        Function evaluation method

        :param params: parameter value(s)
        :type params: list

        :return: data values evaluated from the function of the problem
        :rtype: numpy array
        """
        if self.function is None:
            raise FittingProblemError('Cannot call function before setting '
                                      'function.')

        self.timer.check_elapsed_time()

        x = kwargs.get("x", self.data_x)
        return self.function(x, *params)  # pylint: disable=not-callable

    @property
    def param_names(self):
        """
        Utility function to get the parameter names

        :return: the names of the parameters
        :rtype: list of str
        """
        if self._param_names is None:
            self._param_names = list(self.starting_values[0].keys())
        return self._param_names

    @param_names.setter
    def param_names(self, value):
        raise FittingProblemError('param_names should not be edited')

    def get_function_params(self, params):
        """
        Return the function definition in a string format for output

        :param params: The parameters to use in the function string
        :type params: list

        :return: Representation of the function
                 example format: 'b1 * (b2+x) | b1=-2.0, b2=50.0'
        :rtype: string
        """
        params = ['{}={}'.format(n, p) for n, p
                  in izip_longest(self.param_names,
                                  params if params is not None else [])]
        param_string = ', '.join(params)

        return param_string

    def verify(self):
        """
        Basic check that minimal set of attributes have been set.

        Raise FittingProblemError if object is not properly initialised.
        """
        values = {'data_x': np.ndarray,
                  'data_y': np.ndarray,
                  'starting_values': list}

        for attr_name, attr_type in values.items():
            attr = getattr(self, attr_name)
            type_match = isinstance(attr, attr_type)
            try:
                type_match = type_match or isinstance(attr[0], attr_type)  # NOQA; pylint: disable=unsubscriptable-object
            except (TypeError, IndexError):
                pass
            if not type_match:
                raise FittingProblemError(
                    'Attribute "{}" is not the expected type. Expected "{}", '
                    'got "{}".'.format(attr_name, attr_type, type(attr)))
        if self.function is None:
            raise FittingProblemError('Attribute "function" has not been set.')

    def correct_data(self):
        """
        Strip data that overruns the start and end x_range,
        and approximate errors if not given.
        Modifications happen on member variables.
        """
        use_errors = "weighted_nlls" in self.options.cost_func_type
        if not self.multifit:
            correct_vals = correct_data(x=self.data_x,
                                        y=self.data_y,
                                        e=self.data_e,
                                        startx=self.start_x,
                                        endx=self.end_x,
                                        use_errors=use_errors)
            self.data_x = correct_vals[0]
            self.data_y = correct_vals[1]
            self.data_e = correct_vals[2]
            self.sorted_index = correct_vals[3]
        else:
            # Mantid multifit problem
            self.sorted_index = []
            num_data = len(self.data_x)
            for i in range(num_data):
                # pylint: disable=unsubscriptable-object
                correct_vals = correct_data(x=self.data_x[i],
                                            y=self.data_y[i],
                                            e=self.data_e[i],
                                            startx=self.start_x[i],
                                            endx=self.end_x[i],
                                            use_errors=use_errors)
                self.data_x[i] = correct_vals[0]
                self.data_y[i] = correct_vals[1]
                self.data_e[i] = correct_vals[2]
                self.sorted_index.append(correct_vals[3])

    def set_value_ranges(self, value_ranges):
        """
        Function to format parameter bounds before passing to controllers,
        so self.value_ranges is a list of tuples, which contain lower and
        upper bounds (lb,ub) for each parameter in the problem

        :param value_ranges: dictionary of bounded parameter names with
                             lower and upper bound values e.g.
                            :code:`{p1_name: [p1_min, p1_max], ...}`
        :type value_ranges: dict
        """
        lower_param_names = [name.lower()
                             for name in self.starting_values[0].keys()]
        if not all(name in lower_param_names for name in value_ranges):
            raise IncorrectBoundsError('One or more of the parameter names in '
                                       'the `parameter_ranges` dictionary is '
                                       'incorrect, please check the problem '
                                       'definiton file for this problem.')

        self.value_ranges = []
        for name in lower_param_names:
            if name in value_ranges:
                self.value_ranges.append(
                    (value_ranges[name][0], value_ranges[name][1]))
            else:
                self.value_ranges.append((-np.inf, np.inf))


def correct_data(x, y, e, startx, endx, use_errors):
    """
    Strip data that overruns the start and end x_range,
    and approximate errors if not given.

    :param x: x data
    :type x: np.array
    :param y: y data
    :type y: np.array
    :param e: error data
    :type e: np.array
    :param startx: minimum x value
    :type startx: float
    :param endx: maximum x value
    :type endx: float
    :param use_errors: whether errors should be added if not present
    :type use_errors: bool
    """
    # fix data_e
    if use_errors:
        if e is None:
            e = np.sqrt(abs(y))

        # The values of data_e are used to divide the residuals.
        # If these are (close to zero), then this blows up.
        # This is particularly a problem if trying to fit
        # counts, which may follow a Poisson distribution.
        #
        # Fix this by cutting values less than a certain value
        trim_value = 1.0e-8
        e[e < trim_value] = trim_value
    else:
        e = None

    # impose x ranges
    # pylint: disable=no-member, assignment-from-no-return
    if startx is not None and endx is not None:
        mask = np.logical_and(x >= startx,
                              x <= endx)
        x = x[mask]
        y = y[mask]
        if e is not None:
            e = e[mask]

    # Stores the indices of the sorted data
    sorted_index = np.argsort(x)

    return x, y, e, sorted_index
