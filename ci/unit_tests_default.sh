#!/bin/bash
# Test default installation
DIRS="cli controllers core cost_func hessian jacobian parsing results_processing utils"
for d in $DIRS; do FULL_DIRS="$FULL_DIRS fitbenchmarking/$d"; done
for d in $FULL_DIRS; do COV_ARGS="$COV_ARGS --cov=$d"; done
pytest $FULL_DIRS $COV_ARGS --cov-report term-missing --test-type default --junit-xml test-results/default_unit_pytest.xml --durations=0
status=$?

if [[ $status != 0 ]]
then
   exit 1
fi

exit 0
