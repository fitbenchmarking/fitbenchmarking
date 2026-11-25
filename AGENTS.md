# FitBenchmarking — AI Agent Guidance

This file is read by AI coding assistants (Claude Code, Codex, Cursor, etc.) working
in this repository.  Please follow these rules in addition to any user instructions.

## Project Architecture

FitBenchmarking's pipeline, in order:

1. **Parsing** (`fitbenchmarking/parsing/`): problem files (SIF, Mantid, etc.) are
   read and converted into `FittingProblem` objects.
2. **Cost function** (`fitbenchmarking/cost_func/`): wraps the problem to define the
   scalar objective passed to the minimizer (e.g. NLLS, weighted least-squares).
3. **Controller** (`fitbenchmarking/controllers/`): thin wrapper around a specific
   minimizer library.  Every controller subclasses `base_controller.Controller` and
   must populate `algorithm_check` — a dict keyed by algorithm family (e.g. `"ls"`,
   `"deriv_free"`, `"general"`) listing which minimizers belong to each family.
4. **Results** (`fitbenchmarking/utils/fitbm_result.py`): `FittingResult` stores
   outcome metrics for one problem/minimizer pair.
5. **Output** (`fitbenchmarking/results_processing/`): HTML tables and performance
   profiles are generated from the collected results.

## AI Policy

FitBenchmarking has an [AI-contributions policy](https://fitbenchmarking.readthedocs.io/en/latest/contributors/ai_policy.html).
Key points relevant to agents:

- **Do not open pull requests autonomously.** A human contributor must review all
  AI-generated code and submit the pull request themselves.
- **Do not post to issues, discussions, or forums on behalf of a contributor.**
  Human communication must come from the human.
- **Do not work on issues labelled `good first issue`.** These are reserved for
  new human contributors learning the project.
- Pull requests that used AI assistance must state which tool was used and how.

See the [git workflow guide](https://fitbenchmarking.readthedocs.io/en/latest/contributors/workflow.html)
for the full PR process.

## Core Working Rules

- **Fix root causes.** Fix the underlying mathematical or architectural cause.
  Do not patch individual failing test cases.
- **Preserve coding style.** Match the naming and patterns of the module you are
  editing.  Keep edits minimal and local to the requested change.
- **Avoid duplication.** Reuse or extend nearby logic instead of duplicating it.
  Do not add speculative abstractions or broad refactors unless asked.
- **Do not trust memorised API shapes.** Many minimizer dependencies are optional
  and have changing APIs.  Read the installed source (or the installed package's
  docs) before calling an unfamiliar function — do not rely on training-data memory.
- **Document the present, not the past.** Do not describe a removed or rejected
  approach in a comment or docstring.  Document only what the current code does.

## Coding Style and Conventions

See the [coding standards guide](https://fitbenchmarking.readthedocs.io/en/latest/contributors/guidelines.html)
for the full requirements.  Key points:

- Docstrings use **Sphinx RST style**: `:param name:`, `:type name:`, `:returns:`,
  `:rtype:`.  Update docstrings for any public function you touch.
- The project uses [pre-commit](https://pre-commit.com/) hooks (ruff, flake8, etc.).
  Run `pre-commit run --all-files` before committing.

## Optional Dependencies

Most minimizer controllers depend on packages that are not installed by default.
Before assuming an import is available, check which extra provides it:

```bash
pip install fitbenchmarking[<extra>]   # e.g. scipy, mantid, dfo, minuit, ...
pip install fitbenchmarking[all]       # everything
```

## Testing

```bash
python -m pytest fitbenchmarking/
```

Add a test for every new feature or bug fix in the existing test file for that
module.  When behaviour changes, update the affected tests.  Write the narrowest
test that proves the change.

## Documentation

User-facing docs live under `docs/source/` and are built with Sphinx.  API docs are
auto-generated from docstrings.  When adding new public functions or modules, add a
corresponding entry in the appropriate `.rst` file.
