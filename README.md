[![Build Status](https://travis-ci.com/mantidproject/fitbenchmarking.svg?branch=master)](https://travis-ci.com/mantidproject/fitbenchmarking) [![Coverage Status](https://coveralls.io/repos/github/mantidproject/fitbenchmarking/badge.svg?branch=112_addTestCoverageTracking)](https://coveralls.io/github/mantidproject/fitbenchmarking?branch=112_addTestCoverageTracking)

# FitBenchmarking
FitBenchmarking is an open source tool for comparing different minimizers/fitting frameworks based on their accuracy and runtimes.


## Quick start
You will need [Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg) for running/installing this. Instructions for setting up python are available [here](https://github.com/mantidproject/fitbenchmarking/wiki/Setting-up-Python).

1. Download this repository or clone it using [git](https://git-scm.com/):
`git clone https://github.com/mantidproject/fitbenchmarking.git`
2. Open up a terminal (command prompt) and go into the `fitbenchmarking` directory.
3. Once you are in the right directory, type `python setup.py install`.
4. Optionally, you can install some of the supported fitting software that is benchmarked using this tool. To do this, please run `python setup.py help` and follow the instructions displayed there.
5. Finally, you can see an example script, `example_runScript.py`, located in the example_scripts folder. This example script fit benchmarks Mantid using all the available minimizers.
