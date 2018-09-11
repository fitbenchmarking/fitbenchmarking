[![Build Status](https://travis-ci.com/mantidproject/fitbenchmarking.svg?branch=master)](https://travis-ci.com/mantidproject/fitbenchmarking) [![Coverage Status](https://coveralls.io/repos/github/mantidproject/fitbenchmarking/badge.svg?branch=112_addTestCoverageTracking)](https://coveralls.io/github/mantidproject/fitbenchmarking?branch=112_addTestCoverageTracking)

# FitBenchmarking
FitBenchmarking is an open source tool for comparing different minimizers/fitting frameworks based on their accuracy and runtimes.
Currently, it can be used to compare minimizers in Mantid.

Work is being done to allow this tool to benchmark minimizers from other libraries/software as well.



## Installation
Python 2.7 or later is required to install and run the FtiBenchmarking tool. If you are using Windows, instructions on how to set up python and how to change the PATH environment variable are available [here](https://anthonydebarros.com/2018/06/21/setting-up-python-in-windows-10/).

1. Download this repository or clone it using git:
`git clone https://github.com/mantidproject/fitbenchmarking.git`
2. Open up a terminal(cmd) and change directory to `../fitbenchmarking/`
3. Once you are in the right directory, type `python setup.py install` to install the tool's external package dependencies.
    * To perform this step, you need to have the `setuptools` module installed. If it is not already available:
    * On Linux: `pip install setuptools` or `sudo apt-get install setuptools`
    * On Windows: please follow this [guide](https://packaging.python.org/tutorials/installing-packages/)
4. Optionally, you can install some of the supported fitting software that is benchmarked using this tool. To do this, please run `python setup.py help` and follow the instructions displayed there.
5. Finally, you can see an example script, `example_runScript.py`, located in the example_scripts folder. This example script fit benchmarks Mantid using all the available minimizers.
