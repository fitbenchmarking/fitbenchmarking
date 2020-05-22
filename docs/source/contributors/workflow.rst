.. _workflow:

############
Git Workflow
############


======
Issues
======

All new work should start with a
`new GitHub issue <https://github.com/fitbenchmarking/fitbenchmarking/issues/new/choose>`_
being filed.
This should clearly explain what the change to the code will do.
There are templates for *Bug report*, *Documentation*,
*Feature request* and *Test* issues on GitHub, and you can also
open a blank issue if none of these work.

If issues help meet a piece of work agreed with our funders, it
is linked to the appropriate `Milestone <https://github.com/fitbenchmarking/fitbenchmarking/milestones>`_ in GitHub.

===============
Adding new code
===============

The first step in adding new code is to create a branch, where the work
will be done. Branches should be named according to the convention
"<nnn>-description", where <nnn> is the issue number.

Please ensure everything required in :ref:`guidelines` is included in
the branch.

When you think your new code is ready to be merged into the codebase,
you should open a pull request.  The description should contain the
words "Fixes #<nnn>", where <nnn> is the issue number; this will ensure
the issue is closed when the code is merged into master.  At this point
the automated tests will trigger, and you can see if the code passes on
an independent system.

Sometimes it is desirable to open a pull request when the code is not
quite ready to be merged.  This is a good idea, for example, if you want
to get an early opinion on a coding descision.  If this is the case, you
should mark the pull request as a *draft* on GitHub.

Once the work is ready to be reviewed, you may want to assign a reviewer,
if you think someone would be well suited to review this change.  It is worth
messaging them on, for example, Slack, as well as requesting their review on
GitHub.

================
Release branches
================

Most work should be branched off, and merged into, master.

The exception is when we are near a release, and then the contributor
must make the decision of whether the code will enter this release, or
wait for a future one.

Branches named `release-*` are protected branches; code must be approved by
a reviewer before being added to them, and automated tests will be run on
pull requests to these branches.  If code is to be included in the release, it
must be pulled into this branch and not master.

Release branches should have the format `release-major.minor.x`, starting from
`release-0.1.x`.  When the code is released, we will tag that commit with
`release-0.1.0`.  Any hotfixes will increment `x` by one, and a new tag will
be created accordingly.  If at some point we don't want to provide hot-fixes
to a given minor release, then the corresponding release branch may be deleted.

When a pull request is merged into a release branch, then the change should also
be merged into master as soon a possible.  As long as the tests pass, and there
are no merge conflicts, this can be done without a detailed review.
