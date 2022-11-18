"""
This file implements a parser for SpinW data.
"""
import os
import typing
import sys

import matlab
import numpy as np

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser
from fitbenchmarking.utils.exceptions import ParsingError
from fitbenchmarking.utils.matlab_engine import ENG as eng
from fitbenchmarking.utils.matlab_engine import add_persistent_matlab_var

horace_location = os.environ["HORACE_LOCATION"]
sys.path.insert(0, horace_location)

eng.evalc(f"addpath('{horace_location}')")

eng.evalc('horace_on')
# Keep horace active - even after cleanup of horace controller..
add_persistent_matlab_var('horace')


class SpinWParser(FitbenchmarkParser):
    """
    Parser for a SpinW problem definition file.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A container for improving efficiency in function call if calling
        # with full input data
        self._spinw_x: typing.Optional[np.ndarray] = None

    def _get_data_points(self, data_file_path):
        """
        Get the data points of the problem from the data file.

        :param data_file_path: The path to the file to load the points from
        :type data_file_path: str

        :return: data
        :rtype: dict<str, np.ndarray>
        """
        proj = self._parse_proj()
        eng.workspace['sqw_cut'] = self._parse_cut(data_file_path, proj)
        # Add sample
        eng.workspace['sample'] = self._parse_sample()
        if 'angdeg'  in self._entries:
            eng.evalc(f'sample.angdeg= {self._entries["angdeg"]}')
        if 'alatt' in self._entries:
            eng.evalc(f'sample.alatt= {self._entries["alatt"]}')
        #print(self._parse_sample()[1])
        eng.evalc('w1 = sqw_cut.set_sample(sample);')
        # Add instrument
        eng.workspace['instrument'] = self._parse_instrument()
        eng.evalc('w1 = w1.set_instrument(instrument);')
        # Reduce size of problem if set
        if "random_fraction_pixels" in self._entries:
            eng.evalc('w1 = w1.mask_random_fraction_pixels('
                      f'{self._entries["random_fraction_pixels"]});')
        # Create tbf
        eng.evalc('tbf = tobyfit(w1);')
        # Set mc points if defined
        if "mc_points" in self._entries:
            eng.evalc(f'tbf = tbf.set_mc_points({self._entries["mc_points"]})')
        add_persistent_matlab_var('tbf')       
        bins = [np.array(v) for v in eng.eval('sqw_cut.data.p')]
        counts = np.array(eng.eval('sqw_cut.data.s'))
        x = np.array([[a/2, b/2, c/2]
                      for a in bins[0][0][1:]+bins[0][0][:-1]
                      for b in bins[1][0][1:]+bins[1][0][:-1]
                      for c in bins[2][0][1:]+bins[2][0][:-1]])
        y = counts.flatten()
        self._spinw_x = x

        return {'x': x, 'y': y}

    def _parse_proj(self):
        """
        Create a projection axes object for use with the SpinW cut.

        :raises ParsingError: If arguments are not properly defined.
        :return: The projection axes
        :rtype: eng.proj_axes
        """
        proj_sec = self._entries['projection']
        proj_args = self._parse_single_function(proj_sec)

        args = []
        for k in ['u', 'v', 'w']:
            if k not in proj_args:
                if k == 'w':
                    continue
                raise ParsingError('SpinW cuts must contain both u and v. '
                                   f'{k} is missing.')

            vector = proj_args[k]
            if len(vector) != 3:
                raise ParsingError(f'{k} must be a 1x3 vector, not '
                                   f'1x{len(vector)}')

            args.append(matlab.double(vector))

        kwargs = ['nonorthogonal', True]
        if 'type' in proj_args:
            if len(proj_args['type']) != 3 or \
                    any(c not in 'apr' for c in proj_args['type']):
                raise ParsingError('type must be a string of 3 characters '
                                   'chosen from a, p, and r')
            kwargs.extend(['type', proj_args['type']])
        if 'uoffset' in proj_args:
            vector = proj_args['uoffset']
            if len(vector) != 4:
                raise ParsingError('uoffset must be a 1x4 vector, not '
                                   f'1x{len(vector)}.')
            kwargs.extend(['uoffset', matlab.double(vector)])

        return eng.ortho_proj(*args + kwargs)

    def _parse_cut(self, data_file_path, proj):
        """
        Parse the cut entry and take a cut of the data.

        :param data_file_path: The path to the data file
        :type data_file_path: str
        :param proj: A projection to view the data from
        :type proj: matlab.projaxes
        :raises ParsingError: If unexpected characters are encountered
        :return: The sqw object which contains the data
        :rtype: matlab sqw object
        """
        cut_sec = self._entries['cut']
        cut_args = self._parse_single_function(cut_sec)

        if len(cut_args) != 4:
            raise ParsingError('cut must contain 4 vectors')

        args = []
        for i in range(1, 5):
            k = f'p{i}_bin'
            if k not in cut_args:
                raise ParsingError('cut must have parameters names p1_bin, '
                                   'p2_bin, ...')
            vec = cut_args[k]
            if not isinstance(vec, list):
                raise ParsingError('cut parameters must be vectors, not '
                                   f'{vec}')
            if len(vec) > 4:
                raise ParsingError(
                    'cut parameters should have 4 or fewer elements. Unable '
                    f'to parse {vec}')
            args.append(matlab.double(vec))

        return eng.cut_sqw(data_file_path, proj, *args)

    def _parse_sample(self):
        """
        Parse the sample section of the input file
        Currently only supports IX_sample. Others will be added as required.

        :raises ParsingError: If a non IX_sample is used or arguments are
                              missing
        :return: The sample matlab object
        :rtype: IX_sample
        """
        try:
            sample_sec = self._entries['sample']
            sample_args = self._parse_single_function(sample_sec)
            if sample_args['class'] != 'IX_sample':
                raise ParsingError('This parser only works for IX_sample')
            args = []
            if 'name' in sample_args:
                args.append(sample_args['name'])
            args.append(sample_args['single_crystal'])
            if 'xgeom' in sample_args:
                args.append(matlab.double(sample_args['xgeom']))
                args.append(matlab.double(sample_args['ygeom']))
                if 'shape' in sample_args:
                    args.append(sample_args['shape'])
                    args.append(matlab.double(sample_args['ps']))
            if 'eta' in sample_args:
                args.append(sample_args['eta'])
            if 'temperature' in sample_args:
                args.append(sample_args['temperature'])
        except KeyError as ex:
            raise ParsingError('Missing expected key') from ex
        return eng.IX_sample(*args)

    def _parse_instrument(self):
        """
        Parse the 'instrument' entry

        :raises ParsingError: If the class is unrecognised or arguments are
                              missing
        """
        try:
            instrument_sec = self._entries['instrument']
            instrument_args = self._parse_single_function(instrument_sec)

            args = []
            if instrument_args['class'] == 'maps_instrument':
                args.append(float(instrument_args['ei']))
                args.append(float(instrument_args['hz']))
                args.append(instrument_args['chopper'])
                if 'version' in instrument_args:
                    args.extend(['-version', instrument_args['version']])
                if 'moderator' in instrument_args:
                    args.extend(['-moderator', instrument_args['moderator']])
                return eng.maps_instrument(*args)
            elif instrument_args['class'] == 'melin_instrument':
                args.append(float(instrument_args['ei']))
                args.append(float(instrument_args['hz']))
                args.append(instrument_args['chopper'])
                return eng.merlin_instrument(*args)
            elif instrument_args['class'] == 'let_instrument':
                args.append(float(instrument_args['ei']))
                args.append(instrument_args['hz5'])
                args.append(instrument_args['hz3'])
                args.append(instrument_args['slot_mm'])
                args.append(instrument_args['mode'])
                if 'version' in instrument_args:
                    args.extend(['-version', instrument_args['version']])
                return eng.let_instrument(*args)
            else:
                raise ParsingError('This parser only works for '
                                   'maps, merlin, and let instruments')

        except KeyError as ex:
            raise ParsingError('Missing expected key') from ex

    def _create_function(self) -> typing.Callable:
        """
        Process the SpinW formatted function into a callable.

        Expected function format:
        function='matlab_script=filename,p0=...'

        :return: A callable function
        :rtype: callable
        """
        if len(self._parsed_func) > 1:
            raise ParsingError('Could not parse SpinW problem. Please ensure '
                               'only 1 function definition is present')

        pf = self._parsed_func[0]
        path = os.path.join(os.path.dirname(self._filename),
                            pf['matlab_script'])
        eng.addpath(os.path.dirname(path))
        func_name = os.path.basename(path).split('.', 1)[0]

        # pylint: disable=attribute-defined-outside-init
        self._equation = os.path.splitext(
            os.path.basename(pf['matlab_script']))[0]

        p_names = [k for k in pf if k != 'matlab_script']

        self._starting_values = [{n: pf[n] for n in p_names}]

        try:
            intrinsic_energy_width = float(self._entries['intrinsic_energy_width'])
        except KeyError as e:
            raise ParsingError('SpinW requires an "intrinsic_energy_width". '
                               'Please check the problem file') from e
        cpars = list(self._starting_values[0].values())
        cpars.append(intrinsic_energy_width)
        eng.workspace['cpars'] = matlab.double(cpars)
        cpars_kwargs = '{cpars'
        for key, value in self._entries.items():
            if key.startswith('spinwpars_'):
                try:
                    eng.evalc(f'{key}={value};')
                except:
                    eng.evalc(f"{key}='{value}';")
                add_persistent_matlab_var(key)
                cpars_kwargs += f", '{key[10:]}', {key}"
        cpars_kwargs  += ',"fid", 0}'
        eng.workspace['spinw_args'] = matlab.double([pf[n] for n in p_names])
        eng.evalc('spinw_args = num2cell(spinw_args);')
        eng.evalc(f'sw_obj = {func_name}(spinw_args{{:}})')
        eng.evalc(f'tbf = tbf.set_fun(@sw_obj.horace_sqw, {cpars_kwargs})')

        def fit_function(x, *p):
            # Assume, for efficiency, matching shape => matching values
            print(*p)
            if x.shape != self._spinw_x.shape:
                return np.ones(x.shape)
            eng.workspace['spinw_pin'] = matlab.double(
                list(p) + [intrinsic_energy_width])
            eng.evalc(f'tbf = tbf.set_pin({{spinw_pin, {cpars_kwargs[7:]});')
            eng.eval('wsim = tbf.simulate();', nargout=0)
            eng.evalc('spinw_y = wsim.data.s')
            return np.array(eng.workspace['spinw_y']).flatten()

        return fit_function

    def _get_equation(self) -> str:
        """
        Returns the equation in the problem definition file.

        :return: The equation in the problem definition file.
        :rtype: str
        """
        return self._equation

    def _get_starting_values(self) -> list:
        """
        Returns the starting values for the problem.

        :return: The starting values for the problem.
        :rtype: list
        """
        return self._starting_values
