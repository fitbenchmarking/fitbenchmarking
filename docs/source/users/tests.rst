.. _tests:

#####################
FitBenchmarking tests
#####################

To run both the ``unit`` and ``system`` tests for FitBenchmarking you will need to install ``pytest>=3.6``. We have split the tests into two categories:

* ``default``: denotes all tests that use ``pip`` installable :ref:`software packages<getting-started>`,
* ``all``: denotes all test.

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
   The expected results directory in the ``systests`` directory are generated to check consistency in our automated tests via `Travis CI <https://travis-ci.org/>`__. This is done by checking the text output of the tables are consistent, and therefore, they might not pass on your specific operating system due to, for example, different software package versions.

Travis CI tests
---------------

The scripts that are used our automated tests via `Travis CI <https://travis-ci.org/>`__ are located in the ``travis`` folder. These give an example of how to run both the unit and system tests within FitBenchmarking.
