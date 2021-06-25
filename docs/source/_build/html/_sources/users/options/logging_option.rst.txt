.. _logging_option:

###############
Logging Options
###############

The logging section contains options to control how fitbenchmarking logs
information.

Logging file name (:code:`file_name`)
-------------------------------------

This specifies the file path to write the logs to.

Default is ``fitbenchmarking.log``

.. code-block:: rst

    [LOGGING]
    file_name: fitbenchmarking.log

Logging append (:code:`append`)
-------------------------------

This specifies whether to log in append mode or not.
If append mode is active, the log file will be extended with each subsequent
run, otherwise the log will be cleared after each run.

Default is ``False`` (``yes``/``no`` can also be used)

.. code-block:: rst

    [LOGGING]
    append: no


Logging level (:code:`level`)
-----------------------------------------

This specifies the minimum level of logging to display on console during
runtime.
Options are (from most logging to least):

* ``NOTSET``
* ``DEBUG``
* ``INFO``
* ``WARNING``
* ``ERROR``
* ``CRITICAL``

Default is ``INFO``

.. code-block:: rst

    [LOGGING]
    level: INFO

Logging external output (:code:`external_output`)
-------------------------------------------------

This selects the amount of information displayed from third-parties.
There are 3 options:

* ``display``: Print information from third-parties to the stdout stream
               during a run.
* ``log_only``: Print information to the log file but not the stdout stream.
* ``debug``: Do not intercept third-party use of output streams.

Default is ``log_only``

.. code-block:: rst

    [LOGGING]
    append: log_only
