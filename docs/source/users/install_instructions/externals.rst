.. _external-instructions:

############################
Installing External Software
############################

Fitbenchmarking will install all packages that are available through pip.

To enable Fitbenchmarking with the other supported software,
they need to be installed and available on your machine.  We give
pointers outlining how to do this below, and you can find install scripts
for Ubuntu 18.04 in the directory `/build/<software>/`

Ceres Solver
------------

Ceres Solver is used as a fitting software in FitBenchmarking, and is called via the
PyCeres interface.

Install instructions can be found on the `PyCeres Github page <https://github.com/Edwinem/ceres_python_bindings#recommended-build-alongside-ceres>`__ and `
Ceres Solver documentation <http://ceres-solver.org/installation.html>`__ 

Please note that the ``PYCERES_LOCATION`` environment variable must be set.

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

Note: pyGSL may not be installable with the latest versions of pip. We have found that 20.0.2 works for our tests.

Horace
------

Horace can be installed by following the instructions `on the Horace
website <https://pace-neutrons.github.io/Horace/3.6.0/Download_and_setup.html>`__.
In addition, MATLAB and the MATLAB engine must be installed following the
:ref:`instructions given below<matlab-install>`.


Mantid
------

Mantid is used both as fitting software, and to parse data files.

Instructions on how to install Mantid for a range of systems are available
at `<https://download.mantidproject.org/>`_.

.. _matlab-install:

MATLAB
------

MATLAB is available to use as fitting software in FitBenchmarking, and is
called via the MATLAB Engine API for Python.

To use this fitting software, both MATLAB and the MATLAB engine must be
installed. Installation instructions for MATLAB are available at
`<https://uk.mathworks.com/help/install/ug/install-products-with-internet-connection.html>`_,
and instructions for installing and setting up the MATLAB engine are
here: `<https://uk.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html>`_

RALFit
------

RALFit is available to use as fitting software.

Instructions on how to build the python interface are at `<https://ralfit.readthedocs.io/projects/Python/en/latest/install.html>`_

