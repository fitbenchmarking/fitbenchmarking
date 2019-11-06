import os

"""
This script was used to insert a filetype identifier into FitBenchmark and
Sasview problem definition files.

Identifiers are "FitBenchmark problem" and "SasView Problem"
"""

file_dir = os.path.dirname(os.path.realpath(__file__))
bp_path = os.path.dirname(file_dir)
mapping = {'FitBenchmark Problem': ['Muon', 'Neutron', 'Neutron_test'],
           'SasView Problem': ['SAS_modelling/1D']}

for key in mapping:
    mapping[key] = [os.path.join(bp_path, d)
                    for d in mapping[key]]

for key, val in mapping.items():
    for path in val:
        for name in os.listdir(path):
            print('Found ' + name)
            if os.path.splitext(name)[1] == '.txt':
                data_file_path = os.path.join(path, name)
                print('Updating ' + data_file_path)
                with open(data_file_path, 'r') as f:
                    lines = f.readlines()

                lines.insert(0, '# ' + key + '\n')

                with open(data_file_path, 'w') as f:
                    f.writelines(lines)
