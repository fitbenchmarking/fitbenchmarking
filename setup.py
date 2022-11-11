from setuptools import find_packages, setup, Extension

with open('README.md', encoding="utf-8") as f:
    long_description = f.read()

matlab_controller_c = Extension(
    name="fitbenchmarking.extern.matlab_controller_c",
    sources=['fitbenchmarking/controllers/matlab_controller/pyiface.c'],
    libraries=['matlabcontroller',
               'm',
               'mwmclmcrrt'],
    include_dirs=["/home/alister/MATLAB/R2022b/extern/include",
                  "/home/alister/MATLAB/R2022b/simulink/include",
                  "/home/alister/fitbenchmarking/fitbenchmarking/controllers"
                  "/matlab_controller"],
    library_dirs=['fitbenchmarking/controllers/matlab_controller',
                  '/home/alister/MATLAB/R2022b/runtime/glnxa64/']
)

setup(
    name='FitBenchmarking',
    description='FitBenchmarking: A tool for comparing fitting software',
    author='FitBenchmarking Team',
    author_email="support@fitbenchmarking.com",
    url='http://fitbenchmarking.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='BSD',
    python_requires='>=3.7.1',
    entry_points={
        "console_scripts": [
            'fitbenchmarking = fitbenchmarking.cli.main:main'
        ]
    },
    packages=find_packages(exclude=('*mock*', '*test*')),
    install_requires=['docutils',
                      'tqdm>=4.60',
                      'numpy',
                      'matplotlib>=2.0',
                      'scipy>=0.18',
                      'lxml',
                      'pandas>=1.3',
                      'jinja2',
                      'configparser'],
    extras_require={'DFO': ['DFO-LS', 'dfogn'],
                    'SAS': ['sasmodels',
                            'tinycc;platform_system==\'Windows\''],
                    'minuit': ['iminuit>=2.0'],
                    'bumps': ['bumps>=0.9.0'],
                    'numdifftools': ['numdifftools'],
                    'levmar': ['levmar'],
                    'mantid': ['h5py>=2.10.0,<3', 'pyyaml>=5.4.1'],
                    'matlab': ['dill'],
                    'gofit': ['gofit'],
                    'gradient_free': ['gradient-free-optimizers']},
    zip_safe=False,
    setup_requires=['setuptools_scm'],
    use_scm_version={'fallback_version': '1.0.0'},
    include_package_data=True,
    package_data={'': ['fonts/FiraSans/*/*',
                       'fonts/FontAwesome/*',
                       'templates/*',
                       'templates/css/*',
                       'templates/js/*',
                       'templates/js/output/chtml/fonts/woff-v2/*'],
                  },
    ext_modules=[matlab_controller_c],
)
