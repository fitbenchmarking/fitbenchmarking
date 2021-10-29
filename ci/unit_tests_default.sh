#!/bin/bash
# Test default installation
DIRS="fitbenchmarking/cli fitbenchmarking/controllers fitbenchmarking/core fitbenchmarking/cost_func fitbenchmarking/hessian fitbenchmarking/jacobian fitbenchmarking/parsing fitbenchmarking/results_processing fitbenchmarking/utils"
pytest $DIRS --cov=$DIRS --cov-report term-missing --cov-append --test-type default
status=$?

if [[ $status != 0 ]]
then
   exit 1
fi

exit 0
