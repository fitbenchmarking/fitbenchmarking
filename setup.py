from build.commands.installs import InstallExternals
from build.commands.help import Help
import os
from setuptools import setup, find_packages
import sys

sys.path.insert(0, os.path.abspath('lib/'))

setup(name='FitBenchmarking',
      version='0.1.dev2',
      description='FitBenchmarking software',
      author='FitBenchmarking Team',
      url='http://github.com/fitbenchmarking/fitbenchmarking',
      license='GPL-3.0',
      scripts=['bin/fitbenchmarking'],
      packages=find_packages('lib/'),
      package_dir={'': 'lib'},
      install_requires=['docutils',
                        'numpy<1.17',
                        'matplotlib<3.0',
                        'scipy>=0.18,<1.3',
                        'bumps',
                        'sasmodels',
                        'lxml',
                        'pandas<=0.24.2',
                        'jinja2',
                        'pytablewriter<=0.46.1',
                        'dfogn',
                        'iminuit',
                        'configparser'],
      zip_safe=False,

      cmdclass={
          'externals': InstallExternals,
          'help': Help,
      },
      package_data={'fitbenchmarking': ['utils/default_options.ini']}
      )
