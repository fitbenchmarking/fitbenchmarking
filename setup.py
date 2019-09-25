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
      install_requires=['docutils', 'numpy<1.17', 'matplotlib<3.0',
                        'scipy>=0.17,<1.3', 'bumps', 'sasmodels', 'lxml', 'h5py'],
      zip_safe=False,

      cmdclass={
          'externals': InstallExternals,
          'help': Help,
      },
      package_data={'fitbenchmarking': ['resproc/color_definitions.txt']}
     )
