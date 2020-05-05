#!/bin/bash
# Test one dir to ogenerate the coverage file
pytest fitbenchmarking/cli --cov=fitbenchmarking/cli --cov-report term-missing
status=$?
# Loop over other dirs to append to the coverage file
for dir in controllers core jacobian parsing results_processing utils
do
    pytest fitbenchmarking/$dir --cov=fitbenchmarking/$dir --cov-report term-missing --cov-append
    status=$(($status + $?))
done

if [[ $status != 0 ]]
then
   exit 1
fi

exit 0
