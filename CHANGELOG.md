# Changelog

All notable changes to this project will be documented in this file.

## [0.13.0] - 2026-04-10

### Added
- New `add` CLI command to scaffold project parts in existing apps:
  - `am add endpoint <name>` creates a new endpoint module.
  - `am add util <name>` creates a utility module in `utils/`.
  - `am add view <name>` creates an endpoint plus an HTML template for server-rendered pages.
- Framework-aware endpoint scaffolding for both Flask and FastAPI.

### Changed
- `run` command now executes `app.py` instead of `run.py`.
- Flask SQLite scaffolding now uses the Flask instance folder for the database file.
- Scaffolded endpoints are now split into multiple modules instead of a single `endpoints.py` file.
- Default generated index page has been redesigned with a modern landing-page style inspired by current starter pages.
- Documentation updated to reflect new app runner and endpoint module structure.

### Fixed
- Corrected Flask SQLite database URI generation so `sqlite3` selection no longer produces a MySQL URI.

### Versioning
- Bumped package version from `0.12.0` to `0.13.0` in project metadata.
