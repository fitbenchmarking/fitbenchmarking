This folder contains problem definition files each defining a
fit benchmarking problem that minimizers can be benchmarked against.

More specifically a folder or sub-folder of this directory contain a problem set.

Two problem definition file formats are supported:

* The format native to FitBenchmarking (denoted FitBenchmark). For example, see the neutron_data folder.
* NIST Noninear Regression [format](https://www.itl.nist.gov/div898/strd/nls/data/LINKS/DATA/Misra1a.dat). For example, see the NIST folder.

All FitBenchmark data files are recommended be stored under a folder named `data_files` inside their corresponding problem folders (e.g. `Muon_data`, `Neutron_data`, etc.)
