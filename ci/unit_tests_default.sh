#!/bin/bash
# Test default installation
cd fitbenchmarking
pytest cli controllers core cost_func hessian jacobian parsing results_processing utils --cov=./ --cov-report term-missing --test-type default
status=$?

if [[ $status != 0 ]]
then
   exit 1
fi

exit 0
