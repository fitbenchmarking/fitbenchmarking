######################
Contributor Guidelines
######################

Linting
^^^^^^^

All pull requests should be pep8 compliant.
We suggest running code through flake8 and pylint before submitting to check for this.



Documentation
^^^^^^^^^^^^^

Any new code will be accepted only if there is relevent documentation for it in the corresponding pull request.


Git
^^^

Branches should be created from master, and by convention follow the pattern "nnn_description" where nnn is the issue number.


Testing
^^^^^^^

All tests should pass before submitting code.
Tests are written using unittests and the suggestion is to run it with pytest.

Function: Does the change do what it's supposed to?
Tests: Does it pass? Is there adequate coverage for new code?
Style: Is the coding style consistent? Is anything overly confusing?
Documentation: Is there a suitable change to documentation for this change?
