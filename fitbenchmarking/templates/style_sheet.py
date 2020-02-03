"""
Functions to update style sheet from fitbenchmarking.com
"""
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
import inspect
import os
import wget

import fitbenchmarking

root = os.path.dirname(inspect.getfile(fitbenchmarking))
template_dir = os.path.join(root, 'templates')
filename = wget.download(
    "https://fitbenchmarking.com/assets/css/main.css", template_dir)

with open(filename, 'r') as f:
    expected = f.readlines()

style_sheet = os.path.join(template_dir, "main_style.css")
with open(style_sheet, 'r') as f:
    actual = f.readlines()

diff = []
for exp_line, act_line in zip_longest(expected, actual):
    if exp_line != act_line:
        diff.append([exp_line, act_line])

if diff == []:
    print("\nCurrent style sheet is up to date")
    os.remove(filename)
else:
    print("\nCurrent style sheet is out of date so downloading from "
          "fitbenchmarking.com")
    os.remove(style_sheet)
    os.rename(filename, style_sheet)
