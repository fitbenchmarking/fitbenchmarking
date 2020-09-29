.. _external-instructions:

############################
Installing External Software
############################

Fitbenchmarking will install all packages that are available through pip.

To enable Fitbenchmarking with the other supported software,
they need to be installed and available on your machine.  We give
pointers outlining how to do this below, and you can find install scripts
for Ubuntu 18.04 in the directory `/build/<software>/`

CUTEst
------

CUTEst is used to parse SIF files in FitBenchmarking, and is called via the
PyCUTEst interface.

Currently this is only supported for Mac and Linux, and can be installed by
following the instructions outlined on the `pycutest documentation <https://jfowkes.github.io/pycutest/_build/html/install.html>`_

Please note that the ``PYCUTEST_CACHE`` environment variable must be set, and it must be
in the ``PYTHONPATH``.

GSL
---

GSL is used as a fitting software in FitBenchmarking, and is called via the
pyGSL interface.

Install instructions can be found at the `pyGSL docs <http://pygsl.sourceforge.net/>`__.
This package is also installable via pip, provided GSL is available on your system;
see our example build script in `build/gsl`.

Mantid
------

Mantid is used both as fitting software, and to parse data files.

Instructions on how to install Mantid for range of systems are available
at `<https://download.mantidproject.org/>`_.  

RALFit
------

RALFit is availble to use as fitting software.

Instructions on how to build the python interface are at `<https://ralfit.readthedocs.io/projects/Python/en/latest/install.html>`_

