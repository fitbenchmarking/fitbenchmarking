from setuptools import setup, find_packages

from build.commands.installs import InstallExternals
from build.commands.help import Help


setup(name='FitBenchmarking',
      version='0.1.dev2',
      description='FitBenchmarking software',
      author='FitBenchmarking Team',
      url='http://github.com/fitbenchmarking/fitbenchmarking',
      license='GPL-3.0',
      packages=find_packages(),
      install_requires=['docutils', 'scipy>=0.17,<1.3', 'bumps', 'sasmodels', 'lxml'],
      zip_safe=False,
      cmdclass={
          'externals': InstallExternals,
          'help': Help,
      },
     )
