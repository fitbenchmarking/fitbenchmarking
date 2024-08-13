"""
This file implements a parser for SScanSS problem sets.
"""
import math
import os
import sys
import typing
from importlib import import_module

import numpy as np

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser
from fitbenchmarking.parsing.fitting_problem import FittingProblem


class SScanSSParser(FitbenchmarkParser):
    """
    Parser for a SScanSS problem definition file.

    Function calculates the error from a current pose to the target pose.
    """
    _PARAM_IGNORE_LIST = ['robot', 'module', 'targets']

    def parse(self) -> 'list[FittingProblem]':
        template = super().parse()

        out = []

        pf = self._parsed_func[0]
        path = os.path.join(os.path.dirname(self._filename), pf['module'])
        sys.path.append(os.path.dirname(path))
        module = import_module(os.path.basename(path))
        robot = getattr(module, pf['robot'])
        targets = getattr(module, pf['targets'])

        for i, t in enumerate(targets):
            fp = FittingProblem(self.options)
            fp.multifit = template.multifit
            fp.name = f'{template.name} - target {i+1}'
            fp.description = (f'{template.description.rstrip().rstrip(".")}. '
                              f'This problem is associated with target {i+1}.')
            fp.function = self.inverse_kinematics_error(robot, t)
            fp.format = template.format
            fp.plot_scale = template.plot_scale
            fp.multivariate = template.multivariate
            fp.equation = template.equation
            fp.starting_values = template.starting_values
            fp.value_ranges = template.value_ranges
            fp.data_x = template.data_x
            fp.data_y = template.data_y
            fp.data_e = template.data_e
            fp.start_x = template.start_x
            fp.end_x = template.end_x
            out.append(fp)

        return out

    def _create_function(self) -> typing.Callable:
        """
        Required for base class.
        Since this is only called to build the template, we return a dummy
        function.

        Expected function format:
        function='module=robots,robot=model1,target=target1,p1=...,p2=...,etc'

        :return: A callable function
        :rtype: callable
        """
        # pylint: disable=unused-argument
        def dummy(x, *params):
            pass

        return dummy

    @staticmethod
    def inverse_kinematics_error(robot, target):
        """
        Create a function for calculation the error in a forward kinematics
        transform.
        """
        def error_func(x, *params):
            # pylint: disable=unused-argument
            cur_pose = robot.fkine(params)
            pos_diff = cur_pose[:3, 3] - target[:3, 3]
            angle_diff = SScanSSParser.emap(
                target[:3, :3] @ cur_pose[:3, :3].transpose())
            return np.array(list(pos_diff) + list(angle_diff))

        return error_func

    @staticmethod
    def emap(r):
        """
        Convert a rotation matrix to an exponential map

        :param r: the rotation matrix to convert
        :type r: 3x3 matrix
        """
        b = r - np.identity(3)
        _, _, v = np.linalg.svd(b)
        axis = v[-1, :]

        twocostheta = np.trace(r) - 1
        twosinthetav = [r[2, 1] - r[1, 2],
                        r[0, 2] - r[2, 0], r[1, 0] - r[0, 1]]
        twosintheta = np.dot(axis, twosinthetav)
        angle = math.degrees(math.atan2(twosintheta, twocostheta))
        return angle * axis

    def _get_equation(self) -> str:
        """
        Returns the equation in the problem definition file.

        :return: The equation in the problem definition file.
        :rtype: str
        """
        pf = self._parsed_func[0]
        return pf["robot"]

    def _get_data_file(self):
        return ["no_file_required"]

    def _get_data_points(self, _filename):
        # pylint: disable=unused-argument
        # x data is the spatial and agular coordinates for the pose
        # y data is the error in each coord at the fit (as defined in
        #     inverse_kinematics_error)
        return {'x': np.array(["x", "y", "z", "ex", "ey", "ez"]),
                'y': np.array([0, 0, 0, 0, 0, 0])}
