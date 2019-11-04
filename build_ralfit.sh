#!/bin/bash

git clone https://github.com/ralna/RALFit

cd $SCRIPTPATH/RALFit/libRALFit/
mkdir build
cd build
cmake ..
make
python setup.py build_ext --inplace
export PYTHONPATH=$SCRIPTPATH/libRALFit/build/:${PYTHONPATH}

cd $SCRIPTPATH
