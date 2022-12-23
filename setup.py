from setuptools import find_packages, setup
from glob import glob

with open('README.md', encoding="utf-8") as f:
    long_description = f.read()

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
                    'nlopt': ['nlopt'],
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
                  }
)
