#!/bin/bash
# Handle gracefully the mantid segfault issue
/opt/Mantid/bin/mantidpython -m mantid.simpleapi >file 2>/dev/null | cat
echo "first run of mantid is expected to segfault"

cd fitbenchmarking
pytest cli controllers core cost_func hessian jacobian parsing results_processing utils --cov=./ --cov-report term-missing
status=$?

if [[ $status != 0 ]]
then
   exit 1
fi

exit 0
