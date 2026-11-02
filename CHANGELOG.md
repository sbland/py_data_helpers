# Changelog

This file records notable changes to the project. The initial entry documents
the recent changes known when this changelog was created; earlier release
history has not been reconstructed.

## Unreleased

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
