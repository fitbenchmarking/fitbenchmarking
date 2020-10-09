.. _tests:

#####################
FitBenchmarking Tests
#####################

The tests for FitBenchmarking require ``pytest>=3.6``. We have split the tests into two categories:

* ``default``: denotes tests involving ``pip`` installable :ref:`software packages<getting-started>`,
* ``all``: in addition to ``default``, also runs tests on :ref:`external packages <external-instructions>`.

Unit tests
----------

Each module directory in FitBenchmarking (e.g. ``controllers``) contains a test folder which has the ``unit`` tests for that module. One can run the tests for a module by:

.. code-block:: bash

   pytest fitbenchmarking/<MODULE_DIR> --test-type <TEST_TYPE>

where <TEST_TYPE> is either ``default`` or ``all``. If ``--test-type`` argument is not given the default is ``all``

System tests
------------

System tests can be found in the ``systests`` directory in FitBenchmarking. As with the unit tests, these can be run via:

.. code-block:: bash

   pytest fitbenchmarking/systests --test-type <TEST_TYPE>


.. warning::
   The files in the expected results subdirectory of the ``systests`` directory are generated to check consistency in our automated tests via `Travis CI <https://travis-ci.org/>`__.  They might not pass on your local operating system due to, for example, different software package versions being installed.

Travis CI tests
---------------

The scripts that are used our automated tests via `Travis CI <https://travis-ci.org/>`__ are located in the ``travis`` folder. These give an example of how to run both the unit and system tests within FitBenchmarking.
