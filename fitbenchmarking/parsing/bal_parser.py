"""
This file implements a parser for the Bundle Adjustment problem in the Large (BAL) dataset.
"""
import os
import typing
import numpy as np
import bz2

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser

class BALParser(FitbenchmarkParser):
    """
    Parser for a Bundle Adjustment problem definition file.
    """

    def read_bal_data(self, file_name):
        with bz2.open(file_name, "rt") as file:
            n_cameras, n_points, n_observations = map(
                int, file.readline().split())

            camera_indices = np.empty(n_observations, dtype=int)
            point_indices = np.empty(n_observations, dtype=int)
            
            for i in range(n_observations):
                camera_index, point_index, x, y = file.readline().split()
                camera_indices[i] = int(camera_index)
                point_indices[i] = int(point_index)

            camera_params = np.empty(n_cameras * 9)
            for i in range(n_cameras * 9):
                camera_params[i] = float(file.readline())
            camera_params = camera_params.reshape((n_cameras, -1))

            points_3d = np.empty(n_points * 3)
            for i in range(n_points * 3):
                points_3d[i] = float(file.readline())
            points_3d = points_3d.reshape((n_points, -1))

        return camera_params, points_3d, camera_indices, point_indices
    
    def rotate(points, rot_vecs):
        """Rotate points by given rotation vectors.
        
        Rodrigues' rotation formula is used.
        """
        theta = np.linalg.norm(rot_vecs, axis=1)[:, np.newaxis]
        with np.errstate(invalid='ignore'):
            v = rot_vecs / theta
            v = np.nan_to_num(v)
        dot = np.sum(points * v, axis=1)[:, np.newaxis]
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        return cos_theta * points + sin_theta * np.cross(v, points) + dot * (1 - cos_theta) * v
    
    def project(self, points, camera_params):
        """Convert 3-D points to 2-D by projecting onto images."""
        points_proj = self.rotate(points, camera_params[:, :3])
        points_proj += camera_params[:, 3:6]
        points_proj = -points_proj[:, :2] / points_proj[:, 2, np.newaxis]
        f = camera_params[:, 6]
        k1 = camera_params[:, 7]
        k2 = camera_params[:, 8]
        n = np.sum(points_proj**2, axis=1)
        r = 1 + k1 * n + k2 * n**2
        points_proj *= (r * f)[:, np.newaxis]
        return points_proj
    
    def fun(self, params, n_cameras, n_points, camera_indices, point_indices):
        """Compute projected points
        
        `params` contains camera parameters and 3-D coordinates.
        """
        print(type(params))
        print(params)
        camera_params = params[:n_cameras * 9].reshape((n_cameras, 9))
        points_3d = params[n_cameras * 9:].reshape((n_points, 3))
        points_proj = self.project(points_3d[point_indices], camera_params[camera_indices])
        return points_proj

    def _create_function(self) -> typing.Callable:
        """

        :return: A callable function
        :rtype: callable
        """
        data_file = self._get_data_file()[0]
        camera_params, points_3d, camera_indices, point_indices = self.read_bal_data(data_file)
        # pylint: disable=attribute-defined-outside-init
        self._equation = None

        n_cameras = camera_params.shape[0]
        n_points = points_3d.shape[0]

        # pylint: disable=attribute-defined-outside-init
        self._starting_values = [dict(enumerate(np.hstack((camera_params.ravel(), points_3d.ravel())).tolist()))]

        def fitFunction(x, *params):
            y = self.fun(params, n_cameras, n_points, camera_indices, point_indices)
            return y

        return fitFunction
    
    def _get_data_points(self, file_name):
        """
        Get the data points of the problem from the data file.

        :param data_file_path: The path to the file to load the points from
        :type data_file_path: str

        :return: data
        :rtype: dict<str, np.ndarray>
        """
        with bz2.open(file_name, "rt") as file:
            _, _, n_observations = map(int, file.readline().split())
            points_2d = np.empty((n_observations, 2))

            for i in range(n_observations):
                _, _, x, y = file.readline().split()
                points_2d[i] = [float(x), float(y)]

            print(points_2d.shape)
        
        return {'x': points_2d[:,0], 'y': points_2d[:,1]}

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
    
    def _parse_function(self, func=None):
        return func