This folder contains problem definition files each defining a
fit benchmarking problem that minimizers can be benchmarked against.

More specifically a folder or sub-folder of this directory contain a problem set.

See https://fitbenchmarking.readthedocs.io and section on Problem Definition Files
for the formats supported.

A data file name specified within a definition file is recommended to be stored in a sub-folder named `data_files` relative to the location of the definition file.

Examples of Problem Definition folders include (please note this list is stadily changes and hence below may get out of sync from time to time):

* SAS_modelling : fitting problems specific relevant to fitting SAS (Small Angle Scattering) data
* Muon : generic fitting problems relevant to fitting Muon data collected at a Muon facility such as ISIS Neutron and Muon Facility
* Neutron : generic fitting problems relevant to fitting Neutron data collected at a Neutron facility such as ISIS Neutron and Muon Facility
* NIST : set of made up fitting problem (not against measured data with error bars) as described [here](https://www.itl.nist.gov/div898/strd/nls/nls_main.shtml)
* CUTEes : fitting problems relevant to this tool included in [CUTEet](http://epubs.stfc.ac.uk/bitstream/9327/RAL-TR-2013-005.pdf)

