#!/bin/bash

SCRIPTPATH=$PWD

git clone https://github.com/ralna/RALFit

cd $SCRIPTPATH/RALFit/libRALFit/
mkdir build
cd build
cmake ..
make
python3 setup.py build_ext --user
python3 setup.py install --user

cd $SCRIPTPATH
