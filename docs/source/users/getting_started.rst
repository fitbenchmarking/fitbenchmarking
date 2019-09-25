.. _getting-started:


Getting Started
===============

|Python 2.7| will be needed for running/installing this. Instructions
for setting up python are available
`here <https://github.com/mantidproject/fitbenchmarking/wiki/Setting-up-Python>`__.

1. Download this repository or clone it using
   `git <https://git-scm.com/>`__:
   ``git clone https://github.com/mantidproject/fitbenchmarking.git``
2. Open up a terminal (command prompt) and go into the
   ``fitbenchmarking`` directory.
3. Once you are in the right directory, type
   ``python setup.py install``.
4. Install mantid, platform specific instructions
   `here <https://github.com/mantidproject/fitbenchmarking/wiki/Installing-Mantid>`__.
5. Finally run ``fitbenchmarking/example_scripts/example_runScript.py``,
   located in the example\_scripts folder. This example script fit
   benchmarks Mantid using all the available minimizers. The result
   tables can be found in ``example_scripts/results``.

.. |Python 2.7| image:: https://img.shields.io/badge/python-2.7-blue.svg
   :target: https://www.python.org/downloads/release/python-2715/

