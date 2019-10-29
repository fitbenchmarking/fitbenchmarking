.. _logging:

Logging
=======

Logging is the process of tracking certain events that occur when the
software is running. FitBenchmaring uses the logging tool included in
the Python standard library. Logging calls can be included in different
parts of the code to indicate the occurance of interested events. Such
events could be categorised into different levels depending on their
types. For instance, events that occur during the normal opertation of a
program are considered to be level “INFO” while software errors are of
level “ERROR”. Logging is done in a form of a text message that could
contain the timestamp and/or level of each event.

The benefit of the logging API is that all modules in Python can
contribute to the logging. In other words, it means that your
software/application log can include its own log messages as well as log
messages from any external or third-party modules.

Python Logging Documentation and Tutorials
------------------------------------------

The URL below leads to the official Python website that contains
detailed descriptions and available commands for logging, in addition to
useful tutorials on how to perform logging:

https://docs.python.org/2/library/logging.html#logrecord-attributes

Be aware of this
----------------

-  Logging can increase the runtime of the program significantly. It is
   best to avoid using it in large and nested loops
-  Log messages can be sent to multiple destinations. Some destinations
   are dedicated to the software developers while some are for users. It
   is important to set the level for each destination as some
   destination might not require low-level log messages. More
   information on this can be found
   `here <https://docs.python.org/3/howto/logging-cookbook.html#logging-to-multiple-destinations>`__.
