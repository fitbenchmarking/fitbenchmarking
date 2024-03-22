"""
Matrix for kinematics code.
"""
import numpy as np
from vector import Vector


class Matrix:
    """
    Base matrix implementation
    """
    __array_priority__ = 1

    def __init__(self, rows, cols, values=None, dtype=None):
        if rows < 1 or cols < 1:
            raise ValueError("cols and rows must not be less than 1")
        super().__setattr__("rows", rows)
        super().__setattr__("cols", cols)

        if values is not None:
            data = np.array(values, dtype)
            if (data.size != (rows * cols)
                    or data.shape[0] != rows
                    or data.shape[1] != cols):
                raise ValueError('Values does not match specified dimensions')
        else:
            data = np.zeros((rows, cols), dtype)

        super().__setattr__("_data", data)
        super().__setattr__("_keys", {})

    def __array__(self, _dtype=None):
        # pylint: disable=unused-argument
        return self._data

    def __getattr__(self, attr):
        if attr == "__setstate__":
            # fix for recursion problem during copy
            raise AttributeError(attr)
        if attr in self._keys:
            index = self._keys[attr]
            return self._data[index]
        raise AttributeError(f"'Matrix' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        if attr in self._keys:
            index = self._keys[attr]
            self._data[index] = value
            return
        if hasattr(self, attr):
            super().__setattr__(attr, value)
            return
        raise AttributeError(f"'Matrix' object has no attribute '{attr}'")

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    @staticmethod
    def create(rows, cols, data=None):
        """
        Create an nxn submatrix.
        """
        if rows == 3 and cols == 3:
            return Matrix33(data)
        if rows == 4 and cols == 4:
            return Matrix44(data)
        return Matrix(rows, cols, data)

    @classmethod
    def fromTranslation(cls, rows, cols, vector):
        """
        Create a translated copy of a matrix.
        """
        data = np.eye(rows, cols)
        data[0:rows - 1, cols - 1] = vector[0:rows - 1]
        return cls.create(rows, cols, data)

    @classmethod
    def identity(cls, rows, cols):
        """
        Create an identity matrix
        """
        data = np.eye(rows, cols)
        return cls.create(rows, cols, data)

    @classmethod
    def ones(cls, rows, cols):
        """
        Create a matrix of ones
        """
        data = np.ones((rows, cols))
        return cls.create(rows, cols, data)

    def transpose(self):
        """
        Create a transpose of the matrix
        """
        data = np.transpose(self._data)
        return self.create(self.cols, self.rows, data)

    def inverse(self):
        """
        Create a matrix for the inverse of this matrix
        """
        data = np.linalg.inv(self._data)
        return self.create(self.rows, self.cols, data)

    @property
    def determinant(self):
        """
        Get the determinant
        """
        return np.linalg.det(self._data)

    @property
    def invertible(self):
        """
        Determine if the matrix is of full rank
        """
        a = self._data
        return (a.shape[0] == a.shape[1]
                and np.linalg.matrix_rank(a) == a.shape[0])

    def __str__(self):
        return str(self._data)

    def __add__(self, other):
        if isinstance(other, Matrix):
            if other.rows != self.rows and other.cols != self.cols:
                raise ValueError("cannot add matrices due to bad dimensions")
            return self.create(self.rows, self.cols, self._data + other[:])

        return self.create(self.rows, self.cols, self._data + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Matrix):
            if other.rows != self.rows and other.cols != self.cols:
                raise ValueError(
                    "cannot subtract matrices due to bad dimensions")
            return self.create(self.rows, self.cols, self._data - other[:])

        return self.create(self.rows, self.cols, self._data - other)

    def __rsub__(self, other):
        return self.create(self.rows, self.cols, other - self._data)

    def __matmul__(self, other):
        if isinstance(other, Matrix):
            if other.rows != self.cols:
                raise ValueError(
                    "cannot multiply matrices due to bad dimensions")
            return self.create(self.rows,
                               other.cols,
                               np.matmul(self._data, other[:]))

        if isinstance(other, Vector):
            if other.size != self.cols:
                raise ValueError(
                    "cannot multiply matrix and vector due to bad dimensions")
            return Vector.create(self.rows, np.matmul(self._data, other[:]))

        return np.matmul(self._data, other)

    def __rmatmul__(self, other):
        return np.matmul(other, self._data)

    def __mul__(self, other):
        return self.create(self.rows, self.cols, self._data * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imatmul__(self, other):
        temp = self.__matmul__(other)
        # pylint: disable=attribute-defined-outside-init
        self._data = temp._data
        return self


class Matrix33(Matrix):
    """
    3x3 matrix implementation
    """
    # pylint: disable=arguments-differ

    def __init__(self, values=None, dtype=None):
        super().__init__(3, 3, values, dtype)
        self._keys = {
            'm11': (0, 0), 'm12': (0, 1), 'm13': (0, 2),
            'm21': (1, 0), 'm22': (1, 1), 'm23': (1, 2),
            'm31': (2, 0), 'm32': (2, 1), 'm33': (2, 2),
            'r1': (0, slice(None)), 'r2': (1, slice(None)),
            'r3': (2, slice(None)),
            'c1': (slice(None), 0), 'c2': (slice(None), 1),
            'c3': (slice(None), 2)
        }

    @classmethod
    def identity(cls):
        """
        Create a 3x3 identity matrix.
        """
        return super().identity(3, 3)

    @classmethod
    def ones(cls):
        """
        Create a 3x3 matrix of ones.
        """
        return super().ones(3, 3)

    @classmethod
    def fromTranslation(cls, vector):
        """
        Create a 3x3 translation matrix.
        """
        return super().fromTranslation(3, 3, vector)


class Matrix44(Matrix):
    """
    A 4x4 matrix implementation
    """
    # pylint: disable=arguments-differ

    def __init__(self, values=None, dtype=None):
        super().__init__(4, 4, values, dtype)
        self._keys = {
            'm11': (0, 0), 'm12': (0, 1), 'm13': (0, 2), 'm14': (0, 3),
            'm21': (1, 0), 'm22': (1, 1), 'm23': (1, 2), 'm24': (1, 3),
            'm31': (2, 0), 'm32': (2, 1), 'm33': (2, 2), 'm34': (2, 3),
            'm41': (3, 0), 'm42': (3, 1), 'm43': (3, 2), 'm44': (3, 3),
            'r1': (0, slice(None)), 'r2': (1, slice(None)),
            'r3': (2, slice(None)), 'r4': (3, slice(None)),
            'c1': (slice(None), 0), 'c2': (slice(None), 1),
            'c3': (slice(None), 2), 'c4': (slice(None), 3)
        }

    @classmethod
    def identity(cls):
        """
        Create a 4x4 identity matrix.
        """
        return super().identity(4, 4)

    @classmethod
    def ones(cls):
        """
        Create a 4x4 matrix of ones.
        """
        return super().ones(4, 4)

    @classmethod
    def fromTranslation(cls, vector):
        """
        Create a 4x4 translation matrix.
        """
        return super().fromTranslation(4, 4, vector)
