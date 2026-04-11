# Release Notes

## Version 0.13.1 - Cache-First Dependency Installation

Release date: 2026-04-11

This release improves project creation reliability by changing dependency installation behavior after virtual environment setup.

## Highlights

### 1. Cache-first install flow for project creation
After the virtual environment is created, the tool now installs framework dependencies from local cache first.

What changed:
- Framework package installation now first runs with cache-only flags.
- If cache installation fails due to missing packages, install automatically falls back to online package download/install.
- Successful online installs are followed by best-effort package caching for future project creation runs.

Why this matters:
- Faster and more reliable project bootstrapping when cache is populated.
- Predictable fallback behavior when cache is incomplete.
- Better offline-friendly setup behavior.

## Documentation updates
- Changelog and release notes updated for this patch release.

## Version updates
Updated to `0.13.1` in:
- `pyproject.toml`
- `setup.py`

## Notes
- Existing projects remain compatible.
- This release changes only project creation dependency installation behavior.

## Quick verification checklist
1. Create a new app with `amen create`.
2. Verify install first attempts cache-based package installation.
3. If cache is incomplete, verify installer falls back to online install.
4. Re-run project creation and verify packages are reused from cache when available.

## Thank you
Thanks to everyone providing project structure and workflow feedback that shaped this release.
