#!/bin/bash
# Test default installation
pytest fitbenchmarking/cli --cov=fitbenchmarking/cli --cov-report term-missing
for dir in controllers core jacobian parsing results_processing utils
do
    pytest fitbenchmarking/$dir --test-type default
done
