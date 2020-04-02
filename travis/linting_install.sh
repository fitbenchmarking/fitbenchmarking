#!/bin/bash

pip install pylint
pip install flake8

pip install -r requirements.txt
pip install .

if [ "$TRAVIS_PYTHON_VERSION" == "2.7" ];
then
  pip install backports.tempfile;
fi

# Python bindings for GSL and CUTEst
pip install pygsl
pip install pycutest