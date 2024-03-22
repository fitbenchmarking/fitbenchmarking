"""
Implementation of vector for kinematics
"""
import numpy as np


class Vector:
    """
    A vector
    """
    # pylint: disable=attribute-defined-outside-init
    __array_priority__ = 1

    def __init__(self, size, values=None, dtype=None):
        if size < 1:
            raise ValueError("size must not be less than 1")
        if values is not None:
            if len(values) != size:
                raise ValueError("Values does not match specified size!")
            data = np.array(values[:size], dtype)
        else:
            data = np.zeros(size, dtype)

        super().__setattr__("size", size)
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
        raise AttributeError("'Vector' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        if attr in self._keys:
            index = self._keys[attr]
            self._data[index] = value
            return
        if hasattr(self, attr):
            super().__setattr__(attr, value)
            return
        raise AttributeError("'Vector' object has no attribute '{attr}'")

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    @staticmethod
    def create(size, data=None):
        """
        Create an n vector
        """
        if size == 2:
            return Vector2(data)
        if size == 3:
            return Vector3(data)
        if size == 4:
            return Vector4(data)
        return Vector(size, data)

    @property
    def length(self):
        """
        Length of the vector
        """
        return np.linalg.norm(self._data)

    def normalize(self):
        """
        Make the length of the vector equal to 1
        """
        self._data = self._data / self.length

    @property
    def normalized(self):
        """
        Create a new vector parallel to this with length 1
        """
        data = self._data / self.length
        return self.create(self.size, data)

    def __helper(self, left, right, func):
        result = func(left, right)

        if len(result) == self.size:
            return self.create(self.size, result)

        return result

    def __add__(self, other):
        func = np.add
        if isinstance(other, Vector):
            if len(other) != self.size:
                raise ValueError("cannot add vectors of different sizes")
            return self.__helper(self._data, other[:], func)
        return self.__helper(self._data, other, func)

    def __sub__(self, other):
        func = np.subtract
        if isinstance(other, Vector):
            if len(other) != self.size:
                raise ValueError("cannot subtract vectors of different sizes")
            return self.__helper(self._data, other[:], func)
        return self.__helper(self._data, other, func)

    def __mul__(self, other):
        func = np.multiply
        if isinstance(other, Vector):
            if len(other) != self.size:
                raise ValueError("cannot multiply vectors of different sizes")
            return self.__helper(self._data, other[:], func)
        return self.__helper(self._data, other, func)

    def __truediv__(self, other):
        func = np.true_divide
        if isinstance(other, Vector):
            if len(other) != self.size:
                raise ValueError("cannot divide vectors of different sizes")
            return self.__helper(self._data, other[:], func)
        return self.__helper(self._data, other, func)

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return self.__helper(other, self._data, np.subtract)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        return self.__helper(other, self._data, np.true_divide)

    def __iadd__(self, other):
        temp = self.__add__(other)
        self._data = temp._data
        return self

    def __isub__(self, other):
        temp = self.__sub__(other)
        self._data = temp._data
        return self

    def __imul__(self, other):
        temp = self.__mul__(other)
        self._data = temp._data
        return self

    def dot(self, other):
        """
        Calculate the inner product
        """
        return np.dot(self._data, other[:])

    def cross(self, other):
        """
        Calculate the outer product
        """
        data = np.cross(self._data, other[:])
        if data.size == 1:
            return self.create(3, [0, 0, data])
        return self.create(data.size, data)

    def __or__(self, other):
        return self.dot(other)

    def __xor__(self, other):
        return self.cross(other)

    def __neg__(self):
        return self.create(self._data.size, -1 * self._data)

    def __len__(self):
        return self.size

    def __str__(self):
        return str(self._data)


class Vector2(Vector):
    """
    2D vector implementation
    """

    def __init__(self, values=None, dtype=None):
        super().__init__(2, values, dtype)
        self._keys = {'x': 0, 'y': 1, 'xy': slice(None)}


class Vector3(Vector):
    """
    3D vector implementation
    """

    def __init__(self, values=None, dtype=None):
        super().__init__(3, values, dtype)
        self._keys = {'x': 0, 'y': 1, 'z': 2,
                      'xy': slice(2), 'xyz': slice(None)}


class Vector4(Vector):
    """
    4D vector implementation
    """

    def __init__(self, values=None, dtype=None):
        super().__init__(4, values, dtype)
        self._keys = {'x': 0, 'y': 1, 'z': 2, 'w': 3,
                      'xy': slice(2), 'xyz': slice(3), 'xyzw': slice(None)}
