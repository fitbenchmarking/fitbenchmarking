"""
This file implements a parser for the Fitbenchmark data format.
"""

from __future__ import absolute_import, division, print_function

import importlib
import inspect
import os
import sys
from collections import OrderedDict

import numpy as np
from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.exceptions import MissingSoftwareError, NoJacobianError, ParsingError
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()

import_success = {}
try:
    from scipy.integrate import solve_ivp
    import_success['ivp'] = (True, None)
except ImportError as ex:
    import_success['ivp'] = (False, ex)


try:
    import mantid.simpleapi as msapi
    import_success['mantid'] = (True, None)
except ImportError as ex:
    import_success['mantid'] = (False, ex)


try:
    from sasmodels.bumps_model import Experiment, Model
    from sasmodels.core import load_model
    from sasmodels.data import empty_data1D
    import_success['sasview'] = (True, None)
except ImportError as ex:
    import_success['sasview'] = (False, ex)


# By design the parsers may require many the private methods
# pylint: disable=too-many-branches
class FitbenchmarkParser(Parser):
    """
    Parser for the native FitBenchmarking problem definition (FitBenchmark)
    file.
    """

    def __init__(self, filename, options):
        super().__init__(filename, options)

        self._entries = None
        self._parsed_func = None

    def parse(self):
        """
        Parse the Fitbenchmark problem file into a Fitting Problem.

        :return: The fully parsed fitting problem
        :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
        """
        # pylint: disable=attribute-defined-outside-init
        fitting_problem = FittingProblem(self.options)

        self._entries = self._get_data_problem_entries()
        software = self._entries['software'].lower()
        if software not in import_success:
            raise MissingSoftwareError(
                f'Did not recognise software: {software}'
            )
        if not import_success[software][0]:
            error = import_success[software][1]
            raise MissingSoftwareError(
                f'Requirements are missing for {software} parser: {error}'
            )

        self._parsed_func = self._parse_function()

        if software == 'mantid' and self._entries['input_file'][0] == '[':
            fitting_problem.multifit = True

        # NAME
        fitting_problem.name = self._entries['name']

        # DATA
        data_points = [_get_data_points(p) for p in self._get_data_file()]

        # FUNCTION
        if software == 'mantid':
            fitting_problem.function = self._create_mantid_function()
            fitting_problem.format = 'mantid'
        elif software == 'sasview':
            fitting_problem.function = self._create_sasview_function()
            fitting_problem.format = 'sasview'
        elif software == 'ivp':
            fitting_problem.function = self._create_ivp_function()
            fitting_problem.format = 'ivp'

        # JACOBIAN
        if software == 'ivp':
            try:
                fitting_problem.jacobian = self._parse_ivp_jacobian()
            except NoJacobianError:
                LOGGER.warning("Could not find analytic Jacobian "
                                "information for %s problem", fitting_problem.name)

        # If using a multivariate function wrap the call to take a single
        # argument
        if len(data_points[0]['x'].shape) > 1:
            old_function = fitting_problem.function
            all_data = []
            count = 0
            for dp in data_points:
                all_data.append(dp['x'])
                dp['x'] = np.arange(count, count + dp['x'].shape[0])
                count = count + dp['x'].shape[0]
            all_data = np.concatenate(all_data)

            def new_function(x, *p):
                inp = all_data[x]
                return old_function(inp, *p)

            if fitting_problem.jacobian:
                old_jacobian = fitting_problem.jacobian
                def new_jacobian(x, p):
                    inp = all_data[x]
                    return old_jacobian(inp, p)
                fitting_problem.jacobian = new_jacobian

            fitting_problem.function = new_function
            fitting_problem.multivariate = True

        # Set this flag if the output is non-scalar either
        if len(data_points[0]['y'].shape) > 2:
            fitting_problem.multivariate = True

        # EQUATION
        if software == 'ivp':
            fitting_problem.equation = self._ivp_equation_name
        else:
            equation_count = len(self._parsed_func)
            if equation_count == 1:
                fitting_problem.equation = self._parsed_func[0]['name']
            else:
                fitting_problem.equation = '{} Functions'.format(
                    equation_count)

        # STARTING VALUES
        if software == 'ivp':
            fitting_problem.starting_values = self._ivp_starting_values
        elif software == 'mantid':
            fitting_problem.starting_values = self._mantid_starting_values
        else:
            fitting_problem.starting_values = self._get_starting_values()

        # PARAMETER RANGES
        # Creates list containing tuples of lower and upper bounds
        # (lb,ub) for each parameter
        vr = _parse_range(self._entries.get('parameter_ranges', ''))
        if vr:
            fitting_problem.set_value_ranges(vr)

        # FIT RANGES
        fit_ranges_str = self._entries.get('fit_ranges', '')
        # this creates a list of strs like '{key: val, ...}' and parses each
        fit_ranges = [_parse_range('{' + r.split('}')[0] + '}')
                      for r in fit_ranges_str.split('{')[1:]]

        if fitting_problem.multifit:
            num_files = len(data_points)
            fitting_problem.data_x = [d['x'] for d in data_points]
            fitting_problem.data_y = [d['y'] for d in data_points]
            fitting_problem.data_e = [d['e'] if 'e' in d else None
                                      for d in data_points]

            if not fit_ranges:
                fit_ranges = [{} for _ in range(num_files)]

            fitting_problem.start_x = [f['x'][0] if 'x' in f else None
                                       for f in fit_ranges]
            fitting_problem.end_x = [f['x'][1] if 'x' in f else None
                                     for f in fit_ranges]

        else:
            fitting_problem.data_x = data_points[0]['x']
            fitting_problem.data_y = data_points[0]['y']
            if 'e' in data_points[0]:
                fitting_problem.data_e = data_points[0]['e']

            if fit_ranges and 'x' in fit_ranges[0]:
                fitting_problem.start_x = fit_ranges[0]['x'][0]
                fitting_problem.end_x = fit_ranges[0]['x'][1]

        if software == 'mantid':
            # String containing the function name(s) and the starting parameter
            # values for each function.
            fitting_problem.additional_info['mantid_equation'] \
                = self._entries['function']

            if fitting_problem.multifit:
                fitting_problem.additional_info['mantid_ties'] \
                    = self._parse_ties()

        return fitting_problem

    def _get_data_file(self):
        """
        Find/create the (full) path to a data_file(s) specified in a
        FitBenchmark definition file, where the data_file is searched for in
        the directory of the definition file and subfolders of this file.

        :return: (full) path to a data file. Return None if not found
        :rtype: list<str>
        """
        data_file_name = self._entries['input_file']
        if data_file_name.startswith('['):
            # Parse list assuming filenames do not have quote symbols or commas
            data_file_names = [
                d.replace('"', '').replace("'", '').strip('[').strip(']')
                for d in data_file_name.split(',')]
        else:
            data_file_names = [data_file_name]

        # find or search for path for data_file_name
        data_files = []
        for data_file_name in data_file_names:
            data_file = None
            for root, _, files in os.walk(os.path.dirname(self._filename)):
                for name in files:
                    if data_file_name == name:
                        data_file = os.path.join(root, data_file_name)

            if data_file is None:
                LOGGER.error("Data file %s not found", data_file_name)

            data_files.append(data_file)

        return data_files

    def _get_data_problem_entries(self):
        """
        Get the problem entries from a problem definition file.

        :return: The entries from the file with string values
        :rtype: dict
        """

        entries = {}
        for line in self.file.readlines():
            # Discard comments
            line = line.split('#', 1)[0]
            if line.strip() == '':
                continue

            lhs, rhs = line.split("=", 1)
            entries[lhs.strip()] = rhs.strip().strip('"').strip("'")

        return entries

    def _parse_function(self):
        """
        Get the params from the function as a list of dicts from the data
        file.

        :return: Function definition in format:
                 [{name1: value1, name2: value2, ...}, ...]
        :rtype: list of dict
        """
        # pylint: disable=too-many-branches, too-many-statements
        function_def = []

        for f in self._entries['function'].split(';'):
            params_dict = OrderedDict()
            pop_stack = 0

            stack = [params_dict]
            for p in f.split(','):
                name, val = p.split('=', 1)
                name = name.strip()
                val = val.strip()

                l_count = val.count('(')
                r_count = val.count(')')
                if l_count > r_count:
                    # in brackets
                    # should be of the form 'varname=(othervar=3, ...)'

                    # Allow for nested brackets e.g. 'a=(b=(c=(d=1,e=2)))'
                    for _ in range(l_count - r_count):
                        # Cover case where formula mistyped
                        if '=' not in val:
                            raise ParsingError('Unbalanced brackets in '
                                               'function value: {}'.format(p))
                        # Must start with brackets
                        if val[0] != '(':
                            raise ParsingError('Bad placement of opening '
                                               'bracket in function: '
                                               '{}'.format(p))
                        # Create new dict for this entry and put at top of
                        # working stack
                        new_dict = OrderedDict()
                        stack[-1][name] = new_dict
                        stack.append(new_dict)
                        # Update name and val
                        name, val = val[1:].split('=', 1)
                elif l_count == r_count:
                    # Check if single item in brackets
                    while '=' in val:
                        if val[0] == '(' and val[-1] == ')':
                            val = val[1:-1]
                            new_dict = OrderedDict()
                            stack[-1][name] = new_dict
                            stack.append(new_dict)
                            name, val = val.split('=', 1)
                            pop_stack += 1
                        else:
                            raise ParsingError('Function value contains '
                                               'unexpected "=": {}'.format(p))
                elif l_count < r_count:
                    # exiting brackets
                    pop_stack = r_count - l_count
                    # must end with brackets
                    if val[-pop_stack:] != ')' * pop_stack:
                        raise ParsingError('Bad placement of closing bracket '
                                           'in function: {}'.format(p))
                    val = val[:-pop_stack]

                # Parse to an int/float if possible else assume string
                tmp_val = None
                for t in [int, float]:
                    if tmp_val is None:
                        try:
                            tmp_val = t(val)
                        except (ValueError, TypeError):
                            pass

                if tmp_val is not None:
                    val = tmp_val

                stack[-1][name] = val

                if pop_stack > 0:
                    if len(stack) <= pop_stack:
                        raise ParsingError('Too many closing brackets in '
                                           'function: {}'.format(p))
                    stack = stack[:-pop_stack]
                    pop_stack = 0

            if len(stack) != 1:
                raise ParsingError('Not all brackets are closed in function.')
            function_def.append(params_dict)

        return function_def

    def _get_starting_values(self):
        """
        Get the starting values for the problem

        :return: Starting values for the function
        :rtype: list of OrderedDict
        """
        # SasView functions can have reserved keywords so ignore these
        ignore = ['name']

        starting_values = [
            OrderedDict([(name, val)
                         for name, val in self._parsed_func[0].items()
                         if name not in ignore])]

        return starting_values

    def _create_mantid_function(self):
        """
        Processing the function in the FitBenchmark problem definition into a
        python callable.

        :return: A callable function
        :rtype: callable
        """
        # Get mantid to build the function
        ifun = msapi.FunctionFactory.createInitialized(
            self._entries['function'])

        # Extract the parameter info
        all_params = [(ifun.getParamName(i),
                       ifun.getParamValue(i),
                       ifun.isFixed(i))
                      for i in range(ifun.nParams())]

        # This list will be used to input fixed values alongside unfixed ones
        all_params_dict = {name: value
                           for name, value, _ in all_params}

        # Extract starting parameters
        params = {name: value
                  for name, value, fixed in all_params
                  if not fixed}
        # pylint: disable=attribute-defined-outside-init
        self._mantid_starting_values = [OrderedDict(params)]

        # Convert to callable
        fit_function = msapi.FunctionWrapper(ifun)

        # Use a wrapper to inject fixed parameters into the function
        def wrapped(x, *p):
            # Use the full param dict from above, but update the non-fixed
            # values
            update_dict = dict(zip(params.keys(), p))
            all_params_dict.update(update_dict)

            return fit_function(x, *all_params_dict.values())

        return wrapped

    def _create_sasview_function(self):
        """
        Creates callable function

        :return: the model
        :rtype: callable
        """
        equation = self._parsed_func[0]['name']
        starting_values = self._get_starting_values()
        param_names = list(starting_values[0].keys())

        def fitFunction(x, *tmp_params):

            model = load_model(equation)

            data = empty_data1D(x)
            param_dict = dict(zip(param_names, tmp_params))

            model_wrapper = Model(model, **param_dict)
            func_wrapper = Experiment(data=data, model=model_wrapper)

            return func_wrapper.theory()

        return fitFunction

    def _create_ivp_function(self):
        """
        Process the IVP formatted function into a callable.

        Expected function format:
        function='module=my_python_file,func=my_function_name,
                  step=0.5,p0=0.1,p1...'

        :return: the model
        :rtype: callable
        """
        if len(self._parsed_func) > 1:
            raise ParsingError('Could not parse IVP problem. Please ensure '
                               'only 1 function definition is present')

        pf = self._parsed_func[0]
        path = os.path.join(os.path.dirname(self._filename), pf['module'])
        sys.path.append(os.path.dirname(path))
        module = importlib.import_module(os.path.basename(path))
        fun = getattr(module, pf['func'])
        time_step = pf['step']
        sig = inspect.signature(fun)
        # params[0] should be t
        # parmas[1] should be x so start after.
        p_names = list(sig.parameters.keys())[2:]

        # pylint: disable=attribute-defined-outside-init
        self._ivp_equation_name = fun.__name__
        self._ivp_starting_values = [
            OrderedDict([(n, pf[n])
                         for n in p_names])
        ]

        def fitFunction(x, *p):
            if len(x.shape) == 1:
                x = np.array([x])
            y = np.zeros_like(x)
            for i, inp in enumerate(x):
                soln = solve_ivp(fun=fun,
                                 t_span=[0, time_step],
                                 y0=inp,
                                 args=p,
                                 vectorized=False)
                y[i, :] = soln.y[:, -1]
            return y

        return fitFunction

    def _parse_ties(self):
        try:
            ties = []
            for t in self._entries['ties'].split(','):
                # Strip out these chars
                for s in '[] "\'':
                    t = t.replace(s, '')
                ties.append(t)

        except KeyError:
            ties = []
        return ties

    def _parse_ivp_jacobian(self):

        jacobian_info = {}
        try:
            for j in self._entries['jacobian'].split(','):
                name, val = j.split('=',1)
                jacobian_info[name] = val
        except:
            raise NoJacobianError
        
        path = os.path.join(os.path.dirname(self._filename), jacobian_info['module'])
        sys.path.append(os.path.dirname(path))
        module = importlib.import_module(os.path.basename(path))

        jac_fun = jacobian_info['jac']
        jac_dict = dict(j.split(":") for j in jac_fun.split(";"))
        time_step = jacobian_info['step']

        def fitFunction_jac(x, *p):
            p = tuple(p[0])
            if len(x.shape) == 1:
                x = np.array([x])
            jac = np.zeros((np.shape(x)[0],np.shape(x)[1],len(p)))
            for i, inp in enumerate(x):
                j = 0
                for k,v in jac_dict.items():
                    fun = getattr(module, v)
                    soln = solve_ivp(fun=fun,
                                     t_span=[0, time_step],
                                     y0=inp,
                                     args=p,
                                     vectorized=False)
                    jac[i,:,j] = soln.y[:, -1]
                    j += 1
            new_jac = np.reshape(jac,(np.shape(x)[0]*np.shape(x)[1],len(p)))
            return new_jac

        return fitFunction_jac


def _parse_range(range_str):
    """
    Parse a range string for the problem into a dict or list of dict if
    multi-fit.

    :param range_str: The a string to parse
    :type range_str: string

    :return: The ranges in a dictionary with key as the var and value as a
             list with min and max
             e.g. {'x': [0, 10]}
    :rtype: dict
    """
    if not range_str:
        return {}

    output_ranges = {}
    range_str = range_str.strip('{').strip('}')
    tmp_ranges = range_str.split(',')
    ranges = []
    cur_str = ''
    for r in tmp_ranges:
        cur_str += r
        balanced = True
        for lb, rb in ['[]', '{}', '()']:
            if cur_str.count(lb) > cur_str.count(rb):
                balanced = False
            elif cur_str.count(lb) < cur_str.count(rb):
                raise ParsingError(
                    'Unbalanced brackets in range: {}'.format(r))
        if balanced:
            ranges.append(cur_str)
            cur_str = ''
        else:
            cur_str += ','

    for r in ranges:
        name, val = r.split(':')
        name = name.strip().strip('"').strip("'").lower()

        # Strip off brackets and split on comma
        val = val.strip(' ')[1:-1].split(',')
        val = [v.strip() for v in val]
        try:
            pair = [float(val[0]), float(val[1])]
        except ValueError as e:
            raise ParsingError('Expected floats in range: {}'.format(r)) from e

        if pair[0] >= pair[1]:
            raise ParsingError('Min value must be smaller than max value '
                               'in range: {}'.format(r))

        output_ranges[name] = pair

    return output_ranges


def _get_data_points(data_file_path):
    """
    Get the data points of the problem from the data file.

    :param data_file_path: The path to the file to load the points from
    :type data_file_path: str

    :return: data
    :rtype: dict<str, np.ndarray>
    """

    with open(data_file_path, 'r') as f:
        data_text = f.readlines()

    # Find the line where data starts
    # i.e. the first line with a float on it
    first_row = 0
    for i, line in enumerate(data_text):
        line = line.strip()
        if not line:
            continue
        try:
            float(line.split()[0])
        except ValueError:
            continue
        first_row = i
        break
    else:
        raise ParsingError('Could not find data points')

    dim = len(data_text[first_row].split())
    cols = {'x': [],
            'y': [],
            'e': []}
    num_cols = 0
    if first_row != 0:
        header = data_text[0].split()
        for heading in header:
            if heading == '#':
                continue
            if heading[0] == '<' and heading[-1] == '>':
                heading = heading[1:-1]
            col_type = heading[0].lower()
            if col_type in ['x', 'y', 'e']:
                cols[col_type].append(num_cols)
                num_cols += 1
            else:
                raise ParsingError(
                    'Unrecognised header line, header names must start with '
                    '"x", "y", or "e".'
                    'Examples are: '
                    '"# X Y E", "#   x0 x1 y e", "# X0 X1 Y0 Y1 E0 E1", '
                    '"<X> <Y> <E>", "<X0> <X1> <Y> <E>"...')
        if dim != num_cols:
            raise ParsingError('Could not match header to columns.')
    else:
        cols['x'] = [0]
        cols['y'] = [1]
        if dim == 3:
            cols['e'] = [2]
        elif dim != 2:
            raise ParsingError(
                'Cannot infer size of inputs and outputs in datafile. '
                'Headers are required when not using 1D inputs and outputs.')

    if not cols['x'] or not cols['y']:
        raise ParsingError('Input files need both X and Y values.')
    if cols['e'] and len(cols['y']) != len(cols['e']):
        raise ParsingError('Error must be of the same dimension as Y.')

    data_points = np.zeros((len(data_text) - first_row, dim))

    for idx, line in enumerate(data_text[first_row:]):
        point_text = line.split()
        # Skip any values that can't be represented
        try:
            point = [float(val) for val in point_text]
        except ValueError:
            point = [np.nan for _ in point_text]
        data_points[idx, :] = point

    # Strip all np.nan entries
    data_points = data_points[~np.isnan(data_points[:, 0]), :]

    # Split into x, y, and e
    data = {key: data_points[:, cols[key]]
            for key in ['x', 'y']}
    if cols['e']:
        data['e'] = data_points[:, cols['e']]

    # Flatten if the columns are 1D
    for key, col in cols.items():
        if len(col) == 1:
            data[key] = data[key].flatten()

    return data
