#!/bin/bash

SCRIPTPATH=$PWD

git clone https://github.com/ralna/RALFit

cd $SCRIPTPATH/RALFit/libRALFit/
mkdir build
cd build
cmake ..
make
python setup.py build_ext
python setup.py install

cd $SCRIPTPATH
