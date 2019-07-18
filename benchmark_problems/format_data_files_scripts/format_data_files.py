import os

"""
This script was used to re-format data files specified in FitBenchmark problem definition files in the sub-folder
'data_files' of Muon_data and Neutron_data.

If the data error column of the data files is 'nan' or 0 they are changed to 1. The latter is in accordance with the
default fitting behaviour in Mantid. 
"""

file_dir = os.path.dirname(os.path.realpath(__file__))
bp_path = os.path.dirname(file_dir)
muon_data_path = os.path.join(bp_path, 'Muon_data', 'data_files')
neutron_data_path = os.path.join(bp_path, 'Neutron_data', 'data_files')

paths = [muon_data_path, neutron_data_path]

for path in paths:
    for root, dirs, files in os.walk(path):
        for name in files:
            if os.path.splitext(name)[1] == '.txt':
                data_file_path = os.path.join(root, name)

                data_file = open(data_file_path, 'r+')

                data_string = (data_file.readlines())

                for idx, line in enumerate(data_string[2:]):
                    line = line.strip()
                    point_text = line.split()
                    if point_text[2] == 'nan':
                        point_text[2] = '1.000000e+00'
                        sentence = '    '.join(point_text)
                        data_string[idx+2] = sentence + '\n'
                    elif float(point_text[2]) == 0.0:
                        point_text[2] = '1.000000e+00'
                        sentence = '    '.join(point_text)
                        data_string[idx+2] = sentence + '\n'

                data_file.seek(0)
                data_file.writelines(data_string)
                data_file.close()
