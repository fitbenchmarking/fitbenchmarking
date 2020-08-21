#!/bin/bash
# Test default installation
if [ -z "$1" ]
    then
        FB_DIR=fitbenchmarking
    else
        FB_DIR=$1/fitbenchmarking
fi
pytest $FB_DIR/cli --cov=fitbenchmarking/cli --cov-report term-missing
status=$?
for dir in controllers core jacobian parsing results_processing utils
do
    pytest $FB_DIR/$dir --test-type default
    status=$(($status + $?))
done
if [[ $status != 0 ]]
then
   exit 1
fi

exit 0
