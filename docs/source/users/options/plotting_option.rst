.. _plotting_option:

################
Plotting Options
################

The plotting section contains options to control how results are presented.

Make plots (:code:`make_plots`)
-------------------------------

This allows the user to decide whether or not to create plots during runtime.
Toggling this to False will be much faster on large data sets.

Default is ``True`` (``yes``/``no`` can also be used)

.. code-block:: rst

    [FITTING]
    make_plots: yes

Colour scale (:code:`colour_scale`)
-----------------------------------

Lists thresholds for each colour in the html table.
In the example below, this means that values less than 1.1 will
have the top ranking (brightest) and values over 3 will show as
the worst ranking (deep red). 

Default thresholds are ``1.1, 1.33, 1.75, 3, and inf``

.. code-block:: rst

    [FITTING]
    colour_scale: 1.1, #fef0d9
                  1.33, #fdcc8a
                  1.75, #fc8d59
                  3, #e34a33
                  inf, #b30000


.. _ComparisonOption:

Comparison mode (:code:`comparison_mode`)
-----------------------------------------

This selects the mode for displaying values in the resulting table
options are ``abs``, ``rel``, ``both``:

* ``abs`` indicates that the absolute values should be displayed
* ``rel`` indicates that the values should all be relative to the best result
* ``both`` will show data in the form "abs (rel)"

Default is ``both``

.. code-block:: rst

    [FITTING]
    comparison_mode: both


Table type (:code:`table_type`)
-------------------------------

This selects the types of tables to be produced in FitBenchmarking.
Options are:

* ``acc`` indicates that the resulting table should contain the chi squared values for each of the minimizers.
* ``runtime`` indicates that the resulting table should contain the runtime values for each of the minimizers.
* ``compare`` indicates that the resulting table should contain both the chi squared value and runtime values for each of the minimizers. The tables produced have the chi squared values on the top line of the cell and the runtime on the bottom line of the cell.
* ``local_min`` indicates that the resulting table should return true if a local minimum was found, or false otherwise.  The value of :math:`\frac{|| J^T r||}{||r||}` for those parameters is also returned. The output looks like ``{bool} (norm_value)``, and the colouring is red for false and cream for true.

Default is ``acc``, ``runtime``, ``compare``, and ``local_min``.

.. code-block:: rst

    [FITTING]
    table_type: acc
                runtime
                compare
                local_min


Results directory (:code:`results_dir`)
---------------------------------------

This is used to select where the output should be saved

Default is ``results``

.. code-block:: rst

    [FITTING]
    results_dir: results
