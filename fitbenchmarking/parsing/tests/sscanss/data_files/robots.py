import numpy as np
from sscanss.core.instrument.robotics import Link, SerialManipulator, Vector3


def two_link():
    """
    Create a two link robot
    """
    p1 = Vector3([1.0, 0.0, 0.0])
    p2 = Vector3([1.0, 0.0, 0.0])

    a1 = Vector3([0.0, 0.0, 1.0])
    a2 = Vector3([0.0, 0.0, 1.0])

    l1 = Link(
        name="l1",
        axis=a1,
        vector=p1,
        joint_type=Link.Type.Revolute,
        lower_limit=-np.pi,
        upper_limit=np.pi,
        default_offset=0.0,
    )
    l2 = Link(
        name="l2",
        axis=a2,
        vector=p2,
        joint_type=Link.Type.Revolute,
        lower_limit=-np.pi,
        upper_limit=np.pi,
        default_offset=0.0,
    )

    return SerialManipulator(name="2-link", links=[l1, l2])


def noise():
    """
    Small gaussian noise to create non-exact solution in 4x4 target matrices.
    """
    gen = np.random.default_rng(285138547)
    return gen.normal(loc=0.0, scale=1e-8, size=(4, 4))


robot = two_link()

targets = [robot.fkine([np.pi / 2, -np.pi / 2]) + noise()]
