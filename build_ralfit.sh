#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

git clone https://github.com/ralna/RALFit

cd $SCRIPTPATH/RALFit/libRALFit/
mkdir build
cd build
cmake ..
make
python setup.py build_ext
python setup.py install

export LD_LIBRARY_PATH=$SCRIPTPATH/RALFit/libRALFit/build:$LD_LIBRARY_PATH

cd $SCRIPTPATH

#! /usr/bin/env bash

curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Travis-API-Version: 3" -H "Authorization: token 7u2X3sKhH6-HriIjYvtqPw" -d '{ "quiet": true }' https://api.travis-ci.org/job/607138661/debug
