"""
Implementation of quaternions for kinematics
"""
import math

from matrix import Matrix33, Matrix44
from vector import Vector3, Vector4

eps = 1e-7


class Quaternion:
    """
    The quaternion class
    """

    def __init__(self, w=0.0, x=0.0, y=0.0, z=0.0):
        self._data = Vector4([x, y, z, w])

    def __array__(self, _dtype=None):
        # pylint:disable=unused-argument
        return self._data[:]

    @classmethod
    def identity(cls):
        """
        The identity for a quaternion
        """
        return Quaternion(1.0, 0.0, 0.0, 0.0)

    @property
    def x(self):
        """
        Get the x value for the number
        """
        return self._data.x

    @x.setter
    def x(self, value):
        self._data.x = value

    @property
    def y(self):
        """
        Get the y value for the number
        """
        return self._data.y

    @y.setter
    def y(self, value):
        self._data.y = value

    @property
    def z(self):
        """
        Get the z value for the number
        """
        return self._data.z

    @z.setter
    def z(self, value):
        self._data.z = value

    @property
    def w(self):
        """
        Get the w value for the number
        """
        return self._data.w

    @w.setter
    def w(self, value):
        self._data.w = value

    @property
    def axis(self):
        """
        Get the axis for the number
        """
        return Vector3([self.x, self.y, self.z])

    @axis.setter
    def axis(self, axis):
        self._data.xyz = axis

    def conjugate(self):
        """
        Get the conjugate for the number
        """
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    @property
    def length(self):
        """
        Get the length of the number
        """
        return self._data.length

    def toMatrix(self):
        """
        Convert the quaternion into a rotation matrix
        """
        twoxx = 2 * self.x * self.x
        twoyy = 2 * self.y * self.y
        twozz = 2 * self.z * self.z

        twowx = 2 * self.w * self.x
        twowy = 2 * self.w * self.y
        twowz = 2 * self.w * self.z

        twoxy = 2 * self.x * self.y
        twoxz = 2 * self.x * self.z

        twoyz = 2 * self.y * self.z

        return Matrix33([[1 - twoyy - twozz, twoxy - twowz, twoxz + twowy],
                         [twoxy + twowz, 1 - twoxx - twozz, twoyz - twowx],
                         [twoxz - twowy, twoyz + twowx, 1 - twoxx - twoyy]])

    def toAxisAngle(self):
        """
        Convert the quaternion into an axis and angle pair
        """
        angle = 2 * math.acos(self.w)
        s = math.sqrt(1 - self.w * self.w)
        if angle < eps:
            axis = Vector3()
        else:
            axis = Vector3([self.x, self.y, self.z]) / s

        return axis, angle

    def inverse(self):
        """
        Get the inverse of the quaternion
        """
        return self.conjugate().normalize()

    def normalize(self):
        """
        Find the quaternion with the same direction and a length of 1
        """
        length = self.length
        if length != 0:
            n = self._data.normalized
            return Quaternion(n.w, n.x, n.y, n.z)

        return Quaternion()

    def dot(self, q):
        """
        Calculate the dot product with another quaternion
        """
        return self._data.dot(q[:])

    def rotate(self, point):
        """
        Rotate the number by another quaternion
        """
        p = Quaternion(x=point[0], y=point[1], z=point[2])
        q_inv = self.inverse()

        rotated = self * p * q_inv

        return rotated.axis

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    @classmethod
    def fromAxisAngle(cls, axis, angle):
        """
        Create a quaternion from an axis and angle
        """
        # angle is in radians
        # axis should be a vector3

        w = math.cos(angle / 2)
        x, y, z = axis.normalized * math.sin(angle / 2)

        return Quaternion(w, x, y, z)

    @classmethod
    def fromMatrix(cls, matrix):
        """
        Create a quaternion from a 3d matrix
        """
        if matrix.m33 < eps:
            if matrix.m11 > matrix.m22:
                t = 1 + matrix.m11 - matrix.m22 - matrix.m33
                q = [
                    matrix.m32 - matrix.m23,
                    t,
                    matrix.m12 + matrix.m21,
                    matrix.m13 + matrix.m31,
                ]
            else:
                t = 1 - matrix.m11 + matrix.m22 - matrix.m33
                q = [
                    matrix.m13 - matrix.m31,
                    matrix.m12 + matrix.m21,
                    t,
                    matrix.m23 + matrix.m32,
                ]
        else:
            if matrix.m11 < -matrix.m22:
                t = 1 - matrix.m11 - matrix.m22 + matrix.m33
                q = [
                    matrix.m21 - matrix.m12,
                    matrix.m13 + matrix.m31,
                    matrix.m23 + matrix.m32,
                    t,
                ]
            else:
                t = 1 + matrix.m11 + matrix.m22 + matrix.m33
                q = [
                    t,
                    matrix.m32 - matrix.m23,
                    matrix.m13 - matrix.m31,
                    matrix.m21 - matrix.m12,
                ]

        q = Vector4(q) * 0.5 / math.sqrt(t)
        return Quaternion(*q)

    def __str__(self):
        return f"[{self.w} <{self.x} {self.y} {self.z}>]"

    def __mul__(self, other):
        w1 = self.w
        w2 = other.w

        v1 = self.axis
        v2 = other.axis

        w = w1 * w2 - (v1 | v2)
        v = w1 * v2 + w2 * v1 + (v1 ^ v2)

        return Quaternion(w, *v)

    def __or__(self, other):
        return self.dot(other)


class QuaternionVectorPair:
    """
    A quaternion vector pair
    """

    def __init__(self, q, v):
        self.quaternion = q
        self.vector = v

    def __mul__(self, other):
        if not isinstance(other, QuaternionVectorPair):
            raise ValueError(
                f'cannot multiply {type(other)} with QuaternionVectorPair')

        q = self.quaternion * other.quaternion
        v = self.quaternion.rotate(other.vector) + self.vector

        return QuaternionVectorPair(q, v)

    def __imul__(self, other):
        temp = self.__mul__(other)
        self.quaternion = temp.quaternion
        self.vector = temp.vector
        return self

    def inverse(self):
        """
        Inverse of the quaternion vector pair
        """
        q = self.quaternion.inverse()
        v = -q.rotate(self.vector)

        return QuaternionVectorPair(q, v)

    def toMatrix(self):
        """
        Create a 4x4 matrix from the quaternion vector pair
        """
        m = Matrix44.identity()
        m[0:3, 0:3] = self.quaternion.toMatrix()
        m[0:3, 3] = self.vector

        return m

    @classmethod
    def fromMatrix(cls, matrix):
        """
        Create the quaternion vector pair from a 4x4 matrix
        """
        q = Quaternion.fromMatrix(matrix)
        v = Vector3(matrix[0:3, 3])

        return cls(q, v)

    @classmethod
    def identity(cls):
        """
        The identity for a quaternion vector pair
        """
        q = Quaternion.identity()
        v = Vector3()

        return cls(q, v)

    def __str__(self):
        return f'Quaternion: {self.quaternion}, Vector: {self.vector}'
