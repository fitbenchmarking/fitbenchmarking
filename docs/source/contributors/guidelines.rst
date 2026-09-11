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

========
Spelling
========

FitBenchmarking consistently uses the American spelling ``minimizer``, both in
code and in documentation. A pre-commit hook,
``.custom_hooks/minimizer_spelling.py``, checks every ``.py``, ``.md``,
``.html`` and ``.rst`` file and reports any line containing a discouraged
alternative.

Where such a word cannot be avoided, add ``# ignore: spelling`` to the end of
the line and the check will skip it. The discouraged words are listed below,
each shown with the marker applied::

    minimiser  # ignore: spelling
    solver     # ignore: spelling

If a name comes from a third party API or is part of the public
FitBenchmarking interface, and so appears in many places, add it to
``ALLOWED_NAMES`` in the hook instead. This exempts that name wherever it
occurs, rather than exempting whole lines one at a time.

==========
Pre-commit
==========

Pre-commit runs checks at the point of committing code to ensure simple
problems are spotted before running the CI.
This covers sorting imports, fixing indentation, removing trailing whitespace,
checking the linting, and checking the spelling conventions described above.

Pre-commit will be installed as part of Step 4 in :ref:`install_instructions`
but will need to be activated with ``pre-commit install``.

Note that the spelling check runs locally only. It is skipped on pre-commit.ci,
so activating pre-commit is the only way it will be applied to your changes.
