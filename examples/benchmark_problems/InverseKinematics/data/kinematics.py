"""
Definitions for the inverse kinematics problem files
"""
import sys
from pathlib import Path

import numpy as np

# pylint: disable=wrong-import-position
sys.path.append(str(Path(__file__).parent.parent / 'utils'))
from robotics import enginx_combo, goniometer, table, two_link  # noqa:E402

twolink_robot = two_link()
table_robot = table()
goniometer_robot = goniometer()
enginx_combo_robot = enginx_combo()

tl1 = twolink_robot.fkine([np.pi / 2, -np.pi / 2])
tl2 = twolink_robot.fkine([1, 0.001])

t1 = table_robot.fkine([109.23, np.pi / 2, -100, 40])
t2 = table_robot.fkine([53.81, -np.pi / 4, -10, 40.9])

g1 = goniometer_robot.fkine([np.pi / 2, -np.pi / 3, -np.pi / 4])
g2 = goniometer_robot.fkine([np.pi / 3, np.pi / 4, np.pi / 3])

ec1 = enginx_combo_robot.fkine(
    [24, np.pi / 5, -103, -125, -np.pi / 2, -np.pi / 2, np.pi / 1.1])
ec2 = enginx_combo_robot.fkine(
    [12, -np.pi / 5, -113, -15, np.pi / 1.5, -np.pi / 20, np.pi / 4])
