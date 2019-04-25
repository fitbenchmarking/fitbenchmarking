from setuptools import setup, find_packages

from build.commands.installs import InstallExternals
from build.commands.help import Help


setup(name='FitBenchmarking',
      version='0.1.dev2',
      description='Fit benchmarking software',
      author='ISIS Fit Benchmarking Team',
      url='http://github.com/fitbenchmarking/fitbenchmarking',
      license='GPL-3.0',
      packages=find_packages(),
      install_requires=['docutils', 'scipy>=0.17'],
      zip_safe=False,
      cmdclass={
          'externals': InstallExternals,
          'help': Help,
      },
     )
