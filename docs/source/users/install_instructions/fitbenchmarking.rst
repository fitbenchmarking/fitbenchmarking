.. _getting-started:

#######################################################
Installing FitBenchmarking and default fitting packages
#######################################################

We recommend using |Python 3.6+| for running/installing Fitbenchmarking.
The easiest way to install FitBenchmarking is by using the Python package manager,
`pip <https://pip.pypa.io/en/stable/>`__.


Installing via ``pip``
----------------------

FitBenchmarking can be installed via the command line by entering:

.. code-block:: bash

      python -m pip install fitbenchmarking[bumps,DFO,minuit,SAS]


This will install the latest stable version of FitBenchmarking.
For all available versions please visit the FitBenchamarking
`PyPI project <https://pypi.org/project/fitbenchmarking/>`__.
FitBenchmarking can also use additional software that cannot be installed
using pip; please see :ref:`external-instructions` for details.

.. note::

    This install will include additional optional packages --
    see :ref:`extra_dependencies`.
    Any of the dependencies in the square brackets can be omitted, if required,
    and that package will not be available for Benchmarking, or will use the
    version of the package already on your system, if appropriate.

Installing from source
----------------------

You may instead wish to install from source, e.g., to get the very latest version
of the code that is still in development.

1. Download this repository or clone it using
   `git <https://git-scm.com/>`__:
   ``git clone https://github.com/fitbenchmarking/fitbenchmarking.git``
2. Open up a terminal (command prompt) and go into the
   ``fitbenchmarking`` directory.
3. Once you are in the right directory, we recommend that you type

   .. code-block:: bash

      python -m pip install .[bumps,DFO,minuit,SAS]

4. Additional software that cannot be installed via pip can also be used
   with FitBenchmarking.  Follow the instructions at
   :ref:`external-instructions`.

.. _extra_dependencies:

Extra dependencies
------------------

In addition to the external packages described at :ref:`external-instructions`,
some optional dependencies can be installed directly by FitBenchmarking.
These are installed by issuing the commands

.. code-block:: bash

   python -m pip install fitbenchmarking['option-1','option-2',...]

or

.. code-block:: bash

   python -m pip install .['option-1','option-2',...]

where valid strings ``option-x`` are:

* ``bumps``-- installs the `Bumps <https://bumps.readthedocs.io>`_ fitting package.
* ``DFO`` -- installs the `DFO-LS <http://people.maths.ox.ac.uk/robertsl/dfols/userguide.html>`_ and `DFO-GN <http://people.maths.ox.ac.uk/robertsl/dfogn/userguide.html>`_ fitting packages.
* ``minuit`` -- installs the `Minuit <http://seal.web.cern.ch/seal/snapshot/work-packages/mathlibs/minuit/>`_ fitting package.
* ``SAS`` -- installs the `Sasmodels <https://github.com/SasView/sasmodels>`_ fitting package.


.. |Python 3.6+| image:: https://img.shields.io/badge/python-3.6+-blue.svg
   :alt: Python 3.6+
   :target: https://www.python.org/downloads/


