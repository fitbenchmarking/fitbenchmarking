.. _running:

#######################
Running FitBenchmarking
#######################

Once installed, issuing the command

.. code-block:: bash

   fitbenchmarking

will run the NIST average difficulty problem set on SciPy minmizers.

By default, fitbenchmarking will start a Dash app in order to provide more
interactive plots. The Dash app will keep running after fitbenchmarking
has finished, unless it is stopped by the user. If the app is stopped,
the more interactive plots will not be available.

Running alternative problems
----------------------------

Other problems written in a :ref:`supported file format <problem_def>`
can be analyzed with FitBenchmarking by
passing the path using the ``-p`` or ``--problem-sets`` argument.
Example problems can be downloaded from
:ref:`BenchmarkProblems`, and they can also be found in the
``fitbenchmarking/examples`` directory of the code.

For example, to run the NIST low difficulty set from the base directory
of the source, type into the terminal:

.. code-block:: bash

   fitbenchmarking -p examples/benchmark_problems/NIST/low_difficulty

Changing the options
--------------------

An options file can also be passed with the ``-o`` or ``--options-file`` argument.
For example, the template file can be run by issuing the command

.. code-block:: bash

   fitbenchmarking -o examples/options_template.ini \
   -p examples/benchmark_problems/NIST/low_difficulty

Details about how the options file must be formatted are given in :ref:`options`.

.. _change_results_directory:


Changing options via the command line
------------------------------

It is possible to change the following options via the command line rather than from an ``.ini`` file or from the default options.
They can be changed using the arguments in the table below.

.. list-table:: options table for fitbenchmarking
   :widths: 20, 10, 40, 30
   :header-rows: 1

   * - Option
     - Flags
     - Actions (string description)
     - Help
   * - *Options file*
     - ``-o``
     - ``--options-file``
     - | The path to a %(prog)s options
       | file.
   * - *Problem sets*
     - ``-p``
     - ``--problem_sets``
     - | Paths to directories containing
       | problem sets.
   * - *Results directory*
     - ``-r``
     - ``--results_dir``
     - | The directory to store resulting
       | files in.
   * - *Debug mode*
     - ``-d``
     - ``--debug-mode``
     - | Enable debug mode (prints traceback).
   * - *Number of runs*
     - ``-n``
     - ``--num_runs``
     - | Set the number of runs to average.
   * - *Algorithm type*
     - ``-a``
     - ``--algorithm_type``
     - | Select what type of algorithm is
       | used within a specific software.
   * - *Software*
     - ``-s``
     - ``--software``
     - | Select the fitting software to benchmark.
   * - *Jacobian method*
     - ``-j``
     - ``--jac_method``
     - | Set the Jacobian to be used.
   * - *Cost function type*
     - ``-c``
     - ``--cost_func_type``
     - | Set the cost functions to be used.
   * - *Make plots*
     -
     - ``--make_plots``
     - | Use this option if you have decided
       | to create plots during runtime.
   * - *Don't make plots*
     -
     - ``--don't_make_plots``
     - | Use this option if you have decided
       | not to create plots during runtime.
   * - *Open results browser*
     -
     - ``--results_browser``
     - | Use this option if you have decided
       | to open a browser window to show the
       | results of a fit benchmark.
   * - *Don't open results browser*
     -
     - ``--no_results_browser``
     - | Use this option if you have decided
       | not to open a browser window to show
       | the results of a fit benchmark.
   * - *Show progress bar*
     -
     - ``--pbar``
     - | Use this option if you would like
       | to see the progress bar during runtime.
   * - *Don’t show progress bar*
     -
     - ``--no_pbar``
     - | Use this option if you do not want to
       | see the progress bar during runtime.
   * - *Comparison mode*
     - ``-m``
     - ``--comparison_mode``
     - | Select the mode for displaying values
       | in the resulting table.
   * - *Table type*
     - ``-t``
     - ``--table_type``
     - | Select the type of table to be produced
       | in Fitbenchmarking.
   * - *Logging file name*
     - ``-f``
     - ``--logging_file_name``
     - | Specify the file path to write the logs to.
   * - *Append log*
     -
     - ``--append_log``
     - | Use this option if you have decided to log
       | in append mode. If append mode is active,
       | the log file will be extended with each
       | subsequent run.
   * - *Overwrite log*
     -
     - ``--overwrite_log``
     - | Use this option if you have decided not to
       | log in append mode. If append mode is not
       | active, the log will be cleared after each
       | run.
   * - *Level of logging*
     - ``-l``
     - ``--level``
     - | Specify the minimum level of logging to
       | display on console during runtime.
   * - *External output*
     - ``-e``
     - ``--external_output``
     - | Select the amount of information
       | displayed from third-parties.
   * - *Runtime metric*
     - ``-rt``
     - ``--runtime_metric``
     - | Set the metric for the runtime.
   * - *Dash port*
     -
     - ``--port``
     - | Set the port for Dash app.
   * - *Run Dash app*
     -
     - ``--run_dash``
     - | Use this option if you have decided
       | to run the Dash app.
   * - *Don't run Dash app*
     -
     - ``--dont_run_dash``
     - | Use this option if you have decided
       | not to run the Dash app.

**For example, to change the results directory:**

The default directory where the results are saved can be changed using the ``-r``
or ``--results-dir`` argument. The :ref:`results directory option <results_directory_option>`
can also be changed in the options file.

.. code-block:: bash

   fitbenchmarking -r new_results/

The default results directory is ``fitbenchmarking_results``.

**Multiple options**

For an option for which you wish to make several choices e.g. ``table_type``, simply use a space to separate your choices:

.. code-block:: bash

   fitbenchmarking -t acc runtime

If you wish to change several different options, use a space to separate the arguments:

.. code-block:: bash

   fitbenchmarking -t acc -l WARNING

**Help**

For more information on changing options via the command line, you can use the ``-h``
or ``--help`` argument.

.. code-block:: bash

   fitbenchmarking -h
