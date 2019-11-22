.. _options:

#######################
FitBenchmarking Options
#######################

FitBenchmarking is controlled by a set of options that can be controlled in
3 different ways.
In order from lowest priority to highest these are:

- The default options.
- An options file.
- Options set in a script.

The default options are a complete set of options with sensible values.
These will be used when no other values are given for any of the options,
the values for these can be seen at the end of this document.

The options file must be a `.ini` file, and a good reference for this can be
found in the examples, as well as at the bottom of this document.


.. prettyprintvalue::
   :module: fitbenchmarking.utils.options
   :class: Options
   :var: DEFAULTS

