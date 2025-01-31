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
pyceres interface.

Install instructions can be found on the `pyceres <https://github.com/cvg/pyceres#installation>`__ Github page and 
`Ceres Solver documentation <http://ceres-solver.org/installation.html>`__ 


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
website <https://pace-neutrons.github.io/Horace/v4.0.0/introduction/Download_and_setup.html>`__.
In addition, MATLAB and the MATLAB engine must be installed following the
:ref:`instructions given below<matlab-install>`.

SpinW
-----

SpinW can be installed by following the instructions `on the SpinW website
<https://spinw.org/IntroToSpinW/#/install1>`__. In addition, MATLAB and the MATLAB
engine must be installed following the :ref:`instructions given below<matlab-install>`.

.. _levmar-install:

Levmar
------

Levmar is available on pip, however the latest release will only work up to Python 3.8.
The python interface to levmar is unmaintained and no longer easy to install on the latest versions of python.
The bindings may be installable from the `github repo <https://github.com/bjodah/levmar>`__ though
we have not tested them on python >= 3.12.


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
here: `<https://uk.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html>`_.

There are a couple of different ways to install Matlab through WSL in a Linux environment. One of these involves using 
X11 Forwarding, through a server like VcXsrv. This is an X server for Windows, which enables users to run graphical apps 
from a Linux environment on a Windows  machine. Once installed, one needs to start XLaunch, click "Next" till the window 
"Extra settings", where the last box needs to be ticked for VcXsrv to function correctly. X11Forwarding can be tested by 
running "xeyes" from the WSL Linux environment, which should cause a pop-up with a pair of eyes to appear. For "xeyes" to 
work, the environment variable called "DISPLAY" must have a value, which can be set by running, e.g., "export DISPLAY=:0". 
This could be added to ~./bashrc to avoid repeating every time a terminal is started. It might also be necessary to set 
the environment variable LIBGL_ALWAYS_INDIRECT to 1. If "xeyes" does not work at this point, one should check the inbound 
rules for VcXsrv, by navigating to 
Control Panel > System and Security > Defender Firewall > Advanced settings > Inbound rules. Here, there should be 
two rules with the name "VcXsrv windows server" marked as Public. If these have red stop signs next to them, one should
double click on them and "allow" the connection. This operation requires admin rights on the machine. 
Once all this has been done, running "xeyes" should work and open the pop-up. 

Having configured the X 11Forwarding, this can be used for installing Matlab. For this, one should follow the instructions 
in `<https://uk.mathworks.com/help/install/ug/install-products-with-internet-connection.html>`_, making sure that the 
version of Matlab being downloaded is compatible with the Python version being used. The following page might help with 
that: `<https://uk.mathworks.com/support/requirements/python-compatibility.html>`_. 

After running "sudo ./install" from the Matlab folder (as suggested in the Mathworks instructions), the graphical interface 
will open. Here, the user is asked to select suitable folder for the MATLAB installation. Let's call this path "matlabroot". 
In the last window, before the installation starts, there should be a question on whether to create symbolic links and where. 
That box should be ticked, and the path provided there should correspond to the previously selected "matlabroot".
Finally, the path "<matlabroot>/bin/glnxa64" should be added to LD_LIBRARY_PATH, and the path "<matlabroot>/bin" should be 
added to both PATH and PYTHONPATH.

Having installed matlab, to use it within Fitbenchmarking, it is necessary to install the MATLAB engine, as previously 
mentioned. Furthermore, Matlab requires additional Python packages to be installed. You can find the instructions on how 
to install these packages by following the link provided: :ref:`here <extra_dependencies>`.

RALFit
------

RALFit is available to use as fitting software.

Instructions on how to build the python interface are at `<https://ralfit.readthedocs.io/projects/Python/en/latest/install.html>`_

Theseus
-------

Theseus is used as a fitting software in FitBenchmarking, and is called via theseus-ai python
module which requries pytorch

Install instructions can be found on the `Theseus Github page <https://github.com/facebookresearch/theseus#getting-started/>`__
