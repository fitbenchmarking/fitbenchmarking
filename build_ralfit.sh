#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

git clone https://github.com/ralna/RALFit

cd $SCRIPTPATH/RALFit/libRALFit/
mkdir build
cd build
cmake ..
make
python setup.py build
python setup.py install

cd $SCRIPTPATH
