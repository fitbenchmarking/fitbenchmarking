#!/bin/bash
# ======= System Test =============== #
pytest fitbenchmarking/systests --test-type default --junit-xml default_system_test_results.xml

exit $?
