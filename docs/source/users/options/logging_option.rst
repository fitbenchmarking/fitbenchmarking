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

This toggles whether the output grabber collects the third party
output. We note that for the Windows operating system this
option is not available.

Default is ``True`` (``yes``/``no`` can also be used)

.. code-block:: rst

    [LOGGING]
    append: yes
