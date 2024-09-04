.. _checkpointing:

################################
Checkpointing in FitBenchmarking
################################

In some cases, fitting can take a long time and rerunning the fits to change
output options is inefficient. For this situation we provide a checkpointing
file.

Using the checkpointing feature
===============================

Checkpointing in FitBenchmarking can be used to rerun the report generation
with new options, e.g. plots on, or to combine the data from multiple
fitting runs.

By default, when running FitBenchmarking it will create a ``checkpoint`` file in
the results directory which will contain all the information required to create
output tables and plots.

To generate new reports for an existing checkpoint, use the
``--load_checkpoint`` option:

.. code-block:: bash

    fitbenchmarking --load_checkpoint

This can use the same options file as in the original run but with the output
changed, or separate one as long as the results directory and checkpointing file
are the same.

There is also a separate tool for working with checkpoint files
``fitbenchmarking-cp`` that can be used to regenerate the reports or merge
checkpoint files.

.. code-block:: bash

    fitbenchmarking-cp report --help
    fitbenchmarking-cp merge --help

.. list-table:: options table for checkpointing
   :widths: 20, 10, 30, 40
   :header-rows: 1

   * - Option
     - Flags
     - Actions
     - Help
   * - *Debug mode*
     - ``-d``
     - ``--debug-mode``
     - | Enable debug mode (prints traceback).
   * - *File name*
     - ``-f``
     - ``--file-name``
     - | The path to a fitbenchmarking checkpoint file.
       | If omitted, this will be taken from the options
       | file.
   * - *Options file*
     - ``-o``
     - ``--options-file``
     - | The path to a fitbenchmarking options file
   * - *Strategy*
     - ``-s``
     - ``--strategy``
     - | The merge strategy to use when dealing with 
       | conflicts. Selecting accuracy and runtime will
       | select for the lowest conflicting runs

Warnings
========

Using ``--load_checkpoint`` will not re-run any results or run any new
combinations that have been added to the options file.

This command also does not check whether the checkpoint file has been edited
manually. Manual editing may be desired for removing data while
this feature is developed but should be done with caution to ensure results
are still comparable.

.. important::

   It is recommended that the same version of python is used to load
   the checkpoint file as was used when the file was created. Merging
   files created on the same version of python is also recommended.