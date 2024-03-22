"""
The forward kinematics models
"""
from enum import Enum, unique

import numpy as np
from matrix import Matrix44
from quaternion import Quaternion, QuaternionVectorPair
from vector import Vector3


class SerialManipulator:
    """
    An open loop kinematic chain
    """

    def __init__(self, links, base=None, tool=None, name=''):
        """ This class defines a open loop kinematic chain.

        :param links: list of link objects
        :type links: List[Link]
        :param base: base matrix. None sets base to an identity matrix
        :type base: Union[None, Matrix44]
        :param tool: tool matrix. None sets tool to an identity matrix
        :type tool: Union[None, Matrix44]
        :param name: name of the manipulator
        :type name: str
        """
        self.name = name
        self.links = links
        self.base = Matrix44.identity() if base is None else base
        self.default_base = self.base
        self.tool = Matrix44.identity() if tool is None else tool

    def fkine(self, q, start_index=0, end_index=None,
              include_base=True, ignore_locks=False, setpoint=True):
        """
        Moves the manipulator to specified configuration and returns the
        forward kinematics transformation matrix of the manipulator.
        The transformation matrix can be computed for a subset of links
        i.e a start index to end index

        :param q: Joint offsets to move to.
                  The length must be equal to number of links
        :type q: List[float]
        :param start_index: index to start
        :type start_index: int
        :param end_index: index to end. None sets value to index of last link
        :type end_index: Union[None, int]
        :param include_base: indicates that base matrix should be included
        :type include_base: bool
        :param ignore_locks: indicates that joint locks should be ignored
        :type ignore_locks: bool
        :param setpoint: indicates that given configuration, q is a setpoint
        :type setpoint: bool
        :return: Forward kinematic transformation matrix
        :rtype: Matrix44
        """
        link_count = self.link_count

        start = max(0, start_index)
        end = link_count if end_index is None else min(link_count, end_index)

        base = self.base if include_base and not start else Matrix44.identity()
        tool = self.tool if end == link_count else Matrix44.identity()

        qs = QuaternionVectorPair.identity()
        for i in range(start, end):
            self.links[i].move(q[i], ignore_locks, setpoint)
            qs *= self.links[i].quaterionVectorPair

        return base @ qs.toMatrix() @ tool

    def resetOffsets(self):
        """
        resets link offsets to the defaults
        """
        for link in self.links:
            link.reset()

    def reset(self):
        """
         resets  base matrix, link offsets, locks, and limits to the defaults
        """
        self.base = self.default_base
        for link in self.links:
            link.reset()
            link.locked = False
            link.ignore_limits = False

    @property
    def link_count(self):
        """ number of links in manipulator

        :return: number of links
        :rtype: int
        """
        return len(self.links)

    @property
    def set_points(self):
        """
        expected configuration (set-point for all links) of the manipulator.
        This is useful when the animating the manipulator in that case the
        actual configuration differs from the set-point or final configuration.

        :return: expected configuration
        :rtype: list[float]
        """
        return [link.set_point for link in self.links]

    @set_points.setter
    def set_points(self, q):
        """ setter for set_points

        :param q: expected configuration
        :type q: list[float]
        """
        for offset, link in zip(q, self.links):
            link.set_point = offset

    @property
    def configuration(self):
        """
        current configuration (joint offsets for all links) of the manipulators

        :return: current configuration
        :rtype: list[float]
        """
        return [link.offset for link in self.links]

    @property
    def pose(self):
        """ the pose of the end effector of the manipulator

        :return: transformation matrix
        :rtype: Matrix44
        """
        qs = QuaternionVectorPair.identity()
        for link in self.links:
            qs *= link.quaterionVectorPair

        return self.base @ qs.toMatrix() @ self.tool


class Link:
    """
    A single link/joint in a serial manipulator
    """
    @unique
    class Type(Enum):
        """
        Type of link
        """
        Revolute = 0
        Prismatic = 1

    def __init__(self, axis, point, joint_type, default_offset=0.0,
                 upper_limit=None, lower_limit=None, name=''):
        """
        This class represents a link/joint that belongs to a serial
        manipulator.
        The joint could be revolute or prismatic.
        The link is represented using the Quaternion-vector kinematic notation.

        :param axis: axis of rotation or translation
        :type axis: List[float]
        :param point: centre of joint
        :type point: List[float]
        :param joint_type: joint type
        :type joint_type: Link.Type
        :param default_offset: default joint offset
        :type default_offset: float
        :param upper_limit: upper limit of joint
        :type upper_limit: float
        :param lower_limit: lower limit of joint
        :type lower_limit: float
        :param name: name of the link
        :type name: str
        """
        self.joint_axis = Vector3(axis)

        if self.joint_axis.length < 0.00001:
            raise ValueError('The joint axis cannot be a zero vector.')

        self.quaternion = Quaternion.fromAxisAngle(self.joint_axis, 0.0)
        self.vector = Vector3(point)
        self.home = Vector3(point)
        self.type = joint_type
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.default_offset = default_offset
        self.set_point = default_offset
        self.name = name
        self.locked = False
        self.ignore_limits = False
        self.offset = default_offset
        self.reset()

    def move(self, offset, ignore_locks=False, setpoint=True):
        """ moves link by the specified offset

        :param offset: joint offset
        :type offset: float
        :param ignore_locks: indicates that joint locks should be ignored
        :type ignore_locks: bool
        :param setpoint: indicates that given offset is a setpoint
        :type setpoint: bool
        """
        if self.locked and not ignore_locks:
            return

        self.offset = offset
        self.set_point = offset if setpoint else self.set_point
        if self.type == Link.Type.Revolute:
            self.quaternion = Quaternion.fromAxisAngle(self.joint_axis, offset)
            self.vector = self.quaternion.rotate(self.home)
        else:
            self.vector = self.home + self.joint_axis * offset

    def reset(self):
        """
        moves link to it default offset
        """
        self.move(self.default_offset, True)

    @property
    def transformationMatrix(self):
        """ pose of the link

        :return: pose of the link
        :rtype: Matrix44
        """
        return self.quaterionVectorPair.toMatrix()

    @property
    def quaterionVectorPair(self):
        """ pose of the link

        :return: pose of the link
        :rtype: QuaternionVectorPair
        """
        return QuaternionVectorPair(self.quaternion, self.vector)


def goniometer():
    """
    Create a Goniometer robot
    """
    p1 = Vector3([0.0, 0.0, 0.0])
    p2 = Vector3([49.939575, 0.00012207031, 50.082535])
    p3 = Vector3([0.026367188, 0.012207031, 0.0052795410])

    a1 = Vector3([0.0, 0.0, 1.0])
    a2 = Vector3([-0.70665777, -0.0010367904, 0.70755470])
    a3 = Vector3([0.0001057353511, -0.0000935252756, 1.0000000000000])

    l1 = Link(a1, p2 - p1, Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi)
    l2 = Link(a2, p3 - p2, Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi)
    l3 = Link(a3, p3 - p3, Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi)

    return SerialManipulator([l1, l2, l3])


def two_link():
    """
    Create a two link robot
    """
    p1 = Vector3([1.0, 0.0, 0.0])
    p2 = Vector3([1.0, 0.0, 0.0])

    a1 = Vector3([0.0, 0.0, 1.0])
    a2 = Vector3([0.0, 0.0, 1.0])

    l1 = Link(a1, p1, Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi)
    l2 = Link(a2, p2, Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi)

    return SerialManipulator([l1, l2])


def table():
    """
    Create a table robot
    """
    p1 = Vector3([0.0, 0.0, 0.0])
    p2 = Vector3([0.0, 0.0, 0.0])
    p3 = Vector3([0.0, 0.0, 0.0])
    p4 = Vector3([0.0, 0.0, 0.0])

    a1 = Vector3([0.0, 0.0, 1.0])
    a2 = Vector3([0.0, 0.0, -1.0])
    a3 = Vector3([0.0, 1.0, 0.0])
    a4 = Vector3([1.0, 0.0, 0.0])

    l1 = Link(a1, p1, Link.Type.Prismatic, lower_limit=0, upper_limit=500)
    l2 = Link(a2, p2, Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi)
    l3 = Link(a3, p3, Link.Type.Prismatic, lower_limit=-200, upper_limit=200)
    l4 = Link(a4, p4, Link.Type.Prismatic, lower_limit=-200, upper_limit=200)

    return SerialManipulator([l1, l2, l3, l4])


def enginx_combo():
    """
    Create an enginx combo robot
    """
    p1 = Vector3([0.0, 0.0, 0.0])
    p2 = Vector3([0.0, 0.0, 0.0])
    p3 = Vector3([0.0, 0.0, 0.0])
    p4 = Vector3([0.0, 0.0, 0.0])
    p5 = Vector3([0.0, 0.0, 0.0])
    p6 = Vector3([49.94, 0.0, 50.083])
    p7 = Vector3([0.027, 0.012, 0.005])

    a1 = Vector3([0.0, 0.0, 1.0])
    a2 = Vector3([0.0, 0.0, -1.0])
    a3 = Vector3([0.0, 1.0, 0.0])
    a4 = Vector3([1.0, 0.0, 0.0])
    a5 = Vector3([0.0, 0.0, 1.0])
    a6 = Vector3([-0.7066578, -0.0010368, 0.7075547])
    a7 = Vector3([0.0001057, -0.0000935, 1.0000000])

    l1 = Link(a1, p1, Link.Type.Prismatic, lower_limit=0, upper_limit=500)
    l2 = Link(a2, p2, Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi)
    l3 = Link(a3, p3, Link.Type.Prismatic, lower_limit=-200, upper_limit=200)
    l4 = Link(a4, p5 - p4, Link.Type.Prismatic,
              lower_limit=-200, upper_limit=200)
    l5 = Link(a5, p6 - p5, Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi)
    l6 = Link(a6, p7 - p6, Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi)
    l7 = Link(a7, p7 - p7, Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi)

    return SerialManipulator([l1, l2, l3, l4, l5, l6, l7])
