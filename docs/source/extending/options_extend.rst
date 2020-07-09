.. _options_extend:

##################
Adding new Options
##################

The options file must be a `.ini` formatted file
(`see here <https://docs.python.org/3/library/configparser.html#supported-ini-file-structure>`__).

To add a new option to one of the four sections ``MINIMIZERS``,
``FITTING``, ``PLOTTING`` and ``LOGGING``, follow steps:

1. Add new option to the corresponding ``DEFAULTS`` dictionary in `fitbenchmarking/utils/options.py`.
2. **OPTIONAL** add accepted option values to the ``VALID`` dictionary in `fitbenchmarking/utils/options.py`.
3. Using the ``read_value`` function within the options class, add you new option
   to the class. The ``read_value`` function takes two arguments, the function
   which loads the option and the option key as defined in the ini file. See the
   options class for examples.
4. Add tests in the following way:

    - Each of the sections has it's own test file, for example, ``test_option_fitting`` has tests for the ``FITTING`` section.

    - Add default tests to class called ``{Section}OptionTests``.

    - Add user defined tests to class called ``User{Section}OptionTests``. These
      should check that the user added option is set correctly and that if
      there are accepted options an ``OptionsError`` is raised.

5. Add relevant documentation for the new option in :ref:`options`.

