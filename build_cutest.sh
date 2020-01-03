#!/bin/bash

SCRIPTPATH=$PWD

mkdir cutest
cd cutest
git clone https://github.com/ralna/ARCHDefs ./archdefs
git clone https://github.com/ralna/SIFDecode ./sifdecode
git clone https://github.com/ralna/CUTEst ./cutest

cd $SCRIPTPATH/cutest

export ARCHDEFS=/path/to/cutest/archdefs/
export SIFDECODE=/path/to/cutest/sifdecode/
export MASTSIF=/path/to/cutest/mastsif/
export CUTEST=/path/to/cutest/cutest/
export MYARCH="pc64.lnx.gfo"

echo "N Y N 6 3 N 5 N 2 N Y Y D" | ${ARCHDEFS}/install_optrove

cd $SCRIPTPATH
