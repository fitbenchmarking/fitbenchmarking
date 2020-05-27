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
3. Once you are in the right directory, type
   ``pip install .``. If this doesn't work either ``pip`` is not
   in your PATH or not installed. See `here <https://pip.pypa.io/en/stable/>`__
   for instructions to install ``pip``.
4. Install any additional softwares you wish to benchmark.
   See :ref:`external-instructions` for more information on this.

Default fitting packages
------------------------

The following fitting packages are installed as a default with FitBenchmarking:

1. `Bumps <https://bumps.readthedocs.io>`_
2. `DFO-LS <http://people.maths.ox.ac.uk/robertsl/dfols/userguide.html>`_
3. `DFO-GN <http://people.maths.ox.ac.uk/robertsl/dfogn/userguide.html>`_
4. `Minuit <http://seal.web.cern.ch/seal/snapshot/work-packages/mathlibs/minuit/>`_
5.  Scipy `minimize <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html>`_
6. Scipy `least_squares <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html>`_



.. |Python 3.6+| image:: https://img.shields.io/badge/python-3.6+-blue.svg
   :alt: Python 3.6+
   :target: https://www.python.org/downloads/


