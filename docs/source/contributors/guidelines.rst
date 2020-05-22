.. _guidelines:

################
Coding Standards
################

All code submitted must meet certain standards, outlined below, before
it can be merged into the master branch.  It is the contributor's
job to ensure that the following is satisfied, and the reviewer's
role to check that these guidelines have been followed.

The workflow to be used for submitting new code/issues is described in
:ref:`workflow`.

=======
Linting
=======

All pull requests should be pep8 compliant.
We suggest running code through flake8 and pylint before submitting to check
for this.


=============
Documentation
=============

Any new code will be accepted only if the documentation, written in sphinx and
found in `docs/`, has been updated accordingly, and the docstrings in the code
have been updated where neccessary.


=======
Testing
=======

All tests should pass before submitting code.
Tests are written using pytest.

The following should be checked before any code is merged:

 - Function: Does the change do what it's supposed to?
 - Tests: Does it pass? Is there adequate coverage for new code?
 - Style: Is the coding style consistent? Is anything overly confusing?
 - Documentation: Is there a suitable change to documentation for this change?

=======
Logging
=======

Code should use the logging in ``utils.log``. This uses pythons built in
`logging module <https://docs.python.org/3.8/library/logging.html>`__,
and should be used in place of any print statements to ensure that persistent
logs are kept after runs.
