#!/bin/bash

status=0

for dir in cli controllers core cost_func jacobian parsing results_processing utils
do 
    pylint -r y fitbenchmarking/$dir/* --exit-zero
    status=$(($status + $?))
    flake8 fitbenchmarking/$dir/*
    status=$(($status + $?))
done

if [[ $status != 0 ]]
then
   exit 1
fi

exit 0