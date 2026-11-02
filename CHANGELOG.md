# Changelog

This file records notable changes to the project. The initial entry documents
the recent changes known when this changelog was created; earlier release
history has not been reconstructed.

## Unreleased

- Date: 2026-11-02
- Summary: Resolve Ruff lint errors and formatting differences.
- Credits: Copilot
- Added:
  - Added regression coverage for invalid input error types in `dict_to_cls`.
- Changed:
  - Use `TypeError` for unsupported field types and non-dictionary input, and `ValueError` for unknown strict-mode keys.
  - Simplified wildcard traversal and corrected JSON decoder argument ordering.
- Fixed:
  - Corrected the optional type expression and exception handling for optional widget imports.
- Docs:
  - Recorded the lint cleanup and its validation in the changelog.
- Tests:
  - Full suite: 160 passed, 1 skipped.
- Lint/Format:
  - Ruff lint and formatting checks passed.

- Date: 2026-11-02
- Summary: Record recent dependency and documentation changes.
- Credits: Copilot
- Added:
  - Added `certifi` as a direct runtime dependency in response to a security issue.
  - Created this changelog to document project changes going forward.
- Changed:
  - None.
- Fixed:
  - None.
- Docs:
  - Added the initial changelog.
- Tests:
  - Full suite: 156 passed, 3 failed, and 1 skipped; failures concern dataclass reflection under Python 3.14.
- Lint/Format:
  - Ruff reported existing lint issues and formatting differences in Python source files; no source files changed.

- Date: 2026-11-02
- Summary: Fix dataclass reflection tests and type checking on Python 3.14.
- Credits: Copilot
- Added:
  - None.
- Changed:
  - Updated class comparison tests to use Python's annotation inspection API and ignore interpreter-specific class attributes.
- Fixed:
  - Updated `check_types` to inspect annotations from the instance's class, supporting Python 3.14's deferred class annotations.
- Docs:
  - Recorded the compatibility fix and validation status in this changelog.
- Tests:
  - Python 3.14 full suite: 159 passed, 1 skipped.
  - Python 3.12 tests were not run because `pytest` and `numpy` are unavailable in that interpreter environment.
- Lint/Format:
  - Skipped as requested.
