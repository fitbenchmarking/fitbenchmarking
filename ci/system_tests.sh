#!/bin/bash
# ======= System Test =============== #
pytest fitbenchmarking/systests --junit-xml test-results/full_system_test_results.xml

exit $?
