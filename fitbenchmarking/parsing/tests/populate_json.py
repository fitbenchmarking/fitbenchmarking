"""
This script was used to populate the expected values for functions from each
of the parsers.
Ideally it would be done through the original software, but for batch
generating this is sufficient.
"""
from json import load, dump

import os

from fitbenchmarking.parsing.parser_factory import parse_problem_file

base_file = os.path.join(os.path.dirname(__file__), '{}', 'basic.{}')
fitbenchmark_file = base_file.format('fitbenchmark', 'txt')
sasview_file = base_file.format('sasview', 'txt')
nist_file = base_file.format('nist', 'dat')

base_output = os.path.join(os.path.dirname(__file__), 
                           '{}',
                           'function_evaluations',
                           'basic.json')
fitbenchmark_output = base_output.format('fitbenchmark')
sasview_output = base_output.format('sasview')
nist_output = base_output.format('nist')

with open(fitbenchmark_output) as o:
    empty_input = load(o)

for inp, out in zip([fitbenchmark_file, sasview_file, nist_file],
                    [fitbenchmark_output, sasview_output, nist_output]):
    fitting_problem = parse_problem_file(inp)

    to_write = []
    for x, params, _ in empty_input:
        results = float(fitting_problem.eval_f(x, params, 0))

        to_write.append([x, params, results])

    with open(out, 'w') as o:
        dump(to_write, o)
