import glob
import os
import shutil

from setuptools import find_packages, setup

from build.commands.help import Help
from build.commands.installs import InstallExternals

setup(name='FitBenchmarking',
      version='0.1.0',
      description='FitBenchmarking is an open source tool for comparing different minimizers/fitting frameworks.',
      author='FitBenchmarking Team',
      author_email="support@fitbenchmarking.com",
      url='http://fitbenchmarking.com',
      long_description=README.md,
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
      cmdclass={
          'externals': InstallExternals,
          'help': Help,
      },
      package_data={'fitbenchmarking': ['utils/default_options.ini',
                                        'templates/*']})


# Clean up build files
CLEAN_FILES = ['./dist', './*.pyc', './*.tgz', './lib/*.egg-info']
CURDIR = os.path.abspath(os.curdir)

for path_spec in CLEAN_FILES:
    # Make paths absolute and relative to this path
    abs_paths = glob.glob(os.path.normpath(os.path.join(CURDIR, path_spec)))
    for path in [str(p) for p in abs_paths]:
        if not path.startswith(CURDIR):
            # Die if path in CLEAN_FILES is absolute + outside this directory
            raise ValueError("{} is not a path inside {}".format(path, CURDIR))
        print('removing {}'.format(os.path.relpath(path)))
        shutil.rmtree(path)
