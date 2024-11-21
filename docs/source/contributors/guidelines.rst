.. _guidelines:

################
Coding Standards
################

All code submitted must meet certain standards, outlined below, before
it can be merged into the master branch.  It is the contributor's
job to ensure that the following is satisfied, and the reviewer's
role to check that these guidelines have been followed.
The contributor may wish to make use of git pre-commits to help adhere to
these guidelines. Instructions for using pre-commit are at the bottom of this
document.

The workflow to be used for submitting new code/issues is described in
:ref:`workflow`.

=======
Linting
=======

All pull requests should be compliant with selected `ruff <https://docs.astral.sh/ruff/>`_ rules.
We suggest running code through ruff using the precommit hook before pushing code to github.


=============
Documentation
=============

Any new code will be accepted only if the documentation, written in
`sphinx <https://www.sphinx-doc.org/en/master/>`_ and found in `docs/`,
has been updated accordingly, and the docstrings in the code
have been updated where necessary.

=======
Testing
=======

All tests should pass before submitting code.
Tests are written using `pytest <https://docs.pytest.org/en/stable/>`_.

The following should be checked before any code is merged:

 - Function: Does the change do what it's supposed to?
 - Tests: Does it pass? Is there adequate coverage for new code?
 - Style: Is the coding style consistent? Is anything overly confusing?
 - Documentation: Is there a suitable change to documentation for this change?

=======
Logging
=======

Code should use the logging in ``utils.log``. This uses Python's built in
`logging module <https://docs.python.org/3.12/library/logging.html>`__,
and should be used in place of any print statements to ensure that persistent
logs are kept after runs.

==========
Pre-commit
==========

Pre-commit runs checks at the point of committing code to ensure simple
problems are spotted before running the CI.
This covers sorting imports, fixing indentation, removing trailing whitespace,
and checking the linting.

Pre-commit will be installed as part of Step 4 in :ref:`install_instructions`
but will need to be activated with ``pre-commit install``.
