"""
Definitions for the inverse kinematics problem files
"""
import sys
from pathlib import Path

import numpy as np
from sscanss.core.instrument.robotics import Link, Vector3, SerialManipulator

# pylint: disable=wrong-import-position,import-error
sys.path.append(str(Path(__file__).parent.parent / 'utils'))


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

    l1 = Link(name='l1',
              axis=a1,
              vector=p2 - p1,
              joint_type=Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi,
              default_offset=0.0)
    l2 = Link(name='l2',
              axis=a2,
              vector=p3 - p2,
              joint_type=Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi,
              default_offset=0.0)
    l3 = Link(name='l3',
              axis=a3,
              vector=p3 - p3,
              joint_type=Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi,
              default_offset=0.0)

    return SerialManipulator(name='goniometer', links=[l1, l2, l3])


def two_link():
    """
    Create a two link robot
    """
    p1 = Vector3([1.0, 0.0, 0.0])
    p2 = Vector3([1.0, 0.0, 0.0])

    a1 = Vector3([0.0, 0.0, 1.0])
    a2 = Vector3([0.0, 0.0, 1.0])

    l1 = Link(name='l1',
              axis=a1,
              vector=p1,
              joint_type=Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi,
              default_offset=0.0)
    l2 = Link(name='l2',
              axis=a2,
              vector=p2,
              joint_type=Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi,
              default_offset=0.0)

    return SerialManipulator(name='2-link', links=[l1, l2])


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

    l1 = Link(name='z',
              axis=a1,
              vector=p1,
              joint_type=Link.Type.Prismatic,
              lower_limit=0, upper_limit=500,
              default_offset=0.0)
    l2 = Link(name='rot',
              axis=a2,
              vector=p2,
              joint_type=Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi,
              default_offset=0.0)
    l3 = Link(name='x',
              axis=a3,
              vector=p3,
              joint_type=Link.Type.Prismatic,
              lower_limit=-200, upper_limit=200,
              default_offset=0.0)
    l4 = Link(name='y',
              axis=a4,
              vector=p4,
              joint_type=Link.Type.Prismatic,
              lower_limit=-200, upper_limit=200,
              default_offset=0.0)

    return SerialManipulator(name='table', links=[l1, l2, l3, l4])


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

    l1 = Link(name='l1',
              axis=a1,
              vector=p1,
              joint_type=Link.Type.Prismatic,
              lower_limit=0, upper_limit=500,
              default_offset=0.0)
    l2 = Link(name='l2',
              axis=a2,
              vector=p2,
              joint_type=Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi,
              default_offset=0.0)
    l3 = Link(name='l3',
              axis=a3,
              vector=p3,
              joint_type=Link.Type.Prismatic,
              lower_limit=-200, upper_limit=200,
              default_offset=0.0)
    l4 = Link(name='l4',
              axis=a4,
              vector=p5 - p4,
              joint_type=Link.Type.Prismatic,
              lower_limit=-200, upper_limit=200,
              default_offset=0.0)
    l5 = Link(name='l5',
              axis=a5,
              vector=p6 - p5,
              joint_type=Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi,
              default_offset=0.0)
    l6 = Link(name='l6',
              axis=a6,
              vector=p7 - p6,
              joint_type=Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi,
              default_offset=0.0)
    l7 = Link(name='l7',
              axis=a7,
              vector=p7 - p7,
              joint_type=Link.Type.Revolute,
              lower_limit=-np.pi, upper_limit=np.pi,
              default_offset=0.0)

    return SerialManipulator(name='engin-x',
                             links=[l1, l2, l3, l4, l5, l6, l7])


def noise():
    """
    Small gaussian noise to create non-exact solution in 4x4 target matrices.
    """
    return np.random.normal(loc=0.0, scale=1e-8, size=(4, 4))


twolink_robot = two_link()
table_robot = table()
goniometer_robot = goniometer()
enginx_combo_robot = enginx_combo()

tl_targets = [
    twolink_robot.fkine([np.pi / 2, -np.pi / 2]) + noise(),
    twolink_robot.fkine([1, 0.001]) + noise()]

t_targets = [table_robot.fkine([109.23, np.pi / 2, -100, 40]) + noise(),
             table_robot.fkine([53.81, -np.pi / 4, -10, 40.9]) + noise()]

g_targets = [
    goniometer_robot.fkine([np.pi / 2, -np.pi / 3, -np.pi / 4]) + noise(),
    goniometer_robot.fkine([np.pi / 3, np.pi / 4, np.pi / 3]) + noise()
]

ec_targets = [
    enginx_combo_robot.fkine([24, np.pi / 5, -103, -125, -np.pi / 2,
                              -np.pi / 2, np.pi / 1.1]) + noise(),
    enginx_combo_robot.fkine([12, -np.pi / 5, -113, -15,
                              np.pi / 1.5, -np.pi / 20, np.pi / 4]) + noise()
]
