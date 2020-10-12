import glob
import os
import shutil

from setuptools import find_packages, setup

with open('README.md', encoding="utf-8") as f:
    long_description = f.read()
    
setup(name='FitBenchmarking',
      version='0.1.dev1',
      description='FitBenchmarking: A tool for comparing fitting software',
      author='FitBenchmarking Team',
      author_email="support@fitbenchmarking.com",
      url='http://fitbenchmarking.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='BSD',
      entry_points={
          "console_scripts": [
              'fitbenchmarking = fitbenchmarking.cli.main:main'
          ]
      },
      packages=find_packages(exclude=('*mock*', '*test*')),
      install_requires=['docutils',
                        'numpy',
                        'matplotlib>=2.0',
                        'scipy>=0.18',
                        'lxml',
                        'pandas>=1.0',
                        'jinja2',
                        'configparser',
                        'h5py'],
      extras_require={'DFO': ['DFO-LS','dfogn'],
                      'SAS': ['sasmodels'],
                      'minuit': ['iminuit'],
                      'bumps': ['bumps']},
      zip_safe=False,
      package_data={'fitbenchmarking': ['templates/*']})

