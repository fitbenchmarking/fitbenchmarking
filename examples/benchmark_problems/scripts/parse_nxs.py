"""
This script was used to extract x, y, and e data from Mantid nexus files.
This relies on having Mantid installed and is only intended for use by
developers of FitBenchmarking.
"""

import itertools
import os

from mantid import simpleapi as ms


def parse_nxs(file_name):
    name, ext = os.path.splitext(file_name)
    if ext != '.nxs':
        print('Wrong file!', ext)
        return -1

    ws = ms.LoadNexus(file_name)
    xs = ws.readX(0)
    ys = ws.readY(0)
    es = ws.readE(0)

    data_template = '{0} {1} {2}\n'

    lines = ['# X Y E\n', '\n']
    lines += [data_template.format(x, y, e)
              for x, y, e in itertools.izip(xs, ys, es)]

    with open(name + '.txt', 'w') as f:
        f.writelines(lines)
