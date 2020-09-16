#!/bin/bash
# Test default installation
pytest fitbenchmarking/cli --cov=fitbenchmarking/cli --cov-report term-missing
status=$?
for dir in controllers core jacobian parsing results_processing utils
do
    pytest fitbenchmarking/$dir --test-type default
    status=$(($status + $?))
done
if [[ $status != 0 ]]
then
   exit 1
fi

exit 0
