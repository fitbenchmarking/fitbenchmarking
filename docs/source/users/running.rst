.. _running:

#######################
Running FitBenchmarking
#######################

A set of example problems can be found the ``fitbenchmarking/examples``
directory along with a template for passing in options.

To run with any of these problem sets, you should pass the path to the
``fitbenchmarking`` command.  For example, to run the NIST low difficulty
set, type into the terminal:

.. code-block:: bash
		
   fitbenchmarking examples/benchmark_problems/NIST/low_difficulty

An options file can also be passed with the ``-o`` argument.  For example,
the template file can be run by issuing the command

.. code-block:: bash

   fitbenchmarking -o examples/options_template.ini \
   examples/benchmark_problems/NIST/low_difficulty

Details about how the options file must be formatted are given in :ref:`options`.

Running ``fitbenchmarking -h`` will give more guidance about available commands,
including examples of how to run multiple problem sets.
