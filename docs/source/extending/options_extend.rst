.. _options_extend:

##################
Adding new Options
##################

Default options are set in :class:`~fitbenchmarking.utils.options.Options`.
These can be changed using an `.ini` formatted file
(`see here <https://docs.python.org/3/library/configparser.html#supported-ini-file-structure>`__). :ref:`options` gives examples of how this is currently implemented in
FitBenchmarking.

To add a new option to one of the five sections ``FITTING``, ``MINIMIZERS``, ``PLOTTING`` and ``LOGGING``, follow the steps below.
We'll illustrate the steps using ``<SECTION>``, which could be any of the
sections above.

1. Amend the dictionary ``DEFAULT_<SECTION>`` in :class:`~fitbenchmarking.utils.options.Options` to include any new default options.

2. If the option amended is to be checked for validity, add accepted option values to the ``VALID_<SECTION>`` dictionary in :class:`~fitbenchmarking.utils.options.Options`.

3. Using the :meth:`~fitbenchmarking.utils.options.Options.read_value` function,
   add your new option to the class, following the examples already in
   :class:`~fitbenchmarking.utils.options.Options`.  The syntax of this function is:

   .. automethod:: fitbenchmarking.utils.options.Options.read_value
		    :noindex:

4. Add tests in the following way:

    - Each of the sections has it's own test file, for example,
      ``test_option_fitting`` has tests for the ``FITTING`` section.

    - Add default tests to the class called ``<SECTION>OptionTests``.

    - Add user defined tests to the class called ``User<SECTION>OptionTests``. These
      should check that the user added option is valid and raise an ``OptionsError``
      if not.

5. Add relevant documentation for the new option in :ref:`options`.

Adding new Sections is also possible.  To do this you'll need to extend
``VALID_SECTIONS`` with the new section, and follow the same structure as the
other SECTIONS.
