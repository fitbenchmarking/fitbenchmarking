.. _getting-started:

#######################################################
Installing FitBenchmarking and default fitting packages
#######################################################

|Python 3.6+| will be needed for running/installing this.

1. Download this repository or clone it using
   `git <https://git-scm.com/>`__:
   ``git clone https://github.com/fitbenchmarking/fitbenchmarking.git``
2. Open up a terminal (command prompt) and go into the
   ``fitbenchmarking`` directory.
3. Once you are in the right directory, we recommend that you type
   
   .. code-block:: bash
		   
      pip install .['bumps','DFO','minuit','SAS']

   If this doesn't work either ``pip`` is not
   in your PATH or not installed. See `here <https://pip.pypa.io/en/stable/>`__
   for instructions to install ``pip``.

   .. note::
      
      This install will include additional optional packages -- 
      see :ref:`extra_dependencies` for details.
      Any of the dependencies in the square brackets can be omitted, if required,
      and that package will not be available for Benchmarking.
      
4. Additional software that cannot be installed via pip can also be used
   with FitBenchmarking.  Follow the instructions at :ref:`external-instructions`.

.. _extra_dependencies:

Extra dependencies
------------------

In addition to the external packages described at :ref:`external-instructions`,
some optional dependencties can be installed directly by FitBenchmarking.
These are installed by issuing the commands

.. code-block:: bash

   pip install .['option-1','option-2',...]

   
where valid strings ``option-x`` are: 

* ``bumps``-- installs the `Bumps <https://bumps.readthedocs.io>`_ fitting package.
* ``DFO`` -- installs the `DFO-LS <http://people.maths.ox.ac.uk/robertsl/dfols/userguide.html>`_ and `DFO-GN <http://people.maths.ox.ac.uk/robertsl/dfogn/userguide.html>`_ fitting packages.
* ``minuit`` -- installs the `Minuit <http://seal.web.cern.ch/seal/snapshot/work-packages/mathlibs/minuit/>`_ fitting package.
* ``SAS`` -- installs the `Sasmodels <https://github.com/SasView/sasmodels>`_ fitting package.


.. |Python 3.6+| image:: https://img.shields.io/badge/python-3.6+-blue.svg
   :alt: Python 3.6+
   :target: https://www.python.org/downloads/


