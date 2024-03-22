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


class SScanSSParser(FitbenchmarkParser):
    """
    Parser for a SScanSS problem definition file.

    Function calculates the error from a current pose to the target pose.
    """
    PARAM_IGNORE_LIST = ['robot', 'module', 'target']

    def _create_function(self) -> typing.Callable:
        """
        Process the forward kinematicsfor the given robot into a callable.

        Expected function format:
        function='module=robots,robot=model1,target=target1,p1=...,p2=...,etc'

        :return: A callable function
        :rtype: callable
        """

        pf = self._parsed_func[0]
        path = os.path.join(os.path.dirname(self._filename), pf['module'])
        sys.path.append(os.path.dirname(path))
        module = import_module(os.path.basename(path))
        robot = getattr(module, pf['robot'])
        target = getattr(module, pf['target'])

        return self.inverse_kinematics_error(robot, target)

    @staticmethod
    def inverse_kinematics_error(robot, target):
        """
        Create a function for calculation the error in a forward kinematics
        transform.
        """
        def error_func(*params):
            cur_pose = robot.fkine(params)
            pos_diff = cur_pose[:3, 3] - target[:3, 3]
            angle_diff = SScanSSParser.emap(
                target[:3, :3] @ cur_pose[:3, :3].transpose())
            error = np.sum(pos_diff**2 + angle_diff**2)
            return np.array([error])

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
        return f'{pf["robot"]}_{pf["target"]}'

    def _get_data_file(self):
        return ["no_file_required"]

    @staticmethod
    def _get_data_points(_filename):
        # pylint: disable=unused-argument
        return {'x': np.array([1]),
                'y': np.array([0])}
