#!/bin/bash

# Builds RALfit
./build_ralfit.sh
# Builds GSL
source build_gsl.sh

# To access RALfit
export LD_LIBRARY_PATH=$HOME/build/fitbenchmarking/fitbenchmarking/RALFit/libRALFit/build/src:$LD_LIBRARY_PATH

# Builds cutest
source build_cutest.sh
# to access cutest
export PATH="${SIFDECODE}/bin:${CUTEST}/bin:$PATH"

# Python bindings for GSL and CUTEst
pip install pygsl
pip install pycutest


pip install -r requirements.txt
pip install .
if [ "$TRAVIS_PYTHON_VERSION" == "2.7" ];
then
  source ./travis/py27_mantid_install.sh;
  pip install backports.tempfile
else
  python setup.py externals;
fi

export PYTHONPATH=$PYTHONPATH:/opt/Mantid/lib:/opt/Mantid/bin
