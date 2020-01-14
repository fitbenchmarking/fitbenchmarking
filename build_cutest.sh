#!/bin/bash

SCRIPTPATH=$PWD

cd $HOME
mkdir cutest
cd cutest
git clone https://github.com/ralna/ARCHDefs ./archdefs
git clone https://github.com/ralna/SIFDecode ./sifdecode
git clone https://github.com/ralna/CUTEst ./cutest

cd $HOME/cutest

export ARCHDEFS=$HOME/cutest/archdefs/
export SIFDECODE=$HOME/cutest/sifdecode/
export MASTSIF=$SCRIPTPATH/examples/benchmark_problems/SIF/
export CUTEST=$HOME/cutest/cutest/
export MYARCH="pc64.lnx.gfo"
mkdir pycutest_cache
export PYCUTEST_CACHE=$PWD/pycutest_cache
export PYTHONPATH="${PYCUTEST_CACHE}:${PYTHONPATH}"

# install sifdecode
cd $SIFDECODE
# 6 - 64 bit PC
# 2 - linux
# 5 - gfortran compiler
printf "6\n2\n5\n" > sifdecode.input
# n - modify compiler settings?
# n - modify system commands?
# y - compile the package
printf "nny" >> sifdecode.input

./install_sifdecode  < sifdecode.input

# install cutest

cd $CUTEST
# 6 - 64 bit PC
# 2 - linux
# 5 - gfortran compiler
# 2 - everything except matlab
# 7 - generic gcc compiler
printf "6\n2\n5\n2\n7\n" > cutest.input
# n - modify compiler settings?
# n - modify system commands?
# y - compile package subset?
# d - double precision
# y - install single precision?
printf "nnydn" >> cutest.input

./install_cutest < cutest.input



cd $SCRIPTPATH


