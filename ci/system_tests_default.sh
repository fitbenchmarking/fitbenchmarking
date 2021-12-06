#!/bin/bash
# ======= System Test =============== #
pytest fitbenchmarking/systests --test-type default --junit-xml test-results/default_system_pytest.xml

exit $?
