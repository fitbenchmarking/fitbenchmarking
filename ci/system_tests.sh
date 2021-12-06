#!/bin/bash
# ======= System Test =============== #
pytest fitbenchmarking/systests --junit-xml full_system_test_results.xml

exit $?
