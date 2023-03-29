.. _checkpointing:

################################
Checkpointing in FitBenchmarking
################################

In some cases, fitting can take a long time and rerunning the fits to change
output options is inefficient. For this situation we provide a checkpointing
file.

Using the checkpointing feature
===============================

As indicated above this feature is currently only for rendering changes to
the presentation of runs although we plan to extend it to combining and
filtering runs in the future.

By default, when running FitBenchmarking it will create a ``checkpoint`` file in
the results directory which will contain all the information required to create
output tables and plots. 

To generate new reports for an existing checkpoint, use the
``--load_checkpoint`` option:

.. code-block:: bash

    fitbenchmarking --load_checkpoint

This can use the same options file as in the original run but with the output
changed, or seperate one as long as the results directory and checkpointing file
are the same.

There is also a seperate tool for working with checkpoint files
``fitbenchmarking-cp`` that can be used to regenerate the reports.

.. code-block:: bash

    fitbenchmarking-cp report --help


Warnings
========

Using ``--load_checkpoint`` will not re-run any results or run any new
combinations that have been added to the options file.

This command also does not check that the checkpoint file has not been edited
manually. Manual editing may be desired for removing or combining data while
these features are developed but should be done with caution to ensure results
are still comparable.
