#!/bin/bash

sudo apt-get upgrade
sudo apt-get install cmake gfortran lcov libblas-dev liblapack-dev -y

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

export LD_LIBRARY_PATH=${SCRIPTPATH}/RALFit/libRALFit/build/src:$LD_LIBRARY_PATH

printf "To enable RALFit in future sessions we recommend adding \n
'export LD_LIBRARY_PATH=${SCRIPTPATH}/RALFit/libRALFit/build/src:\$LD_LIBRARY_PATH' \n
to your .bashrc file \n"
