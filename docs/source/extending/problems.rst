.. _problems:

#####################
Adding Problem Groups
#####################

*This section describes how to add a problem group to the fit benchmarking
software. The default problem groups that come with this software are:
CUTEst, Muon, Neutron, NIST, SAS_modelling, and simple_tests.*

1. Add your problem file directory in
   ``fitbenchmarking/benchmark_problems/``. Some examples of how this
   should look like are available in the same dir.

2. Modify ``example_scripts/example_runScripts.py`` to run new problem
   set in ``fitbenchmarking/benchmark_problems/``.
