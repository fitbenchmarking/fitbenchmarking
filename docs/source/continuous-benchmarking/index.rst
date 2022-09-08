#######################
Continuous Benchmarking
#######################

FitBenchmarking is run every month on all software we support, and the
results are published at https://www.fitbenchmarking.com
We invite developers of the fitting software we test to submit changes to the
way the software is called and/or installed.

All tests are run on virtual machines that are running Ubuntu 20.04:

.. csv-table:: Virtual Machines
	       :header: "Machine", "CPUs", "RAM"

   "fitbenchmarking-tiny", "2", "2GB"
   "fitbencharmking-medium", "4", "8GB"
   
These machines are rebuilt before each test.  The VM `fitbenchmarking-orch`
orchestrates the testing process, and contains the scripts used to setup
the VMs and start the tests.

The external softare packages are build using the script
`fitbenchmarking/build/build-scripts.sh`,
which should be run using  `source` from the home directory of the machine.
Once this has been run, the script `fitbenchmarking/build/set-environment.sh`
can be used to set the required environment variables for future sessions, if
needed.








