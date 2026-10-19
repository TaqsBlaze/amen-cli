# Release Notes

## Version 0.14.0 — Interactive welcome and dependable project workflows

Release date: 2026-10-19

AMEN 0.14.0 gives newly generated webapps an interactive welcome page and brings
all recent database, scaffolding, authentication, and command-handling repairs
into one minor release.

### A new welcome experience

Flask and FastAPI webapps receive a Laravel-inspired light/dark interface with
project, framework, database, and version details. The AMEN version is prominent
beside the logo. A searchable reference lists all CLI commands with descriptions
and copy buttons; the illustration is removed. The health control queries the
application's real `/health` endpoint and exposes its response in a JSON inspector. Styles, scripts, and the bundled
Instrument Sans font are served locally, alongside the font's SIL Open Font
License, so the interface does not depend on a runtime CDN.

API-only projects retain their JSON welcome response.

### Database and rendering repairs

- Database-free projects omit database setup and dependencies.
- Flask registers models for Flask-Migrate. FastAPI receives SQLAlchemy sessions,
  shared model metadata, and an Alembic migration environment.
- Both frameworks honor external/project `.env` `DATABASE_URL` configuration,
  resolve relative SQLite paths from the project root, and calculate creation
  timestamps for each inserted record. MySQL uses PyMySQL.
- Installation and generated requirements use the selected database packages.
  `amen migrate` selects Flask-Migrate or Alembic and reports failed migrations.
- Initial and added FastAPI views use compatible template response arguments.

### Safer scaffolding and clearer failures

- `amen add` rejects existing endpoint, utility, and template paths, including
  symlinks. Partial output is removed after failed writes or registration, and
  registration files are replaced atomically.
- CLI failures return nonzero statuses and include useful diagnostics. Failed
  application, test, installation, and migration subprocesses preserve their
  exit codes; server commands run without a shell.
- Web creation validates requests, reports target conflicts without terminal
  prompts, and returns the actual normalized name/path only after success.
- Malformed, invalid, and expired Flask bearer credentials return 401. Valid
  credentials accept a case-insensitive Bearer scheme; unrelated application
  failures remain visible as errors.
- Audit handling preserves report output, distinguishes findings from tool
  failures, normalizes severity aliases, and excludes project environments.
  Monitor inputs are validated and web-monitor startup failures reach the CLI.

### Compatibility and validation

Existing generated applications are not rewritten. Regenerate or manually adopt
selected template changes when updating an older application. Legacy FastAPI
projects need an Alembic configuration before using the repaired migration flow.

Automation must account for the new failure statuses: commands that previously
printed an error and exited successfully now fail. Signal termination maps to
`128 + signal`; clean audits exit 0 and audits with findings exit 1.

Regression coverage includes generated Flask/FastAPI routes and welcome assets,
SQLite persistence and migrations, database-free imports, collision protection,
command failures, authentication, and web-creation response contracts. Live MySQL
and native macOS/Windows verification remain pending.

Both `pyproject.toml` and `setup.py` declare `0.14.0`. Publishing the GitHub
release triggers the repository’s existing build and PyPI publication workflow.
The PyPI stage uses the configured `pypi` environment and publishing credential.

---

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
