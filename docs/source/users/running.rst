.. _running:

#######################
Running FitBenchmarking
#######################

Once installed, issuing the command

.. code-block:: bash

   fitbenchmarking

will run the NIST test example on SciPy minmizers.

Running alternative problems
----------------------------

Other problems written in a :ref:`supported file format <problem_def>`
can be analyzed with FitBenchmarking by
passing the path using the ``--problem-sets`` (or ``-p``) option.
A example problems can be downloaded from
:ref:`BenchmarkProblems`, and they can also be found in the
``fitbenchmarking/examples`` directory of the code.

For example, to run the NIST low difficulty set from the base directory
of the source, type into the terminal:

.. code-block:: bash
		
   fitbenchmarking -p examples/benchmark_problems/NIST/low_difficulty

Changing the options
--------------------
   
An options file can also be passed with the ``-o`` argument.  For example,
the template file can be run by issuing the command

.. code-block:: bash

   fitbenchmarking -o examples/options_template.ini \
   -p examples/benchmark_problems/NIST/low_difficulty

Details about how the options file must be formatted are given in :ref:`options`.

Running ``fitbenchmarking -h`` will give more guidance about available commands,
including examples of how to run multiple problem sets.
