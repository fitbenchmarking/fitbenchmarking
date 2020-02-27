#!/bin/bash
# Test one dir to ogenerate the coverage file
pytest fitbenchmarking/cli --cov=fitbenchmarking/cli --cov-report term-missing
# Loop over other dirs to append to the coverage file
for dir in controllers core parsing results_processing utils
do
    pytest fitbenchmarking/$dir --cov=fitbenchmarking/$dir --cov-report term-missing --cov-append
done
