#!/bin/bash
# Handle gracefully the mantid segfault issue
/opt/Mantid/bin/mantidpython -m mantid.simpleapi >file 2>/dev/null | cat
echo "first run of mantid is expected to segfault"

DIRS="fitbenchmarking/cli fitbenchmarking/controllers fitbenchmarking/core fitbenchmarking/cost_func fitbenchmarking/hessian fitbenchmarking/jacobian fitbenchmarking/parsing fitbenchmarking/results_processing fitbenchmarking/utils"
pytest $DIRS --cov=$DIRS --cov-report term-missing
status=$?

if [[ $status != 0 ]]
then
   exit 1
fi

exit 0
