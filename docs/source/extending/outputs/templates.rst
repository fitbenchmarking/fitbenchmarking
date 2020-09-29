.. _templates:

##################
HTML/CSS Templates
##################

In FitBenchmarking, templates are used to generate all html output files,
and can be found in the `fitbenchmarking/templates` directory.

==============
HTML Templates
==============
HTML templates allow for easily adaptable outputs.
In the simple case of rearranging the page or making static changes
(changes that don't vary with results), this can be done by editing the
template, and it will appear in every subsequent HTML page.

For more complicated changes such as adding information that is page dependent,
we use `jinja <https://jinja.palletsprojects.com/en/2.11.x/>`__.
Jinja allows code to be added to templates which can contain conditional
blocks, replicated blocks, or substutions for values from python.

Changes to what information is displayed in the page will usually involve
editing the python source code to ensure you pass the approprate values to
jinja. In practice the amount of effort required to do this can range from
one line of code to many depending on the object to be added.

=============
CSS Templates
=============
The CSS files contained in the `templates` directory are used to format the
HTML pages.

If you wish to change the style of the output results
(e.g. to match a website), this is where they can be changed.
