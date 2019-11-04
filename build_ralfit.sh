#!/bin/bash

git clone https://github.com/ralna/RALFit

cd RALFit

./makebuild.sh
./makecov.sh

cd ..
