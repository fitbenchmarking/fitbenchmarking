#!/bin/bash

pylint -r y fitbenchmarking/parsing/* --exit-zero
status=$?
flake8 fitbenchmarking/parsing/*
status=$(($status + $?))

if [[ $status != 0 ]]
then
   exit 1
fi

exit 0