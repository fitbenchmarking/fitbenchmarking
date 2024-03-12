"""
This file implements a parser for the Bundle Adjustment problem in the Large (BAL) dataset.
"""
import typing
import bz2
import numpy as np
from scipy.sparse import lil_matrix

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser

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

def project(points, camera_params):
    """Convert 3-D points to 2-D by projecting onto images."""
    points_proj = rotate(points, camera_params[:, :3])
    points_proj += camera_params[:, 3:6]
    points_proj = -points_proj[:, :2] / points_proj[:, 2, np.newaxis]
    f = camera_params[:, 6]
    k1 = camera_params[:, 7]
    k2 = camera_params[:, 8]
    n = np.sum(points_proj**2, axis=1)
    r = 1 + k1 * n + k2 * n**2
    points_proj *= (r * f)[:, np.newaxis]
    return points_proj
class BALParser(FitbenchmarkParser):
    """
    Parser for a Bundle Adjustment problem definition file.
    """

    def read_bal_data(self, file_name):
        """
        Read in datafile
        """
        with bz2.open(file_name, "rt") as file:
            self.n_cameras, self.n_points, n_observations = map(
                int, file.readline().split())

            self.camera_indices = np.empty(n_observations, dtype=int)
            self.point_indices = np.empty(n_observations, dtype=int)

            for i in range(n_observations):
                camera_index, point_index, x, y = file.readline().split()
                self.camera_indices[i] = int(camera_index)
                self.point_indices[i] = int(point_index)

            camera_params = np.empty(self.n_cameras * 9)
            for i in range(self.n_cameras * 9):
                camera_params[i] = float(file.readline())
            camera_params = camera_params.reshape((self.n_cameras, -1))

            points_3d = np.empty(self.n_points * 3)
            for i in range(self.n_points * 3):
                points_3d[i] = float(file.readline())
            points_3d = points_3d.reshape((self.n_points, -1))

        return camera_params, points_3d

    def fun(self, params):
        """Compute projected points

        `params` contains camera parameters and 3-D coordinates.
        """
        camera_params = np.array(params)[:self.n_cameras * 9].reshape((self.n_cameras, 9))
        points_3d = np.array(params)[self.n_cameras * 9:].reshape((self.n_points, 3))
        points_proj = project(points_3d[self.point_indices],
                                   camera_params[self.camera_indices])
        return points_proj

    def _create_function(self) -> typing.Callable:
        """

        :return: A callable function
        :rtype: callable
        """
        data_file = self._get_data_file()[0]
        camera_params, points_3d = self.read_bal_data(data_file)
        # pylint: disable=attribute-defined-outside-init
        self._equation = None

        # pylint: disable=attribute-defined-outside-init
        self._starting_values = [
            dict(enumerate(np.hstack((camera_params.ravel(),
                                      points_3d.ravel())).tolist()))
        ]

        def fitFunction(x, *params):
            y = self.fun(params)
            return y

        return fitFunction

    def _get_data_points(self, data_file_path):
        """
        Get the data points of the problem from the data file.

        :param data_file_path: The path to the file to load the points from
        :type data_file_path: str

        :return: data
        :rtype: dict<str, np.ndarray>
        """
        with bz2.open(data_file_path, "rt") as file:
            _, _, n_observations = map(int, file.readline().split())
            points_2d = np.empty((n_observations, 2))

            for i in range(n_observations):
                _, _, x, y = file.readline().split()
                points_2d[i] = [float(x), float(y)]

        return {'x': np.zeros((n_observations,2)),
                'y': points_2d,
                'e': np.ones((n_observations,2))}

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

    def bundle_adjustment_sparsity(self):
        """
        Jacobian sparsity structure for BAL problems
        """
        m = self.camera_indices.size * 2
        n = self.n_cameras * 9 + self.n_points * 3
        A = lil_matrix((m, n), dtype=int)

        i = np.arange(self.camera_indices.size)
        for s in range(9):
            A[2 * i, self.camera_indices * 9 + s] = 1
            A[2 * i + 1, self.camera_indices * 9 + s] = 1

        for s in range(3):
            A[2 * i, self.n_cameras * 9 + self.point_indices * 3 + s] = 1
            A[2 * i + 1, self.n_cameras * 9 + self.point_indices * 3 + s] = 1

        return A

    def _sparse_jacobian(self) -> typing.Callable:
        """
        Process the sparse jac function into a callable. Returns
        None if this is not possible.

        :return: A callable function
        :rtype: callable
        """
        def sparse_jac(x, *params):
            A = self.bundle_adjustment_sparsity()
            return A

        return sparse_jac
