.. _guidelines:

######################
Contributor Guidelines
######################

=======
Linting
=======

All pull requests should be pep8 compliant.
We suggest running code through flake8 and pylint before submitting to check
for this.


=============
Documentation
=============

Any new code will be accepted only if there is relevent documentation for it in
the corresponding pull request.

===
Git
===

Branches should be created from master, and by convention follow the pattern
"nnn_description" where nnn is the issue number.

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
