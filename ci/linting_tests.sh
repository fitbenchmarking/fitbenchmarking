#!/bin/bash

pylint fitbenchmarking || pylint-exit $? --error-fail --warn-fail --refactor-fail --convention-fail
status=$?

flake8 fitbenchmarking
status=$(($status + $?))

if [[ $status != 0 ]]
then
   exit 1
fi

exit 0