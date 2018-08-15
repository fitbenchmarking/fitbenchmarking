from setuptools import setup, find_packages

from build.commands.installs import InstallExternals
from build.commands.help import Help


setup(name='FitBenchmarking',
      version='1.0',
      description='Fit benchmarking software',
      author='ISIS Fit Benchmarking Team',
      url='http://github.com/mantidproject/fitbenchmarking',
      license='GPL-3.0',
      packages=find_packages(),
      install_requires=['docutils',
                        'matplotlib',
                        'libopenblas-dev',
                        'liblapack-dev',
                        'cython',
                        'scipy'],
      zip_safe=False,
      cmdclass={
          'externals': InstallExternals,
          'help': Help,
      },
     )
