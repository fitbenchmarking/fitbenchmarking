#!/bin/bash
# ======= System Test =============== #
pytest fitbenchmarking/systests --test-type mantid --junit-xml test-results/full_system_pytest.xml --durations=0

exit $?